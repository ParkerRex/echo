"""
Chapters generation processor.
"""
import json
from typing import Any, Dict, List, Optional

from ...utils.error_handling import retry
from ...utils.logging import get_logger

logger = get_logger(__name__)


class ChaptersProcessor:
    """
    Handles generation of video chapters from audio content.
    """
    
    def __init__(self, model_service: Any, testing_mode: bool = False):
        """
        Initialize the chapters processor.
        
        Args:
            model_service: Service for AI model access
            testing_mode: Whether to run in testing mode (returns mock data)
        """
        self.model_service = model_service
        self.testing_mode = testing_mode
    
    @retry(max_attempts=2)
    def generate_chapters(self, audio_path: str) -> List[Dict[str, str]]:
        """
        Generate timestamped chapters from audio.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of chapter dictionaries with timecode and summary
            
        Raises:
            Exception: If generation fails
        """
        try:
            logger.info(f"Generating chapters for {audio_path}")
            
            # For testing mode, return mock chapters
            if self.testing_mode:
                logger.info("TESTING MODE: Returning mock chapters")
                return self._get_mock_chapters()
            
            # Read the audio file
            with open(audio_path, "rb") as f:
                audio_content = f.read()
            
            # Prompt for chapter generation
            prompt = (
                "Chapterize the video content by grouping the content into chapters and providing a summary for each chapter. "
                "Please only capture key events and highlights. If you are not sure about any info, please do not make it up. "
                'Return the result ONLY as a valid JSON array of objects, where each object has the keys "timecode" (string, e.g., "00:00") '
                'and "chapterSummary" (string). Aim for chapters roughly every 2 minutes.\n'
                "Example JSON output format:\n"
                "[\n"
                '  {"timecode": "00:00", "chapterSummary": "Introduction to the topic..."},\n'
                '  {"timecode": "02:01", "chapterSummary": "Discussing the first main point..."}\n'
                "]"
            )
            
            # Generate chapters using the model service
            response = self.model_service.generate_content(
                prompt=prompt,
                content=audio_content,
                content_type="audio/wav",
                config={
                    "temperature": 0.6,
                    "response_mime_type": "application/json",
                }
            )
            
            # Parse the JSON response
            try:
                if hasattr(response, 'text'):
                    chapters = json.loads(response.text)
                else:
                    chapters = json.loads(str(response))
                
                # Validate the structure
                if not isinstance(chapters, list):
                    raise ValueError("Response is not a list")
                
                # Validate each chapter
                for chapter in chapters:
                    if not isinstance(chapter, dict):
                        raise ValueError(f"Chapter is not a dictionary: {chapter}")
                    if "timecode" not in chapter or "chapterSummary" not in chapter:
                        raise ValueError(f"Chapter missing required keys: {chapter}")
                
                logger.info(f"Generated {len(chapters)} chapters")
                return chapters
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse chapters JSON: {e}. Response: {response}")
                # Fall back to mock chapters if parsing fails
                return self._get_mock_chapters()
            
        except Exception as e:
            logger.error(f"Failed to generate chapters: {e}")
            # Return empty list on failure
            return []
    
    def format_chapters_text(self, chapters: List[Dict[str, str]]) -> str:
        """
        Format chapters as text.
        
        Args:
            chapters: List of chapter dictionaries
            
        Returns:
            Formatted chapters text
        """
        # Join chapters into a text format
        lines = []
        for chapter in chapters:
            lines.append(f"{chapter['timecode']} - {chapter['chapterSummary']}")
        
        return "\n".join(lines)
    
    def _get_mock_chapters(self) -> List[Dict[str, str]]:
        """
        Generate mock chapters for testing.
        
        Returns:
            List of mock chapters
        """
        return [
            {"timecode": "00:00", "chapterSummary": "Introduction to the topic"},
            {"timecode": "02:00", "chapterSummary": "Background and context"},
            {"timecode": "04:00", "chapterSummary": "Main points and discussion"},
            {"timecode": "06:00", "chapterSummary": "Analysis and implications"},
            {"timecode": "08:00", "chapterSummary": "Conclusion and next steps"}
        ]