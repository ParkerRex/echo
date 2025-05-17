"""
Service for orchestrating the video processing pipeline.

This module implements the core business logic for video processing workflows,
handling the entire pipeline from initial upload through processing stages to
completion. It coordinates between repositories, storage systems, AI services,
and utility libraries to process videos and extract metadata.

The service manages background tasks, error handling, and provides status tracking
of processing jobs, implementing a robust pipeline for video analysis.

Usage:
    from fastapi import BackgroundTasks, Depends
    from sqlalchemy.orm import Session
    from apps.core.services.video_processing_service import VideoProcessingService

    # Inject dependencies and create service
    video_processing_service = VideoProcessingService(
        video_repo=VideoRepository(),
        job_repo=VideoJobRepository(),
        metadata_repo=VideoMetadataRepository(),
        storage=file_storage_service,
        ai_adapter=ai_adapter,
        ffmpeg_utils=ffmpeg_utils,
        subtitle_utils=subtitle_utils,
        file_utils=file_utils
    )

    # Initiate video processing
    job = await video_processing_service.initiate_video_processing(
        db=db_session,
        original_filename="video.mp4",
        video_content=file_bytes,
        content_type="video/mp4",
        uploader_user_id=user_id,
        background_tasks=background_tasks
    )

    # Get job status
    job_details = await video_processing_service.get_job_details(
        db=db_session,
        job_id=job.id,
        user_id=user_id
    )
"""

from typing import Optional

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from apps.core.core.exceptions import VideoProcessingError
from apps.core.lib.ai.base_adapter import AIAdapterInterface
from apps.core.lib.auth.supabase_auth import AuthenticatedUser
from apps.core.lib.storage.file_storage import FileStorageService
from apps.core.lib.utils.ffmpeg_utils import FfmpegUtils
from apps.core.lib.utils.file_utils import FileUtils
from apps.core.lib.utils.subtitle_utils import SubtitleUtils
from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.models.video_metadata_model import VideoMetadataModel
from apps.core.models.video_model import VideoModel
from apps.core.operations.video_job_repository import VideoJobRepository
from apps.core.operations.video_metadata_repository import VideoMetadataRepository
from apps.core.operations.video_repository import VideoRepository


