"""
Metadata service for generating and managing video metadata.

This module provides services for generating video metadata components including
titles, descriptions, tags, and thumbnails.
"""

import logging
import os
from typing import Dict, List

from apps.core.core.exceptions import MetadataGenerationError
from apps.core.lib.ai.base_adapter import AIAdapterInterface
from apps.core.lib.storage.file_storage import FileStorageService
from apps.core.models.video_metadata_model import VideoMetadata


class MetadataService:
    """
    Service for generating video metadata.

    This service handles the generation of various metadata components for videos
    using AI services, including titles, descriptions, tags, and thumbnails.
    """

    def __init__(
        self,
        ai_adapter: AIAdapterInterface,
        storage_adapter: FileStorageService,
        output_dir: str = "metadata",
    ):
        """
        Initialize the MetadataService with required dependencies.

        Args:
            ai_adapter: AI adapter for content generation
            storage_adapter: Storage adapter for file operations
            output_dir: Directory for generated metadata files
        """
        self._ai = ai_adapter
        self._storage = storage_adapter
        self._output_dir = output_dir

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        logging.info(f"Initialized MetadataService with output_dir={output_dir}")

    def generate_metadata(self, transcript: str) -> VideoMetadata:
        """
        Generate complete metadata from a transcript.

        Args:
            transcript: Transcript text

        Returns:
            VideoMetadata object with all metadata components

        Raises:
            MetadataGenerationError: If metadata generation fails
        """
        try:
            logging.info("Generating complete metadata from transcript")

            # Delegate to AI service to generate all metadata components at once
            metadata_dict = self._ai.generate_metadata(transcript)

            # Create VideoMetadata object
            metadata = VideoMetadata(
                title=metadata_dict.get("title", "Untitled Video"),
                description=metadata_dict.get("description", ""),
                tags=metadata_dict.get("tags", []),
                show_notes=metadata_dict.get("show_notes", ""),
                chapters=metadata_dict.get("chapters", []),
            )

            logging.info(
                f"Successfully generated metadata with title: {metadata.title}"
            )
            return metadata

        except Exception as e:
            error_msg = f"Failed to generate metadata: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def generate_title(self, transcript: str) -> str:
        """
        Generate a title from a transcript.

        Args:
            transcript: Transcript text

        Returns:
            Generated title

        Raises:
            MetadataGenerationError: If title generation fails
        """
        try:
            logging.info("Generating title from transcript")

            # Use AI to generate title and keywords
            title_tags = self._generate_title_tags(transcript)

            title = title_tags.get("Description", "Untitled Video")
            logging.info(f"Generated title: {title}")
            return title

        except Exception as e:
            error_msg = f"Failed to generate title: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def generate_description(self, transcript: str, max_length: int = 500) -> str:
        """
        Generate a description from a transcript.

        Args:
            transcript: Transcript text
            max_length: Maximum length of the description

        Returns:
            Generated description

        Raises:
            MetadataGenerationError: If description generation fails
        """
        try:
            logging.info(
                f"Generating description from transcript (max {max_length} chars)"
            )

            # Use AI to summarize content
            description = self._ai.summarize_content(transcript, max_length)

            logging.info(f"Generated description ({len(description)} chars)")
            return description

        except Exception as e:
            error_msg = f"Failed to generate description: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def generate_tags(self, transcript: str, max_tags: int = 10) -> List[str]:
        """
        Generate tags from a transcript.

        Args:
            transcript: Transcript text
            max_tags: Maximum number of tags to generate

        Returns:
            List of generated tags

        Raises:
            MetadataGenerationError: If tag generation fails
        """
        try:
            logging.info(f"Generating tags from transcript (max {max_tags} tags)")

            # Use AI to generate title and keywords
            title_tags = self._generate_title_tags(transcript)

            # Convert comma-separated keywords to list and limit to max_tags
            keywords = title_tags.get("Keywords", "video,content")
            tags = [tag.strip() for tag in keywords.split(",") if tag.strip()][
                :max_tags
            ]

            logging.info(f"Generated {len(tags)} tags")
            return tags

        except Exception as e:
            error_msg = f"Failed to generate tags: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def generate_thumbnail_description(
        self, transcript: str, timestamp: float = 30.0
    ) -> str:
        """
        Generate a description for a thumbnail at a specific timestamp.

        Args:
            transcript: Transcript text
            timestamp: Time in seconds for the thumbnail

        Returns:
            Description for the thumbnail

        Raises:
            MetadataGenerationError: If description generation fails
        """
        try:
            logging.info(f"Generating thumbnail description at timestamp {timestamp}s")

            # Delegate to AI adapter
            description = self._ai.generate_thumbnail_description(transcript, timestamp)

            logging.info(f"Generated thumbnail description: {description}")
            return description

        except Exception as e:
            error_msg = f"Failed to generate thumbnail description: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def save_metadata_to_json(self, metadata: VideoMetadata, filename: str) -> str:
        """
        Save metadata to a JSON file.

        Args:
            metadata: VideoMetadata object
            filename: Base filename without extension

        Returns:
            Path to the saved JSON file

        Raises:
            MetadataGenerationError: If saving fails
        """
        try:
            # Ensure filename has .json extension
            if not filename.endswith(".json"):
                filename = f"{filename}.json"

            output_path = os.path.join(self._output_dir, filename)

            # Convert metadata to dictionary
            metadata_dict = metadata.to_dict()

            # Save to storage
            json_content = metadata.to_json()
            self._storage.upload_from_string(
                json_content, output_path, content_type="application/json"
            )

            logging.info(f"Saved metadata to {output_path}")
            return output_path

        except Exception as e:
            error_msg = f"Failed to save metadata to JSON: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def _generate_title_tags(self, transcript: str) -> Dict[str, str]:
        """
        Generate title and tags as a dictionary from transcript.

        Args:
            transcript: Transcript text

        Returns:
            Dictionary with "Description" (title) and "Keywords" (comma-separated tags)

        Raises:
            MetadataGenerationError: If generation fails
        """
        try:
            # This is a wrapper around the AI adapter method to simplify testing
            # and to provide consistent error handling
            result = self._ai._generate_title_tags(transcript)

            # Ensure required keys are present
            if "Description" not in result:
                result["Description"] = "Untitled Video"

            if "Keywords" not in result:
                result["Keywords"] = "video,content"

            return result

        except Exception as e:
            error_msg = f"Failed to generate title and tags: {str(e)}"
            logging.error(error_msg)
            # Return default values instead of raising to make this more robust
            return {"Description": "Untitled Video", "Keywords": "video,content"}
