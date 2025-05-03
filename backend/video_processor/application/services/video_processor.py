"""
Video processor service for orchestrating the video processing pipeline.

This module provides the main service for coordinating the video processing workflow,
from initial upload to completed processing and publishing.
"""

import logging
from typing import Optional

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.domain.exceptions import (
    InvalidVideoError,
    MetadataGenerationError,
    ProcessingError,
)
from video_processor.domain.models.job import JobStatus, VideoJob


class VideoProcessorService:
    """
    Service for coordinating the video processing workflow.

    This service orchestrates the entire video processing pipeline, including:
    - Video validation and preparation
    - Audio extraction
    - Transcript generation
    - Metadata generation
    - Subtitle creation
    - Thumbnail generation
    - Output file management
    """

    def __init__(
        self,
        storage_adapter: StorageInterface,
        ai_adapter: AIServiceInterface,
        output_bucket: Optional[str] = None,
        local_output_dir: Optional[str] = None,
    ):
        """
        Initialize the VideoProcessorService with required dependencies.

        Args:
            storage_adapter: Storage adapter for file operations
            ai_adapter: AI adapter for content generation
            output_bucket: GCS bucket for output files (optional)
            local_output_dir: Local directory for output files (optional, for testing)
        """
        self._storage = storage_adapter
        self._ai = ai_adapter
        self._output_bucket = output_bucket
        self._local_output_dir = local_output_dir or "output"

        logging.info(
            f"Initialized VideoProcessorService with output_bucket={output_bucket}, "
            f"local_output_dir={local_output_dir}"
        )

    def process_video(self, job: VideoJob) -> VideoJob:
        """
        Process a video based on the provided job.

        This is the main entry point for the video processing workflow.
        It coordinates all the steps required to process a video and generate metadata.

        Args:
            job: VideoJob object containing video and processing details

        Returns:
            Updated VideoJob with processing results

        Raises:
            VideoProcessingError: If any step in the processing pipeline fails
        """
        try:
            logging.info(f"Starting video processing for job {job.id}")

            # Update job status
            job.status = JobStatus.PROCESSING
            job.update_stage("started")

            # TODO: Implement the full processing workflow
            # This will be expanded in the next implementation task

            # For now, return the job with updated status
            job.status = JobStatus.COMPLETED
            job.update_stage("completed")

            logging.info(f"Completed video processing for job {job.id}")
            return job

        except InvalidVideoError as e:
            job.status = JobStatus.FAILED
            job.error = f"Invalid video: {str(e)}"
            logging.error(f"Invalid video in job {job.id}: {str(e)}")
            raise

        except MetadataGenerationError as e:
            job.status = JobStatus.FAILED
            job.error = f"Metadata generation failed: {str(e)}"
            logging.error(f"Metadata generation failed for job {job.id}: {str(e)}")
            raise

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = f"Processing error: {str(e)}"
            logging.error(f"Unexpected error in job {job.id}: {str(e)}")
            raise ProcessingError(f"Video processing failed: {str(e)}") from e
