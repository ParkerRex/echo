"""
API routes for video processing.

This module provides API endpoints for uploading, processing, and retrieving videos.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.application.interfaces.repositories import JobRepositoryInterface
from video_processor.application.services.video_processor import VideoProcessorService
from video_processor.domain.exceptions import PublishingError
from video_processor.domain.models.enums import ProcessingStatus
from video_processor.domain.models.job import VideoJob
from video_processor.domain.models.metadata import VideoMetadata
from video_processor.domain.models.video import Video
from video_processor.infrastructure.api.dependencies import (
    get_job_repository,
    get_publishing_adapter,
    get_video_processor,
)
from video_processor.infrastructure.api.schemas.video import (
    JobResponse,
    JobStatusResponse,
    PublishResponse,
    VideoPublishRequest,
    VideoSummary,
    VideoUploadRequest,
    VideoUploadUrlRequest,
)

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/videos", tags=["videos"])


from supabase import Client, create_client

from video_processor.config.settings import settings
from video_processor.infrastructure.api.auth import get_current_active_user
from video_processor.infrastructure.api.dependencies import get_storage_adapter


@router.get(
    "/my",
    response_model=List[VideoSummary],
    summary="List videos for the current user",
    description="List all videos belonging to the authenticated user from Supabase.",
)
async def list_my_videos(
    user: dict = Depends(get_current_active_user),
) -> List[VideoSummary]:
    """
    List videos for the current user from Supabase.

    Args:
        user: Authenticated user (from JWT)

    Returns:
        List of VideoSummary objects
    """
    try:
        user_id = user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID missing from token")

        supabase_url = settings.supabase_url
        supabase_key = settings.supabase_service_role_key
        supabase: Client = create_client(supabase_url, supabase_key)

        # Query videos for the current user
        response = (
            supabase.table("videos")
            .select("id, title, processing_status, created_at, thumbnail_gcs_path")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        if response.error:
            raise HTTPException(
                status_code=500,
                detail=f"Supabase error: {response.error.message}",
            )

        videos = response.data or []
        # Map to VideoSummary
        return [
            VideoSummary(
                id=video["id"],
                title=video.get("title") or "",
                status=video.get("processing_status"),
                created_at=video.get("created_at"),
                thumbnail_url=video.get("thumbnail_gcs_path"),
            )
            for video in videos
        ]
    except Exception as e:
        logger.exception(f"Failed to list user videos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list user videos: {str(e)}",
        )


@router.post(
    "/upload-url",
    summary="Get a signed upload URL for direct video upload",
    description="Generate a signed URL for uploading a video file directly to storage.",
)
async def get_upload_url(
    request: VideoUploadUrlRequest,
    user: dict = Depends(get_current_active_user),
    storage=Depends(get_storage_adapter),
):
    """
    Generate a signed upload URL for a video file.

    Args:
        request: VideoUploadUrlRequest with filename, content_type, file_size
        user: Authenticated user (from JWT)
        storage: Storage adapter (GCS)

    Returns:
        JSON with signed_url and storage_path
    """
    try:
        user_id = user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID missing from token")

        # Use a bucket or prefix from config if needed; here we use a standard path
        # Example: videos/{user_id}/{filename}
        storage_path = f"videos/{user_id}/{request.filename}"

        signed_url = storage.get_upload_signed_url(
            storage_path,
            content_type=request.content_type,
        )

        return {
            "signed_url": signed_url,
            "storage_path": storage_path,
            "expires_in": 3600,
        }
    except Exception as e:
        logger.exception(f"Failed to generate upload signed URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate upload signed URL: {str(e)}",
        )


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload and process a video",
    description="Submit a video for processing. This will start an asynchronous processing job.",
)
async def upload_video(
    request: VideoUploadRequest,
    background_tasks: BackgroundTasks,
    job_repository: JobRepositoryInterface = Depends(get_job_repository),
    video_processor: VideoProcessorService = Depends(get_video_processor),
) -> JobResponse:
    """
    Upload and process a video.

    Args:
        request: Video upload request
        background_tasks: FastAPI background tasks
        job_repository: Job repository dependency
        video_processor: Video processor service dependency

    Returns:
        Job information
    """
    try:
        # Create video object
        video = Video(
            file_path=request.file_path,
            duration=0,  # Will be populated during processing
            format="unknown",  # Will be populated during processing
            resolution=(0, 0),  # Will be populated during processing
        )

        # Create metadata object
        metadata = VideoMetadata(
            title=request.title or "",
            description=request.description or "",
        )

        # Create job object
        job = VideoJob(
            video=video,
            metadata=metadata,
            status=ProcessingStatus.PENDING,
        )

        # Save job to repository
        job_id = job_repository.save(job)
        job.id = job_id

        # Start processing in background
        background_tasks.add_task(
            process_video_background,
            job_id=job_id,
            video_processor=video_processor,
            job_repository=job_repository,
            publish_to_youtube=request.publish_to_youtube,
        )

        # Get the job with assigned ID
        job = job_repository.get_by_id(job_id)

        # Convert to response model
        return job_to_response(job)

    except Exception as e:
        logger.exception(f"Failed to upload video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}",
        )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job details",
    description="Get details about a processing job, including video metadata and status.",
)
async def get_job(
    job_id: str,
    job_repository: JobRepositoryInterface = Depends(get_job_repository),
) -> JobResponse:
    """
    Get job details.

    Args:
        job_id: Job ID
        job_repository: Job repository dependency

    Returns:
        Job information

    Raises:
        HTTPException: If job not found
    """
    job = job_repository.get_by_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )

    return job_to_response(job)


@router.get(
    "/{job_id}/status",
    response_model=JobStatusResponse,
    summary="Get job status",
    description="Get the status of a processing job.",
)
async def get_job_status(
    job_id: str,
    job_repository: JobRepositoryInterface = Depends(get_job_repository),
) -> JobStatusResponse:
    """
    Get job status.

    Args:
        job_id: Job ID
        job_repository: Job repository dependency

    Returns:
        Job status information

    Raises:
        HTTPException: If job not found
    """
    job = job_repository.get_by_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )

    # Convert to response model
    stages = list(job.processing_stages.keys()) if job.processing_stages else []

    return JobStatusResponse(
        id=job.id,
        status=ProcessingStatus(job.status.value),
        error=job.error,
        stages=stages,
        updated_at=job.updated_at,
    )


@router.post(
    "/{job_id}/publish",
    response_model=PublishResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Publish a processed video",
    description="Publish a processed video to a platform like YouTube.",
)
async def publish_video(
    job_id: str,
    request: VideoPublishRequest,
    background_tasks: BackgroundTasks,
    job_repository: JobRepositoryInterface = Depends(get_job_repository),
    publishing_adapter: PublishingInterface = Depends(get_publishing_adapter),
) -> PublishResponse:
    """
    Publish a processed video.

    Args:
        job_id: Job ID
        request: Publish request
        background_tasks: FastAPI background tasks
        job_repository: Job repository dependency
        publishing_adapter: Publishing adapter dependency

    Returns:
        Publish response

    Raises:
        HTTPException: If job not found or video not processed
    """
    # Validate job ID in path matches request
    if job_id != request.job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job ID in path does not match job ID in request body",
        )

    # Get job from repository
    job = job_repository.get_by_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )

    # Check job status
    if job.status != ProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video processing not completed. Current status: {job.status.value}",
        )

    # Start publishing in background
    background_tasks.add_task(
        publish_video_background,
        job=job,
        platform=request.platform,
        custom_metadata=request.metadata.dict() if request.metadata else None,
        job_repository=job_repository,
        publishing_adapter=publishing_adapter,
    )

    # Return initial response
    return PublishResponse(
        job_id=job_id,
        platform=request.platform,
        platform_id="pending",
        status="publishing",
    )


@router.get(
    "",
    response_model=List[JobStatusResponse],
    summary="List processing jobs",
    description="List all processing jobs or filter by status.",
)
async def list_jobs(
    status: Optional[str] = None,
    job_repository: JobRepositoryInterface = Depends(get_job_repository),
) -> List[JobStatusResponse]:
    """
    List processing jobs.

    Args:
        status: Filter by status
        job_repository: Job repository dependency

    Returns:
        List of job status information
    """
    if status:
        try:
            job_status = ProcessingStatus(status)
            jobs = job_repository.get_jobs_by_status(job_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}",
            )
    else:
        # TODO: Implement getting all jobs
        # For now, return pending jobs
        jobs = job_repository.get_pending_jobs()

    # Convert to response models
    responses = []
    for job in jobs:
        stages = list(job.processing_stages.keys()) if job.processing_stages else []
        responses.append(
            JobStatusResponse(
                id=job.id,
                status=ProcessingStatus(job.status.value),
                error=job.error,
                stages=stages,
                updated_at=job.updated_at,
            )
        )

    return responses


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job",
    description="Delete a processing job and its associated data.",
)
async def delete_job(
    job_id: str,
    job_repository: JobRepositoryInterface = Depends(get_job_repository),
) -> None:
    """
    Delete a job.

    Args:
        job_id: Job ID
        job_repository: Job repository dependency

    Raises:
        HTTPException: If job not found or deletion fails
    """
    job = job_repository.get_by_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )

    success = job_repository.delete(job_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job with ID {job_id}",
        )


# Helper functions for background tasks


async def process_video_background(
    job_id: str,
    video_processor: VideoProcessorService,
    job_repository: JobRepositoryInterface,
    publish_to_youtube: bool = False,
) -> None:
    """
    Process a video in the background.

    Args:
        job_id: Job ID
        video_processor: Video processor service
        job_repository: Job repository
        publish_to_youtube: Whether to publish to YouTube after processing
    """
    try:
        logger.info(f"Starting background processing for job {job_id}")

        # Get job from repository
        job = job_repository.get_by_id(job_id)

        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return

        # Process video
        updated_job = video_processor.process_video(job)

        # Update job in repository
        job_repository.update(updated_job)

        logger.info(f"Completed background processing for job {job_id}")

        # TODO: If publish_to_youtube is True, start publishing process

    except Exception as e:
        logger.exception(f"Error in background processing for job {job_id}: {str(e)}")

        # Update job status to failed
        try:
            job_repository.update_job_status(
                job_id=job_id,
                status=ProcessingStatus.FAILED,
                error=str(e),
            )
        except Exception as update_error:
            logger.error(f"Failed to update job status: {str(update_error)}")


async def publish_video_background(
    job: VideoJob,
    platform: str,
    custom_metadata: Optional[Dict[str, Any]],
    job_repository: JobRepositoryInterface,
    publishing_adapter: PublishingInterface,
) -> None:
    """
    Publish a video in the background.

    Args:
        job: Video job
        platform: Publishing platform
        custom_metadata: Custom metadata for publishing
        job_repository: Job repository
        publishing_adapter: Publishing adapter
    """
    try:
        logger.info(f"Starting background publishing for job {job.id} to {platform}")

        if platform.lower() != "youtube":
            logger.error(f"Unsupported platform: {platform}")
            raise PublishingError(f"Unsupported platform: {platform}")

        # Prepare metadata
        metadata = {
            "title": job.metadata.title,
            "description": job.metadata.description,
            "tags": job.metadata.tags,
            "privacy_status": "private",  # Default to private
        }

        # Override with custom metadata if provided
        if custom_metadata:
            metadata.update(custom_metadata)

        # Upload video to YouTube
        platform_id = publishing_adapter.upload_video(
            video_file=job.video.file_path,
            metadata=metadata,
        )

        logger.info(
            f"Video for job {job.id} published to {platform} with ID {platform_id}"
        )

        # TODO: Store publishing result in database

    except Exception as e:
        logger.exception(f"Error in background publishing for job {job.id}: {str(e)}")
        # TODO: Store publishing error in database


def job_to_response(job: VideoJob) -> JobResponse:
    """
    Convert a VideoJob to a JobResponse.

    Args:
        job: VideoJob to convert

    Returns:
        JobResponse
    """
    return JobResponse(
        id=job.id,
        status=ProcessingStatus(job.status.value),
        video={
            "id": job.video.id,
            "file_path": job.video.file_path,
            "duration": job.video.duration,
            "format": job.video.format,
            "resolution": job.video.resolution,
            "created_at": job.video.created_at,
            "updated_at": job.video.updated_at,
        },
        metadata={
            "title": job.metadata.title,
            "description": job.metadata.description,
            "tags": job.metadata.tags,
            "show_notes": job.metadata.show_notes,
            "thumbnail_url": job.metadata.thumbnail_url,
            "transcript": job.metadata.transcript,
            "transcript_url": job.metadata.transcript_url,
            "subtitle_urls": job.metadata.subtitle_urls,
        },
        error=job.error,
        processing_stages=job.processing_stages,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
