import fitz  # PyMuPDF
import io
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Service for processing PDF files and extracting text"""
    
    def __init__(self):
        self.max_pages = 5
    
    def extract_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            # Check page count
            if len(pdf_document) > self.max_pages:
                pdf_document.close()
                raise ValueError(f"PDF has {len(pdf_document)} pages, maximum allowed is {self.max_pages}")
            
            text_content = ""
            
            # Extract text from each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                page_text = page.get_text()
                
                # Clean and format the text
                cleaned_text = self._clean_text(page_text)
                if cleaned_text:
                    text_content += f"\n\n--- Page {page_num + 1} ---\n\n{cleaned_text}"
            
            pdf_document.close()
            
            # Final cleanup
            text_content = self._final_cleanup(text_content)
            
            logger.info(f"Successfully extracted {len(text_content)} characters from PDF")
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def get_page_count(self, pdf_content: bytes) -> int:
        """Get the number of pages in the PDF"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            page_count = len(pdf_document)
            pdf_document.close()
            return page_count
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (simple heuristic)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip very short lines that might be page numbers or artifacts
            if len(line) < 3:
                continue
                
            # Skip lines that are just numbers (likely page numbers)
            if line.isdigit():
                continue
                
            # Skip lines with only special characters
            if re.match(r'^[^\w\s]*$', line):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _final_cleanup(self, text: str) -> str:
        """Final text cleanup and formatting"""
        if not text:
            return ""
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Ensure proper sentence spacing
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def validate_pdf(self, pdf_content: bytes) -> dict:
        """Validate PDF and return metadata"""
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            metadata = {
                "page_count": len(pdf_document),
                "is_valid": True,
                "has_text": False,
                "file_size": len(pdf_content)
            }
            
            # Check if PDF has extractable text
            sample_text = ""
            pages_checked = min(2, len(pdf_document))  # Check first 2 pages
            
            for page_num in range(pages_checked):
                page = pdf_document[page_num]
                page_text = page.get_text()
                sample_text += page_text
                
                if len(sample_text) > 100:  # Found sufficient text
                    metadata["has_text"] = True
                    break
            
            pdf_document.close()
            
            return metadata
            
        except Exception as e:
            logger.error(f"PDF validation error: {str(e)}")
            return {
                "page_count": 0,
                "is_valid": False,
                "has_text": False,
                "file_size": len(pdf_content),
                "error": str(e)
            }