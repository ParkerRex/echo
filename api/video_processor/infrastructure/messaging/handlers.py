"""
Event handlers for processing messages in the video processor.
"""

import logging
from typing import Any, Dict

from video_processor.application.services.video_processor import VideoProcessorService
from video_processor.domain.exceptions import VideoProcessingError
from video_processor.domain.models.enums import ProcessingStatus
from video_processor.infrastructure.repositories.job_repository import JobRepository

# Configure logger
logger = logging.getLogger(__name__)


def handle_video_uploaded(
    message: Dict[str, Any],
    video_processor: VideoProcessorService,
    job_repository: JobRepository,
) -> None:
    """
    Handle a message indicating a video has been uploaded.

    Args:
        message: Message data containing video information
        video_processor: Instance of VideoProcessorService
        job_repository: Instance of JobRepository

    Raises:
        VideoProcessingError: If processing fails
    """
    try:
        logger.info(
            f"Handling video uploaded event: {message.get('file_name', 'unknown')}"
        )

        # Extract required information from message
        bucket_name = message.get("bucket_name")
        file_name = message.get("file_name")

        if not bucket_name or not file_name:
            raise ValueError(
                "Missing required fields in message: bucket_name, file_name"
            )

        # Create a job for the video
        job_id = job_repository.create(
            video_path=f"gs://{bucket_name}/{file_name}",
            status=ProcessingStatus.PENDING,
        )

        # Start processing asynchronously
        # Note: In a real system, this might be a background task or separate process
        video_processor.process_video(job_id)

        logger.info(f"Started processing job {job_id} for video {file_name}")
    except Exception as e:
        logger.error(f"Error handling video upload event: {str(e)}", exc_info=True)
        raise VideoProcessingError(
            f"Failed to process video upload event: {str(e)}"
        ) from e


def handle_processing_complete(
    message: Dict[str, Any],
    job_repository: JobRepository,
) -> None:
    """
    Handle a message indicating video processing has completed.

    Args:
        message: Message data containing job information
        job_repository: Instance of JobRepository

    Raises:
        VideoProcessingError: If handling fails
    """
    try:
        job_id = message.get("job_id")
        status = message.get("status")

        if not job_id:
            raise ValueError("Missing required field in message: job_id")

        logger.info(f"Handling processing complete event for job {job_id}")

        # Update job status
        if status == "success":
            job_repository.update_status(job_id, ProcessingStatus.COMPLETED)
        elif status == "failure":
            error_message = message.get("error", "Unknown error")
            job_repository.update_status(
                job_id, ProcessingStatus.FAILED, error=error_message
            )
        else:
            logger.warning(f"Unknown status in processing complete event: {status}")

        logger.info(f"Updated job {job_id} status to {status}")
    except Exception as e:
        logger.error(
            f"Error handling processing complete event: {str(e)}", exc_info=True
        )
        raise VideoProcessingError(
            f"Failed to process completion event: {str(e)}"
        ) from e


def handle_publishing_complete(
    message: Dict[str, Any],
    job_repository: JobRepository,
) -> None:
    """
    Handle a message indicating video publishing has completed.

    Args:
        message: Message data containing publishing information
        job_repository: Instance of JobRepository

    Raises:
        VideoProcessingError: If handling fails
    """
    try:
        job_id = message.get("job_id")
        platform = message.get("platform", "unknown")
        platform_id = message.get("platform_id")
        status = message.get("status")

        if not job_id or not status:
            raise ValueError("Missing required fields in message: job_id, status")

        logger.info(
            f"Handling publishing complete event for job {job_id} on {platform}"
        )

        # Get the job
        job = job_repository.get_by_id(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found for publishing complete event")
            return

        # Update the job with publishing information
        metadata = {}
        if platform and platform_id:
            metadata[f"{platform}_id"] = platform_id

        if status == "success":
            metadata[f"{platform}_status"] = "published"
        else:
            error_message = message.get("error", "Unknown publishing error")
            metadata[f"{platform}_status"] = "failed"
            metadata[f"{platform}_error"] = error_message

        # Update the job with the publishing metadata
        job_repository.update_metadata(job_id, metadata)

        logger.info(f"Updated job {job_id} with publishing information for {platform}")
    except Exception as e:
        logger.error(
            f"Error handling publishing complete event: {str(e)}", exc_info=True
        )
        raise VideoProcessingError(
            f"Failed to process publishing event: {str(e)}"
        ) from e


def register_handlers(
    message_handler,
    video_processor: VideoProcessorService,
    job_repository: JobRepository,
) -> None:
    """
    Register all event handlers with the message handler.

    Args:
        message_handler: The message handler instance
        video_processor: Instance of VideoProcessorService
        job_repository: Instance of JobRepository
    """

    # Define a wrapper for each handler that provides the required dependencies
    def video_uploaded_wrapper(message_data: Dict[str, Any]) -> None:
        handle_video_uploaded(message_data, video_processor, job_repository)

    def processing_complete_wrapper(message_data: Dict[str, Any]) -> None:
        handle_processing_complete(message_data, job_repository)

    def publishing_complete_wrapper(message_data: Dict[str, Any]) -> None:
        handle_publishing_complete(message_data, job_repository)

    # Register handlers for specific topics
    message_handler.subscribe("video-uploaded", video_uploaded_wrapper)
    message_handler.subscribe("processing-complete", processing_complete_wrapper)
    message_handler.subscribe("publishing-complete", publishing_complete_wrapper)

    logger.info("Registered all event handlers")
