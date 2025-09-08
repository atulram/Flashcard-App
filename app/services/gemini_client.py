import asyncio
from xmlrpc import client
from google import genai
from google.genai import types
import json
import os
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    """Service for interacting with Google Gemini API to generate flashcards"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        self.client = genai.Client(api_key=self.api_key)

        self.model_name = "gemini-2.5-flash"
        
        # Generation config for consistent output
        self.generation_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=16384,
        )
    
    def generate_content(self, prompt):
        """Generate content with a timeout"""
        logger.info("Starting LLM generation...")
        logger.debug(f"Prompt: {prompt[:500]}...")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            return response
        except Exception as e:
            logger.error(f"Error in LLM generation: {e}")
            raise

    async def generate_flashcards(self, text_content: str, num_cards: int = None) -> List[Dict[str, str]]:
        """Generate flashcards from text content using Gemini"""
        
        try:
            # Estimate appropriate number of cards based on content length
            if num_cards is None:
                num_cards = self._estimate_card_count(text_content)
            
            # Create the prompt
            prompt = self._create_flashcard_prompt(text_content, num_cards)
            
            logger.info(f"Generating {num_cards} flashcards using Gemini API")
            
            # Generate content
            response = self.generate_content(prompt)
            
            # Parse the response
            flashcards = self._parse_flashcard_response(response.text) # type: ignore
            
            logger.info(f"Successfully generated {len(flashcards)} flashcards")
            return flashcards
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            raise
    
    def _estimate_card_count(self, text_content: str) -> int:
        """Estimate appropriate number of flashcards based on content length"""
        word_count = len(text_content.split())
        
        if word_count < 200:
            return 3
        elif word_count < 500:
            return 5
        elif word_count < 1000:
            return 8
        elif word_count < 2000:
            return 12
        else:
            return 15
    
    def _create_flashcard_prompt(self, text_content: str, num_cards: int) -> str:
        """Create a structured prompt for flashcard generation"""
        
        prompt = f"""
You are an expert educational content creator. Please analyze the following text and create exactly {num_cards} high-quality flashcards for studying.

Requirements:
1. Create exactly {num_cards} flashcards
2. Focus on the most important concepts, definitions, facts, and key points
3. Questions should be clear and specific
4. Answers should be concise but complete
5. Avoid overly obvious or trivial questions
6. Include a mix of question types: definitions, explanations, examples, applications
7. Ensure questions test understanding, not just memorization

Output format: Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "Clear, specific question here",
    "answer": "Concise but complete answer here"
  }},
  {{
    "question": "Another question here",
    "answer": "Another answer here"
  }}
]

Content to analyze:
{text_content}

Generate exactly {num_cards} flashcards in the JSON format specified above:"""

        return prompt
    
    def _parse_flashcard_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse the Gemini response and extract flashcards"""
        
        try:
            # Clean the response text
            cleaned_text = self._clean_response_text(response_text)
            
            # Try to parse as JSON
            flashcards = json.loads(cleaned_text)
            
            # Validate the structure
            if not isinstance(flashcards, list):
                raise ValueError("Response is not a list")
            
            validated_cards = []
            for card in flashcards:
                if not isinstance(card, dict):
                    continue
                
                if "question" not in card or "answer" not in card:
                    continue
                
                question = str(card["question"]).strip()
                answer = str(card["answer"]).strip()
                
                if not question or not answer:
                    continue
                
                if len(question) < 10 or len(answer) < 5:
                    continue
                
                validated_cards.append({
                    "question": question,
                    "answer": answer
                })
            
            if not validated_cards:
                raise ValueError("No valid flashcards found in response")
            
            return validated_cards
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            # Try to extract flashcards using regex as fallback
            return self._extract_flashcards_fallback(response_text)
        
        except Exception as e:
            logger.error(f"Error parsing flashcard response: {str(e)}")
            raise
    
    def _clean_response_text(self, text: str) -> str:
        """Clean the response text to extract JSON"""
        
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON array bounds
        start_idx = text.find('[')
        end_idx = text.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1]
        
        return text.strip()
    
    def _extract_flashcards_fallback(self, text: str) -> List[Dict[str, str]]:
        """Fallback method to extract flashcards using regex"""
        
        flashcards = []
        
        # Try to find question-answer pairs in various formats
        patterns = [
            r'["\']question["\']\s*:\s*["\']([^"\']+)["\'],?\s*["\']answer["\']\s*:\s*["\']([^"\']+)["\']',
            r'Q:\s*([^\n]+)\s*A:\s*([^\n]+)',
            r'Question:\s*([^\n]+)\s*Answer:\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match) == 2:
                    question = match[0].strip()
                    answer = match[1].strip()
                    
                    if len(question) > 10 and len(answer) > 5:
                        flashcards.append({
                            "question": question,
                            "answer": answer
                        })
        
        if not flashcards:
            # Create a fallback flashcard
            flashcards = [{
                "question": "What was the main topic of the uploaded document?",
                "answer": "Please review the document content to understand the main concepts and topics covered."
            }]
        
        return flashcards[:15]  # Limit to 15 cards max
    
    def test_connection(self) -> bool:
        """Test the Gemini API connection"""
        try:
            response = self.generate_content("Test connection")
            return True
        except Exception as e:
            logger.error(f"Gemini API test failed: {str(e)}")
            return False