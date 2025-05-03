"""
Video processing core functionality.
"""

import os
import tempfile
import uuid
from typing import Any

from video_processor.config import get_settings
from video_processor.core.models import (
    ProcessingStage,
    ProcessingStatus,
    VideoJob,
    VideoMetadata,
)
from video_processor.services.storage import get_storage_service
from video_processor.utils.error_handling import VideoProcessingError
from video_processor.utils.file_handling import normalize_filename
from video_processor.utils.logging import get_logger

from .audio import AudioProcessor

logger = get_logger(__name__)


def process_video_event(bucket_name: str, file_name: str) -> None:
    """
    Process a video upload event.

    Args:
        bucket_name: Name of the GCS bucket
        file_name: Path to the file in the bucket

    Raises:
        VideoProcessingError: If processing fails
    """
    settings = get_settings()

    # Skip non-target files
    if not file_name.endswith(".mp4") or not file_name.startswith(
        ("daily-raw/", "main-raw/")
    ):
        logger.info(f"Skipping non-target file: {file_name}")
        return

    # Create a job ID for tracking
    job_id = str(uuid.uuid4())
    logger.info(
        f"Starting video processing job {job_id} for gs://{bucket_name}/{file_name}"
    )

    # Initialize components with dependency injection
    storage_service = get_storage_service(
        testing_mode=settings.testing_mode, local_output=settings.local_output
    )
    audio_processor = AudioProcessor(testing_mode=settings.testing_mode)

    # Create video job object
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    base_name_normalized = normalize_filename(base_name)
    channel = "daily" if file_name.startswith("daily-raw/") else "main"
    processed_path = f"processed-{channel}/{base_name_normalized}/"

    # Initialize metadata
    metadata = VideoMetadata(title=base_name, channel=channel)

    # Create video job
    job = VideoJob(
        bucket_name=bucket_name,
        file_name=file_name,
        job_id=job_id,
        metadata=metadata,
        processed_path=processed_path,
    )

    # Log job initialization
    logger.info(f"Initialized job {job.job_id}:")
    logger.info(f"  Original file: gs://{bucket_name}/{file_name}")
    logger.info(f"  Output path: gs://{bucket_name}/{processed_path}")

    try:
        # Process the video
        process_video(job, storage_service, audio_processor)

        # Log successful completion
        logger.info(f"✅ Successfully processed job {job.job_id}")
    except Exception as e:
        # Log error and update job status
        logger.error(
            f"❌ Error processing job {job.job_id}: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        job.update_status(ProcessingStatus.FAILED, str(e))
        raise VideoProcessingError(f"Failed to process video: {str(e)}") from e


def process_video(
    job: VideoJob, storage_service: Any, audio_processor: AudioProcessor
) -> None:
    """
    Process a video job through all stages.

    Args:
        job: Video job to process
        storage_service: Storage service instance
        audio_processor: Audio processor instance

    Raises:
        VideoProcessingError: If processing fails
    """
    settings = get_settings()

    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Update job status
        job.update_status(ProcessingStatus.IN_PROGRESS)

        # Set file paths
        video_filename = os.path.basename(job.file_name)
        video_path = os.path.join(tmpdir, video_filename)
        base_name = os.path.splitext(video_filename)[0]
        audio_path = os.path.join(tmpdir, f"{base_name}.wav")

        # Execute each processing stage
        _download_video(job, storage_service, video_path, settings)

        # Extract audio from video
        _extract_audio(job, audio_processor, video_path, audio_path)

        # Implement additional processing stages

        # Upload results
        _upload_results(job, storage_service, video_filename, settings)

        # Complete the job
        job.move_to_stage(ProcessingStage.COMPLETE)
        job.update_status(ProcessingStatus.COMPLETED)


def _download_video(
    job: VideoJob, storage_service: Any, video_path: str, settings: Any
) -> None:
    """Download the video file from storage."""
    job.current_stage = ProcessingStage.DOWNLOAD
    try:
        logger.info(
            f"Downloading video from gs://{job.bucket_name}/{job.file_name} "
            f"to local path {video_path}..."
        )

        # If in testing mode, create dummy file
        if getattr(settings, "testing_mode", False):
            logger.info("TESTING MODE: Creating dummy video file")
            with open(video_path, "wb") as f:
                f.write(b"DUMMY MP4 FILE")
        else:
            # Download the video
            storage_service.download_file(job.bucket_name, job.file_name, video_path)

        logger.info("Download complete.")
        job.complete_current_stage()
    except Exception as e:
        logger.error(f"Failed to download video: {type(e).__name__}: {str(e)}")
        job.update_status(ProcessingStatus.FAILED, f"Download failed: {str(e)}")
        raise VideoProcessingError(
            f"Failed to download video from {job.bucket_name}/{job.file_name}: {str(e)}"
        ) from e


def _extract_audio(
    job: VideoJob, audio_processor: AudioProcessor, video_path: str, audio_path: str
) -> None:
    """Extract audio from the video file."""
    job.move_to_stage(ProcessingStage.EXTRACT_AUDIO)
    try:
        logger.info(f"Extracting audio from {video_path} to {audio_path}...")
        audio_processor.extract_audio(video_path, audio_path)
        logger.info("Audio extraction complete.")
        job.complete_current_stage()
    except Exception as e:
        logger.error(f"Failed to extract audio: {type(e).__name__}: {str(e)}")
        job.update_status(ProcessingStatus.FAILED, f"Audio extraction failed: {str(e)}")
        raise VideoProcessingError(
            f"Failed to extract audio from {video_path}: {str(e)}"
        ) from e


def _add_dummy_outputs(job: VideoJob, storage_service: Any) -> None:
    """
    Add dummy output files for testing or initial structure.
    In a production implementation, this would be replaced with real outputs.
    """
    # Add dummy content for each output type
    dummy_outputs = {
        "transcript.txt": "This is a dummy transcript for testing purposes.",
        "subtitles.vtt": (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:05.000\n"
            "This is a dummy subtitle for testing.\n\n"
            "00:00:05.000 --> 00:00:10.000\n"
            "More dummy subtitles."
        ),
        "shownotes.txt": (
            "# Dummy Shownotes\n\n"
            "## Key takeaways\n"
            "- Point 1\n"
            "- Point 2\n\n"
            "## Resources mentioned\n"
            "- [Example link](https://example.com)"
        ),
        "chapters.txt": (
            "00:00 - Introduction\n" "02:00 - Main content\n" "05:00 - Conclusion"
        ),
        "title.txt": job.metadata.title,
    }

    # Upload each dummy output
    for filename, content in dummy_outputs.items():
        output_path = f"{job.processed_path}{filename}"
        storage_service.upload_from_string(
            bucket=job.bucket_name, content=content, destination_path=output_path
        )
        job.add_output_file(filename, output_path)
        logger.info(f"Added dummy output: {output_path}")


def _upload_results(
    job: VideoJob, storage_service: Any, video_filename: str, settings: Any
) -> None:
    """Upload job results to storage."""
    job.move_to_stage(ProcessingStage.UPLOAD_RESULTS)
    try:
        logger.info(f"Uploading results for job {job.job_id}...")

        # In testing mode, generate dummy outputs
        if getattr(settings, "testing_mode", False):
            logger.info("TESTING MODE: Generating dummy outputs")
            _add_dummy_outputs(job, storage_service)
        else:
            # Here we would process and upload real outputs
            # This is a placeholder for implementation
            logger.info("Uploading actual results - implementation needed")
            _add_dummy_outputs(job, storage_service)  # Temporary while implementing

        logger.info("Upload results complete.")
        job.complete_current_stage()
    except Exception as e:
        logger.error(f"Failed to upload outputs: {type(e).__name__}: {str(e)}")
        job.update_status(ProcessingStatus.PARTIAL, f"Output upload failed: {str(e)}")
        # Don't re-raise, try to continue
