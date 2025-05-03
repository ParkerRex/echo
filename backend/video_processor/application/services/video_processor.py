"""
Video processor service for orchestrating the video processing pipeline.

This module provides the main service for coordinating the video processing workflow,
from initial upload to completed processing and publishing.
"""

import logging
import os
import tempfile
from typing import Dict, Optional

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.application.services.metadata import MetadataService
from video_processor.application.services.subtitle import SubtitleService
from video_processor.application.services.transcription import TranscriptionService
from video_processor.domain.exceptions import (
    InvalidVideoError,
    MetadataGenerationError,
    ProcessingError,
    StorageError,
)
from video_processor.domain.models.job import JobStatus, VideoJob
from video_processor.utils.ffmpeg import (
    extract_audio,
    extract_frame,
    get_video_metadata,
)


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

        # Initialize dependent services
        self._transcription_service = TranscriptionService(ai_adapter)
        self._subtitle_service = SubtitleService()
        self._metadata_service = MetadataService(ai_adapter)

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

            # Create a temporary directory for processing files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download video file if needed
                video_path = self._prepare_video_file(job, temp_dir)
                job.update_stage("video_prepared")

                # Extract video metadata
                self._extract_video_metadata(job, video_path)
                job.update_stage("metadata_extracted")

                # Generate transcript
                transcript_path = self._generate_transcript(job, video_path, temp_dir)
                job.update_stage("transcript_generated")

                # Generate metadata (title, description, tags)
                self._generate_content_metadata(job, transcript_path)
                job.update_stage("metadata_generated")

                # Generate subtitles
                subtitle_paths = self._generate_subtitles(
                    job, transcript_path, temp_dir
                )
                job.update_stage("subtitles_generated")

                # Generate thumbnail
                thumbnail_path = self._generate_thumbnail(job, video_path, temp_dir)
                job.update_stage("thumbnail_generated")

                # Upload and organize output files
                self._upload_output_files(
                    job, video_path, transcript_path, subtitle_paths, thumbnail_path
                )
                job.update_stage("files_uploaded")

            # Mark job as completed
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

        except StorageError as e:
            job.status = JobStatus.FAILED
            job.error = f"Storage operation failed: {str(e)}"
            logging.error(f"Storage operation failed for job {job.id}: {str(e)}")
            raise

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = f"Processing error: {str(e)}"
            logging.error(f"Unexpected error in job {job.id}: {str(e)}")
            raise ProcessingError(f"Video processing failed: {str(e)}") from e

    def _prepare_video_file(self, job: VideoJob, temp_dir: str) -> str:
        """
        Prepare the video file for processing.

        Downloads the file if needed or uses the local path.

        Args:
            job: The video job
            temp_dir: Temporary directory for processing

        Returns:
            Path to the video file
        """
        logging.info(f"Preparing video file for job {job.id}")

        video_path = job.video.file_path

        # If the path is a GCS URL or other remote path, download it
        if video_path.startswith("gs://") or video_path.startswith("http"):
            local_video_path = os.path.join(
                temp_dir, f"input_video{os.path.splitext(video_path)[1]}"
            )
            video_path = self._storage.download_file(video_path, local_video_path)
            logging.info(f"Downloaded video to {video_path}")

        # Validate the video file
        if not os.path.exists(video_path):
            raise InvalidVideoError(f"Video file not found: {video_path}")

        return video_path

    def _extract_video_metadata(self, job: VideoJob, video_path: str) -> None:
        """
        Extract metadata from the video file and update the job.

        Args:
            job: The video job
            video_path: Path to the video file
        """
        logging.info(f"Extracting video metadata for job {job.id}")

        try:
            # Extract metadata using FFmpeg
            video_info = get_video_metadata(video_path)

            # Update video and metadata objects
            job.video.duration = video_info.get("duration", 0)
            job.video.resolution = video_info.get("resolution", (0, 0))
            job.video.format = video_info.get("format", "unknown")

            logging.info(
                f"Video metadata extracted: duration={job.video.duration}, resolution={job.video.resolution}"
            )

        except Exception as e:
            logging.error(f"Failed to extract video metadata: {str(e)}")
            raise InvalidVideoError(f"Failed to extract video metadata: {str(e)}")

    def _generate_transcript(
        self, job: VideoJob, video_path: str, temp_dir: str
    ) -> str:
        """
        Generate transcript for the video.

        Args:
            job: The video job
            video_path: Path to the video file
            temp_dir: Temporary directory for processing

        Returns:
            Path to the transcript file
        """
        logging.info(f"Generating transcript for job {job.id}")

        try:
            # Extract audio
            audio_path = os.path.join(temp_dir, "audio.wav")
            extract_audio(video_path, audio_path)

            # Generate transcript
            transcript_path = os.path.join(temp_dir, "transcript.txt")
            transcript_text = self._transcription_service.generate_transcript(
                audio_path
            )

            # Save transcript to file
            with open(transcript_path, "w") as f:
                f.write(transcript_text)

            # Update job metadata with transcript
            job.metadata.transcript = transcript_text

            logging.info(f"Transcript generated and saved to {transcript_path}")
            return transcript_path

        except Exception as e:
            logging.error(f"Failed to generate transcript: {str(e)}")
            raise MetadataGenerationError(f"Failed to generate transcript: {str(e)}")

    def _generate_content_metadata(self, job: VideoJob, transcript_path: str) -> None:
        """
        Generate content metadata (title, description, tags) from transcript.

        Args:
            job: The video job
            transcript_path: Path to the transcript file
        """
        logging.info(f"Generating content metadata for job {job.id}")

        try:
            with open(transcript_path, "r") as f:
                transcript_text = f.read()

            # Generate title
            job.metadata.title = self._metadata_service.generate_title(transcript_text)

            # Generate description
            job.metadata.description = self._metadata_service.generate_description(
                transcript_text
            )

            # Generate tags
            job.metadata.tags = self._metadata_service.generate_tags(transcript_text)

            # Generate show notes
            job.metadata.show_notes = self._metadata_service.generate_show_notes(
                transcript_text
            )

            logging.info(f"Content metadata generated for job {job.id}")

        except Exception as e:
            logging.error(f"Failed to generate content metadata: {str(e)}")
            raise MetadataGenerationError(
                f"Failed to generate content metadata: {str(e)}"
            )

    def _generate_subtitles(
        self, job: VideoJob, transcript_path: str, temp_dir: str
    ) -> Dict[str, str]:
        """
        Generate subtitles in various formats from the transcript.

        Args:
            job: The video job
            transcript_path: Path to the transcript file
            temp_dir: Temporary directory for processing

        Returns:
            Dictionary mapping format names to file paths
        """
        logging.info(f"Generating subtitles for job {job.id}")

        subtitle_paths = {}

        try:
            with open(transcript_path, "r") as f:
                transcript_text = f.read()

            # Generate VTT subtitles
            vtt_path = os.path.join(temp_dir, "subtitles.vtt")
            self._subtitle_service.generate_vtt(transcript_text, vtt_path)
            subtitle_paths["vtt"] = vtt_path

            # Generate SRT subtitles
            srt_path = os.path.join(temp_dir, "subtitles.srt")
            self._subtitle_service.generate_srt(transcript_text, srt_path)
            subtitle_paths["srt"] = srt_path

            logging.info(f"Subtitles generated for job {job.id}")
            return subtitle_paths

        except Exception as e:
            logging.error(f"Failed to generate subtitles: {str(e)}")
            raise MetadataGenerationError(f"Failed to generate subtitles: {str(e)}")

    def _generate_thumbnail(self, job: VideoJob, video_path: str, temp_dir: str) -> str:
        """
        Generate thumbnail image for the video.

        Args:
            job: The video job
            video_path: Path to the video file
            temp_dir: Temporary directory for processing

        Returns:
            Path to the thumbnail image
        """
        logging.info(f"Generating thumbnail for job {job.id}")

        try:
            # Determine thumbnail timestamp (e.g., 10% into the video)
            timestamp = job.video.get_thumbnail_time()

            # Extract frame
            thumbnail_path = os.path.join(temp_dir, "thumbnail.jpg")
            extract_frame(video_path, timestamp, thumbnail_path)

            logging.info(f"Thumbnail generated at {thumbnail_path}")
            return thumbnail_path

        except Exception as e:
            logging.error(f"Failed to generate thumbnail: {str(e)}")
            # Not raising an error here as this is not critical for processing
            return ""

    def _upload_output_files(
        self,
        job: VideoJob,
        video_path: str,
        transcript_path: str,
        subtitle_paths: Dict[str, str],
        thumbnail_path: str,
    ) -> None:
        """
        Upload and organize all output files.

        Args:
            job: The video job
            video_path: Path to the video file
            transcript_path: Path to the transcript file
            subtitle_paths: Dictionary of subtitle format to file paths
            thumbnail_path: Path to the thumbnail image
        """
        logging.info(f"Uploading output files for job {job.id}")

        try:
            # Create base output path
            base_path = f"processed/{job.id}"
            os.makedirs(os.path.join(self._local_output_dir, base_path), exist_ok=True)

            # Upload transcript
            transcript_dest = f"{base_path}/transcript.txt"
            if self._output_bucket:
                transcript_url = self._storage.upload_file(
                    transcript_path, f"{self._output_bucket}/{transcript_dest}"
                )
            else:
                transcript_url = self._storage.upload_file(
                    transcript_path,
                    os.path.join(self._local_output_dir, transcript_dest),
                )
            job.metadata.transcript_url = transcript_url

            # Upload subtitles
            subtitle_urls = {}
            for format_name, subtitle_path in subtitle_paths.items():
                subtitle_dest = f"{base_path}/subtitles.{format_name}"
                if self._output_bucket:
                    subtitle_url = self._storage.upload_file(
                        subtitle_path, f"{self._output_bucket}/{subtitle_dest}"
                    )
                else:
                    subtitle_url = self._storage.upload_file(
                        subtitle_path,
                        os.path.join(self._local_output_dir, subtitle_dest),
                    )
                subtitle_urls[format_name] = subtitle_url
            job.metadata.subtitle_urls = subtitle_urls

            # Upload thumbnail if available
            if thumbnail_path and os.path.exists(thumbnail_path):
                thumbnail_dest = f"{base_path}/thumbnail.jpg"
                if self._output_bucket:
                    thumbnail_url = self._storage.upload_file(
                        thumbnail_path, f"{self._output_bucket}/{thumbnail_dest}"
                    )
                else:
                    thumbnail_url = self._storage.upload_file(
                        thumbnail_path,
                        os.path.join(self._local_output_dir, thumbnail_dest),
                    )
                job.metadata.thumbnail_url = thumbnail_url

            logging.info(f"All output files uploaded for job {job.id}")

        except Exception as e:
            logging.error(f"Failed to upload output files: {str(e)}")
            raise StorageError(f"Failed to upload output files: {str(e)}")