class VideoProcessingService:
    """
    Service layer for orchestrating the video processing pipeline.

    This service coordinates the end-to-end processing of video uploads, including
    storage, metadata extraction, AI processing, and status tracking. It manages the
    complex workflow of video analysis while keeping the API layer simple.

    Attributes:
        video_repo (VideoRepository): Repository for video data access.
        job_repo (VideoJobRepository): Repository for job data access.
        metadata_repo (VideoMetadataRepository): Repository for metadata access.
        storage (FileStorageService): Service for file storage operations.
        ai_adapter (AIAdapterInterface): AI service for text generation and transcription.
        ffmpeg_utils (FfmpegUtils): Utilities for video processing operations.
        subtitle_utils (SubtitleUtils): Utilities for subtitle generation.
        file_utils (FileUtils): Utilities for file system operations.
    """

    def __init__(
        self,
        video_repo: VideoRepository,
        job_repo: VideoJobRepository,
        metadata_repo: VideoMetadataRepository,
        storage: FileStorageService,
        ai_adapter: AIAdapterInterface,
        ffmpeg_utils: FfmpegUtils,
        subtitle_utils: SubtitleUtils,
        file_utils: FileUtils,
    ):
        self.video_repo = video_repo
        self.job_repo = job_repo
        self.metadata_repo = metadata_repo
        self.storage = storage
        self.ai_adapter = ai_adapter
        self.ffmpeg_utils = ffmpeg_utils
        self.subtitle_utils = subtitle_utils
        self.file_utils = file_utils

    async def initiate_video_processing(
        self,
        db: Session,
        original_filename: str,
        video_content: bytes,
        content_type: str,
        uploader_user_id: str,
        background_tasks: BackgroundTasks,
    ) -> VideoJobModel:
        """
        Initiate the video processing pipeline for a newly uploaded video.

        This method handles the initial steps of the video processing workflow:
        1. Saves the uploaded video to storage
        2. Creates database records for the video and processing job
        3. Schedules the full processing pipeline as a background task

        Args:
            db (Session): Database session for database operations
            original_filename (str): Original filename of the uploaded video
            video_content (bytes): Raw video file content
            content_type (str): MIME type of the video file (e.g., "video/mp4")
            uploader_user_id (str): ID of the user who uploaded the video
            background_tasks (BackgroundTasks): FastAPI background tasks manager

        Returns:
            VideoJobModel: Created job model with PENDING status

        Note:
            This method commits the transaction before returning, ensuring the
            records are visible to the background task that will process the video.
        """
        # Save video file
        stored_video_path = await self.storage.save_file(
            file_content=video_content,
            filename=original_filename,
            subdir=f"uploads/{uploader_user_id}",
        )
        # Create VideoModel
        video = self.video_repo.create(
            db=db,
            uploader_user_id=uploader_user_id,
            original_filename=original_filename,
            storage_path=stored_video_path,
            content_type=content_type,
            size_bytes=len(video_content),
        )
        # Create VideoJobModel
        job = self.job_repo.create(
            db=db,
            video_id=video.id,
            status=ProcessingStatus.PENDING,
            processing_stages=None,
            error_message=None,
        )
        db.commit()
        # Schedule background processing
        background_tasks.add_task(
            self._execute_processing_pipeline, job.id, stored_video_path
        )
        return job

    async def _execute_processing_pipeline(
        self,
        job_id: int,
        video_storage_path: str,
    ):
        """
        Execute the full video processing pipeline as a background task.

        This method is the core of the video processing workflow, handling all
        steps from downloading the video through processing to metadata generation.
        It's designed to run as a background task and updates the job status
        throughout the process.

        Processing steps:
        1. Set up a database session and temporary directory
        2. Download the video from storage to local temp directory
        3. Extract basic video metadata (duration, resolution, format)
        4. Extract audio track from the video
        5. Transcribe audio to text using AI service
        6. Generate content metadata (title, description, tags) using AI
        7. Generate subtitle files in multiple formats
        8. Extract thumbnail image from the video
        9. Update job status to COMPLETED when done

        Args:
            job_id (int): ID of the video processing job
            video_storage_path (str): Storage path of the uploaded video

        Note:
            This method handles its own error management, updating the job status to FAILED
            if any step encounters an exception. It also ensures proper cleanup of temporary
            files and database connections.
        """
        from apps.core.lib.database.connection import get_db_session

        db_bg = next(get_db_session())
        temp_dir = self.file_utils.create_temp_dir()
        try:
            job = self.job_repo.get_by_id(db_bg, job_id)
            if not job:
                raise VideoProcessingError(f"Job {job_id} not found")
            self.job_repo.update_status(db_bg, job_id, ProcessingStatus.PROCESSING)
            db_bg.commit()

            # Download video to temp dir
            local_video_path = f"{temp_dir}/{job.video.original_filename}"
            await self.storage.download_file(video_storage_path, local_video_path)

            # Step 1: Basic Metadata
            video_metadata = self.ffmpeg_utils.get_video_metadata_sync(local_video_path)
            self.metadata_repo.create_or_update(
                db_bg,
                job_id,
                extracted_video_duration_seconds=video_metadata.get("duration"),
                extracted_video_resolution=video_metadata.get("resolution"),
                extracted_video_format=video_metadata.get("format"),
            )
            db_bg.commit()

            # Step 2: Extract Audio
            audio_path = f"{temp_dir}/audio.wav"
            self.ffmpeg_utils.extract_audio_sync(local_video_path, audio_path)

            # Step 3: Transcript
            transcript_text = await self.ai_adapter.transcribe_audio(audio_path)
            transcript_file_path = f"{temp_dir}/transcript.txt"
            with open(transcript_file_path, "w") as f:
                f.write(transcript_text)
            transcript_url = await self.storage.save_file(
                file_content=transcript_text.encode("utf-8"),
                filename="transcript.txt",
                subdir=f"transcripts/{job.video.uploader_user_id}",
            )

            self.metadata_repo.create_or_update(
                db_bg,
                job_id,
                transcript_text=transcript_text,
                transcript_file_url=transcript_url,
            )
            db_bg.commit()

            # Step 4: Content Metadata
            title = await self.ai_adapter.generate_text(
                prompt="Generate a YouTube-style title for this video.",
                context=transcript_text,
            )
            description = await self.ai_adapter.generate_text(
                prompt="Generate a YouTube-style description for this video.",
                context=transcript_text,
            )
            tags = await self.ai_adapter.generate_text(
                prompt="Generate a comma-separated list of tags for this video.",
                context=transcript_text,
            )
            show_notes = await self.ai_adapter.generate_text(
                prompt="Generate show notes for this video.", context=transcript_text
            )
            self.metadata_repo.create_or_update(
                db_bg,
                job_id,
                title=title,
                description=description,
                tags=[t.strip() for t in tags.split(",")],
                show_notes_text=show_notes,
            )
            db_bg.commit()

            # Step 5: Subtitles
            segments = [
                {"text": line, "start_time": 0.0, "end_time": 0.0}
                for line in transcript_text.splitlines()
            ]
            vtt_content = self.subtitle_utils.generate_vtt(segments)
            srt_content = self.subtitle_utils.generate_srt(segments)
            vtt_url = await self.storage.save_file(
                file_content=vtt_content.encode("utf-8"),
                filename="subtitles.vtt",
                subdir=f"subtitles/{job.video.uploader_user_id}",
            )
            srt_url = await self.storage.save_file(
                file_content=srt_content.encode("utf-8"),
                filename="subtitles.srt",
                subdir=f"subtitles/{job.video.uploader_user_id}",
            )
            self.metadata_repo.create_or_update(
                db_bg,
                job_id,
                subtitle_files_urls={"vtt": vtt_url, "srt": srt_url},
            )
            db_bg.commit()

            # Step 6: Thumbnail
            thumbnail_path = f"{temp_dir}/thumbnail.jpg"
            self.ffmpeg_utils.extract_frame_sync(local_video_path, 1.0, thumbnail_path)
            with open(thumbnail_path, "rb") as f:
                thumbnail_bytes = f.read()
            thumbnail_url = await self.storage.save_file(
                file_content=thumbnail_bytes,
                filename="thumbnail.jpg",
                subdir=f"thumbnails/{job.video.uploader_user_id}",
            )
            self.metadata_repo.create_or_update(
                db_bg,
                job_id,
                thumbnail_file_url=thumbnail_url,
            )
            db_bg.commit()

            # Mark job as completed
            self.job_repo.update_status(db_bg, job_id, ProcessingStatus.COMPLETED)
            db_bg.commit()
        except Exception as e:
            self.job_repo.update_status(db_bg, job_id, ProcessingStatus.FAILED)
            self.job_repo.add_processing_stage(db_bg, job_id, f"Error: {str(e)}")
            db_bg.commit()
        finally:
            self.file_utils.cleanup_temp_dir(temp_dir)
            db_bg.close()

    async def get_job_details(
        self, db: Session, job_id: int, user_id: str
    ) -> Optional[VideoJobModel]:
        """
        Retrieve video processing job details with access control checks.

        This method fetches a video processing job by ID, but includes authorization
        checks to ensure the requesting user is the owner of the associated video.
        It returns the job with its related video and metadata objects for a
        complete view of the processing status.

        Args:
            db (Session): Database session for database operations
            job_id (int): ID of the video processing job to retrieve
            user_id (str): ID of the user requesting the job details

        Returns:
            Optional[VideoJobModel]: The job with related objects if found and authorized

        Raises:
            HTTPException: 404 error if job not found or user is not authorized to view it
        """
        job = self.job_repo.get_by_id(db, job_id)
        if not job or job.video.uploader_user_id != user_id:
            raise HTTPException(status_code=404, detail="Job not found")
        # Eagerly load related video and metadata if not already loaded
        return job
