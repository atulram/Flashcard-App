from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid
import os
import logging
from typing import Dict, Any

from app.services.pdf_processor import PDFProcessor
from app.services.gemini_client import GeminiClient

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

# Initialize services
pdf_processor = PDFProcessor()
gemini_client = GeminiClient()

@router.post("/upload")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """Process uploaded PDF and generate flashcards"""
    
    try:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check file size (10MB limit)
        max_size = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds {max_size // (1024*1024)}MB limit"
            )
        
        logger.info(f"Processing file: {file.filename}")
        
        # Extract text from PDF
        try:
            text_content = pdf_processor.extract_text(file_content)
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to process PDF. Please ensure it's a text-based PDF.")
        
        # Validate page count (max 5 pages)
        page_count = pdf_processor.get_page_count(file_content)
        if page_count > 5:
            raise HTTPException(
                status_code=400, 
                detail=f"PDF has {page_count} pages. Maximum allowed is 5 pages."
            )
        
        # Check if text was extracted
        if not text_content or len(text_content.strip()) < 100:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract sufficient text from PDF. Please ensure it contains readable text."
            )
        
        logger.info(f"Extracted {len(text_content)} characters from {page_count} pages")
        
        # Generate flashcards using Gemini
        try:
            flashcards = await gemini_client.generate_flashcards(text_content)
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate flashcards. Please try again.")
        
        if not flashcards:
            raise HTTPException(status_code=400, detail="No flashcards could be generated from this content.")
        
        # Create session and store flashcards
        session_id = str(uuid.uuid4())
        request.app.state.sessions[session_id] = {
            "flashcards": flashcards,
            "filename": file.filename,
            "total_cards": len(flashcards)
        }
        
        logger.info(f"Generated {len(flashcards)} flashcards for session {session_id}")
        
        # Redirect to study page
        return RedirectResponse(url=f"/study/{session_id}", status_code=303)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")

@router.get("/study/{session_id}", response_class=HTMLResponse)
async def study_flashcards(request: Request, session_id: str):
    """Display flashcards for studying"""
    
    # Get session data
    sessions = request.app.state.sessions
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Study session not found or expired")
    
    session_data = sessions[session_id]
    
    return templates.TemplateResponse("study.html", {
        "request": request,
        "session_id": session_id,
        "flashcards": session_data["flashcards"],
        "filename": session_data["filename"],
        "total_cards": session_data["total_cards"]
    })

@router.get("/api/session/{session_id}")
async def get_session_data(request: Request, session_id: str):
    """API endpoint to get session flashcards as JSON"""
    
    sessions = request.app.state.sessions
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]

@router.delete("/api/session/{session_id}")
async def delete_session(request: Request, session_id: str):
    """Delete a study session"""
    
    sessions = request.app.state.sessions
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Session not found")