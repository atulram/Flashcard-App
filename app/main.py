from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Load environment variables
load_dotenv()

from app.routers import flashcards

# Configure logging
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Flashcard Generator",
    description="Generate flashcards from PDF documents using Gemini AI",
    version="1.0.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(flashcards.router)

# Global storage for flashcard sessions (in production, use Redis or database)
app.state.sessions = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with PDF upload form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("Flashcard Generator API starting up...")
    
    # Verify Gemini API key is set
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY not set in environment variables")
    
    # Create uploads directory if it doesn't exist
    Path("uploads").mkdir(exist_ok=True)
    
    logger.info("Flashcard Generator API ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Flashcard Generator API shutting down...")
    
    # Clear sessions
    app.state.sessions.clear()
    
    logger.info("Shutdown complete!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)