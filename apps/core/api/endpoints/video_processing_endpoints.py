"""
API endpoints for video processing functionality.

This module defines FastAPI routes for video upload, processing, and status retrieval.
It provides a clean RESTful interface for the video processing pipeline, handling
authentication, request validation, response formatting, and error handling.

The endpoints handle:
- Video file uploads with validation
- Asynchronous video processing via background tasks
- Status checking for ongoing and completed jobs
- Authorization to ensure users only access their own data

All business logic is delegated to the VideoProcessingService, with this module
focusing solely on HTTP concerns.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from apps.core.api.schemas.video_processing_schemas import (
    VideoJobSchema,
    VideoUploadResponseSchema,
)
from apps.core.core.config import settings
from apps.core.lib.ai.ai_client_factory import get_ai_adapter
from apps.core.lib.auth.supabase_auth import AuthenticatedUser, get_current_user
from apps.core.lib.database.connection import get_async_db_session, get_db_session
from apps.core.lib.storage.file_storage import FileStorageService
from apps.core.lib.utils.ffmpeg_utils import FfmpegUtils
from apps.core.lib.utils.file_utils import FileUtils
from apps.core.lib.utils.subtitle_utils import SubtitleUtils
from apps.core.operations.video_job_repository import (
    VideoJobRepository,
    get_video_job_repository,
)
from apps.core.operations.video_metadata_repository import VideoMetadataRepository
from apps.core.operations.video_repository import VideoRepository, get_video_repository
from apps.core.services.video_processing_service import VideoProcessingService

router = APIRouter()


async def get_video_processing_service(
    # Repositories are now injected via their async getters
    video_repo: VideoRepository = Depends(get_video_repository),
    job_repo: VideoJobRepository = Depends(get_video_job_repository),
    # VideoMetadataRepository uses static methods, so no instance needed for them directly
    # However, VideoProcessingService expects an instance. We can pass a dummy or refactor service.
    # For now, let's assume VideoProcessingService can handle VideoMetadataRepository methods being called statically if needed
    # or we can instantiate it if it has a simple __init__.
    # VideoMetadataRepository has no __init__, its methods are static.
    # The service VideoProcessingService instantiates it as `metadata_repo: VideoMetadataRepository`. Let's keep that for now.
    # If VideoProcessingService directly calls VideoMetadataRepository.create_or_update (which it does), that's fine.
    storage_service: FileStorageService = Depends(
        FileStorageService
    ),  # Assuming FileStorageService can be Depended on directly or has a getter
    ai_adapter_instance=Depends(
        get_ai_adapter
    ),  # Renamed to avoid conflict, uses existing getter
    ffmpeg_utils_instance: FfmpegUtils = Depends(
        FfmpegUtils
    ),  # Assuming FfmpegUtils can be Depended on
    subtitle_utils_instance: SubtitleUtils = Depends(
        SubtitleUtils
    ),  # Assuming SubtitleUtils can be Depended on
    file_utils_instance: FileUtils = Depends(
        FileUtils
    ),  # Assuming FileUtils can be Depended on
) -> VideoProcessingService:
    # Dependency injection for the service and its dependencies
    return VideoProcessingService(
        video_repo=video_repo,  # Injected async repo
        job_repo=job_repo,  # Injected async repo
        metadata_repo=VideoMetadataRepository(),  # Instantiated as before (static methods)
        storage=storage_service,
        ai_adapter=ai_adapter_instance,
        ffmpeg_utils=ffmpeg_utils_instance,
        subtitle_utils=subtitle_utils_instance,
        file_utils=file_utils_instance,
    )


@router.post(
    "/upload",
    response_model=VideoUploadResponseSchema,
    summary="Upload a video and initiate processing",
)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db_session),
    service: VideoProcessingService = Depends(get_video_processing_service),
):
    """
    Upload a video file and initiate the processing pipeline.

    This endpoint allows users to upload a video file, which is then processed to:
    - Extract metadata (duration, resolution, format)
    - Generate a transcript
    - Create AI-generated title, description, and tags
    - Generate subtitle files (VTT and SRT formats)
    - Extract a thumbnail image

    The processing occurs asynchronously in the background, and clients can
    check the processing status using the returned job_id.

    Returns:
        VideoUploadResponseSchema: Contains the job_id and initial PENDING status

    Raises:
        400: If the uploaded file is not a video or is missing metadata
        401: If the user is not authenticated
    """
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    if not file.filename or not file.content_type:
        raise HTTPException(status_code=400, detail="Missing file metadata")
    video_content = await file.read()
    job = await service.initiate_video_processing(
        db=db,
        original_filename=file.filename,
        video_content=video_content,
        content_type=file.content_type,
        uploader_user_id=current_user.id,
        background_tasks=background_tasks,
    )
    return VideoUploadResponseSchema(job_id=job.id, status=job.status)


@router.get(
    "/jobs/{job_id}",
    response_model=VideoJobSchema,
    summary="Get video processing job details",
)
async def get_job_details(
    job_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db_session),
    service: VideoProcessingService = Depends(get_video_processing_service),
):
    """
    Retrieve details and status of a video processing job.

    This endpoint allows users to check the status of a video processing job and retrieve
    all associated metadata. It includes authorization checks to ensure users can only
    access their own video processing jobs.

    The response includes:
    - Job status (PENDING, PROCESSING, COMPLETED, FAILED)
    - Processing stages information
    - Error messages (if any)
    - Video metadata (title, description, tags, etc.)
    - Generated asset URLs (transcript, subtitles, thumbnail)
    - Technical metadata (duration, resolution, format)

    Path Parameters:
        job_id (int): The ID of the video processing job to retrieve

    Returns:
        VideoJobSchema: Complete job information with nested video and metadata

    Raises:
        401: If the user is not authenticated
        403/404: If the job doesn't exist or belongs to another user
    """
    job = await service.get_job_details(db=db, job_id=job_id, user_id=current_user.id)
    return job
