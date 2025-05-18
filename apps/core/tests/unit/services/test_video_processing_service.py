"""
Unit tests for the VideoProcessingService.
"""

import os
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest
from fastapi import BackgroundTasks, HTTPException

# Assuming AsyncSession is needed for type hints if db mocks are AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.core.exceptions import VideoProcessingError
from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.models.video_metadata_model import VideoMetadataModel
from apps.core.models.video_model import VideoModel
from apps.core.services.video_processing_service import VideoProcessingService


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for the VideoProcessingService."""
    return {
        "video_repo": AsyncMock(),  # Repositories are now async
        "job_repo": AsyncMock(),  # Repositories are now async
        "metadata_repo": AsyncMock(),  # Repositories are now async
        "storage": AsyncMock(),  # Already AsyncMock
        "ai_adapter": AsyncMock(),  # Already AsyncMock
        # Assuming these utils remain synchronous. If any method called by service is async, these would need adjustment.
        "ffmpeg_utils": MagicMock(),
        "subtitle_utils": MagicMock(),
        "file_utils": MagicMock(),
    }


@pytest.fixture
def service(mock_dependencies):
    """Create a VideoProcessingService instance with mock dependencies."""
    return VideoProcessingService(
        video_repo=mock_dependencies["video_repo"],
        job_repo=mock_dependencies["job_repo"],
        metadata_repo=mock_dependencies["metadata_repo"],
        storage=mock_dependencies["storage"],
        ai_adapter=mock_dependencies["ai_adapter"],
        ffmpeg_utils=mock_dependencies["ffmpeg_utils"],
        subtitle_utils=mock_dependencies["subtitle_utils"],
        file_utils=mock_dependencies["file_utils"],
    )


@pytest.fixture
def mock_db_async() -> AsyncMock:  # Renamed and returns AsyncMock
    """Mock SQLAlchemy AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_background_tasks():
    """Mock FastAPI BackgroundTasks."""
    # BackgroundTasks itself is not async, its add_task method is sync.
    return MagicMock(spec=BackgroundTasks)


@pytest.fixture
def sample_video_data():
    """Sample video data for testing."""
    return {
        "original_filename": "test_video.mp4",
        "video_content": b"test video content",
        "content_type": "video/mp4",
        "uploader_user_id": "test-user-123",
    }


class TestVideoProcessingService:
    """Test cases for the VideoProcessingService class."""

    async def test_initiate_video_processing(
        self,
        service: VideoProcessingService,
        mock_db_async: AsyncMock,  # Use the async db mock
        mock_background_tasks: MagicMock,
        mock_dependencies: dict,
        sample_video_data: dict,
    ):
        """Test initiating video processing pipeline."""
        # Set up mock returns
        # storage.save_file is async, ensure it's awaited in service or its return is awaitable if mock is AsyncMock
        mock_dependencies[
            "storage"
        ].save_file.return_value = "gs://bucket/uploads/test-user-123/test_video.mp4"

        mock_video = AsyncMock(
            spec=VideoModel
        )  # Using AsyncMock if its attributes are accessed or methods called async
        mock_video.id = 1
        # repo.create is now async, so its mock should handle await or be an AsyncMock itself
        mock_dependencies["video_repo"].create.return_value = mock_video

        mock_job = AsyncMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_dependencies["job_repo"].create.return_value = mock_job

        # Call the service method (already awaited)
        result = await service.initiate_video_processing(
            db=mock_db_async,  # Pass async_db_mock
            **sample_video_data,
            background_tasks=mock_background_tasks,
        )

        assert result is mock_job

        # storage.save_file is async
        mock_dependencies["storage"].save_file.assert_awaited_once_with(
            file_content=sample_video_data["video_content"],
            filename=sample_video_data["original_filename"],
            subdir=f"uploads/{sample_video_data['uploader_user_id']}",
        )

        # video_repo.create is async
        mock_dependencies["video_repo"].create.assert_awaited_once_with(
            db=mock_db_async,
            uploader_user_id=sample_video_data["uploader_user_id"],
            original_filename=sample_video_data["original_filename"],
            storage_path="gs://bucket/uploads/test-user-123/test_video.mp4",
            content_type=sample_video_data["content_type"],
            size_bytes=len(sample_video_data["video_content"]),
        )

        # job_repo.create is async
        mock_dependencies["job_repo"].create.assert_awaited_once_with(
            db=mock_db_async,
            video_id=mock_video.id,
            status=ProcessingStatus.PENDING,
            processing_stages=None,  # Assuming default
            error_message=None,  # Assuming default
        )

        # DB commit is async
        mock_db_async.commit.assert_awaited_once()

        # BackgroundTasks.add_task is synchronous
        mock_background_tasks.add_task.assert_called_once_with(
            service._execute_processing_pipeline,  # Target function
            mock_job.id,  # args for the target function
            "gs://bucket/uploads/test-user-123/test_video.mp4",  # args for the target function
        )

    @patch("apps.core.services.video_processing_service.AsyncSessionLocal")
    async def test_execute_processing_pipeline_success(
        self,
        mock_AsyncSessionLocal: MagicMock,  # Patched AsyncSessionLocal factory
        service: VideoProcessingService,
        mock_dependencies: dict,
    ):
        """Test successful execution of video processing pipeline."""
        # Setup mock for the async context manager produced by AsyncSessionLocal()
        mock_db_async_cm = AsyncMock()  # This is the context manager object
        mock_db_async_session = AsyncMock(
            spec=AsyncSession
        )  # This is the session yielded by __aenter__
        mock_AsyncSessionLocal.return_value = mock_db_async_cm
        mock_db_async_cm.__aenter__.return_value = mock_db_async_session

        # Mock job and related objects
        mock_video = AsyncMock(spec=VideoModel)  # Use AsyncMock for spec consistency
        mock_video.original_filename = "test_video.mp4"
        mock_video.uploader_user_id = "test-user-123"

        mock_job = AsyncMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video  # Assuming direct attribute assignment for mock

        # job_repo.get_by_id is async
        mock_dependencies["job_repo"].get_by_id.return_value = mock_job

        # Mock file utilities (assuming these remain synchronous)
        mock_dependencies["file_utils"].create_temp_dir.return_value = "/tmp/test_dir"

        # Mock ffmpeg utilities (assuming sync)
        mock_dependencies["ffmpeg_utils"].get_video_metadata_sync.return_value = {
            "duration": 120.5,
            "resolution": "1920x1080",
            "format": "mp4",
        }

        # Mock AI adapter (methods are async)
        mock_dependencies[
            "ai_adapter"
        ].transcribe_audio.return_value = "This is a test transcript."
        mock_dependencies["ai_adapter"].generate_text.side_effect = [
            "Test Video Title",
            "Test video description.",
            "test, video, processing",
            "Show notes for the test video.",
        ]

        # Mock subtitle utils (assuming sync)
        mock_dependencies[
            "subtitle_utils"
        ].generate_vtt.return_value = (
            "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nThis is a test transcript."
        )
        mock_dependencies[
            "subtitle_utils"
        ].generate_srt.return_value = (
            "1\n00:00:00,000 --> 00:00:01,000\nThis is a test transcript."
        )

        # Mock storage.save_file (async)
        # Use a list for side_effect if called multiple times with different return values in sequence
        mock_dependencies["storage"].save_file.side_effect = [
            "gs://bucket/transcripts/test-user-123/transcript.txt",
            "gs://bucket/subtitles/test-user-123/subtitles.vtt",
            "gs://bucket/subtitles/test-user-123/subtitles.srt",
            "gs://bucket/thumbnails/test-user-123/thumbnail.jpg",
        ]

        mock_open = MagicMock()  # For patching builtins.open (sync)
        mock_file_content = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file_content
        mock_file_content.read.return_value = b"test thumbnail data"

        with patch("builtins.open", mock_open):
            await service._execute_processing_pipeline(
                42, "gs://bucket/uploads/test-user-123/test_video.mp4"
            )

        # --- Assertions ---

        # Step 0: Job status update to PROCESSING
        mock_dependencies["job_repo"].update_status.assert_any_await_with(
            mock_db_async_session, 42, ProcessingStatus.PROCESSING
        )

        # Step 1: Download video (if service._download_video is called and is async)
        # service._download_video might call storage.download_file_to_temp, which is async.
        # Assuming it's called, and storage.download_file_to_temp is the underlying async call.
        # This depends on the internal structure of _execute_processing_pipeline and _download_video.
        # For now, let's assume _download_video is called and it uses storage.download_file_to_temp.
        # If _download_video is a helper that orchestrates this, we might not mock storage.download directly here
        # unless _download_video itself is mocked. Given it's a private method, we test its effects.
        # The existing test doesn't mock/assert a download step explicitly other than file_utils.create_temp_dir.
        # So, we'll stick to what was previously being asserted or implied.
        mock_dependencies[
            "file_utils"
        ].create_temp_dir.assert_called_once()  # For local processing

        # Step 2: Metadata extraction (ffmpeg - sync)
        mock_dependencies["ffmpeg_utils"].get_video_metadata_sync.assert_called_once()
        mock_dependencies["metadata_repo"].create_or_update.assert_any_await_with(
            mock_db_async_session,
            42,
            extracted_video_duration_seconds=120.5,
            extracted_video_resolution="1920x1080",
            extracted_video_format="mp4",
        )

        # Step 3: Audio extraction (ffmpeg - sync) and transcription (AI - async)
        mock_dependencies[
            "ffmpeg_utils"
        ].extract_audio_sync.assert_called_once()  # Sync
        mock_dependencies["ai_adapter"].transcribe_audio.assert_awaited_once()  # Async
        #   Save transcript text (storage.save_file - async)
        mock_dependencies["storage"].save_file.assert_any_await_with(
            file_content="This is a test transcript.",
            filename="transcript.txt",
            subdir=f"transcripts/{mock_video.uploader_user_id}",
            content_type="text/plain",
        )
        mock_dependencies["metadata_repo"].create_or_update.assert_any_await_with(
            mock_db_async_session,
            42,
            transcript_text="This is a test transcript.",
            transcript_file_url="gs://bucket/transcripts/test-user-123/transcript.txt",  # From save_file side_effect
        )

        # Step 4: Content metadata generation (AI - async)
        assert mock_dependencies["ai_adapter"].generate_text.await_count == 4
        mock_dependencies["metadata_repo"].create_or_update.assert_any_await_with(
            mock_db_async_session,
            42,
            title="Test Video Title",
            description="Test video description.",
            tags=["test", "video", "processing"],
            # show_notes_text="Show notes for the test video.", # If this is a field
        )

        # Step 5: Subtitles generation (sync) and saving (async)
        mock_dependencies["subtitle_utils"].generate_vtt.assert_called_once()
        mock_dependencies["subtitle_utils"].generate_srt.assert_called_once()
        #   Save VTT (storage.save_file - async)
        mock_dependencies["storage"].save_file.assert_any_await_with(
            file_content="WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nThis is a test transcript.",
            filename="subtitles.vtt",
            subdir=f"subtitles/{mock_video.uploader_user_id}",
            content_type="text/vtt",
        )
        #   Save SRT (storage.save_file - async)
        mock_dependencies["storage"].save_file.assert_any_await_with(
            file_content="1\n00:00:00,000 --> 00:00:01,000\nThis is a test transcript.",
            filename="subtitles.srt",
            subdir=f"subtitles/{mock_video.uploader_user_id}",
            content_type="application/x-subrip",
        )
        mock_dependencies["metadata_repo"].create_or_update.assert_any_await_with(
            mock_db_async_session,
            42,
            subtitle_files_urls={
                "vtt": "gs://bucket/subtitles/test-user-123/subtitles.vtt",  # From save_file side_effect
                "srt": "gs://bucket/subtitles/test-user-123/subtitles.srt",  # From save_file side_effect
            },
        )

        # Step 6: Thumbnail extraction (ffmpeg - sync) and saving (async)
        # Assuming extract_frame_sync takes the local video path and output path
        # The exact args depend on how ffmpeg_utils.extract_frame_sync is structured.
        # Let's assume it takes an output path like "/tmp/test_dir/thumbnail.jpg"
        mock_dependencies["ffmpeg_utils"].extract_frame_sync.assert_called_once()
        #   Patching builtins.open was done to simulate reading this thumbnail file.
        #   Save thumbnail (storage.save_file - async)
        mock_dependencies["storage"].save_file.assert_any_await_with(
            file_content=b"test thumbnail data",  # From the mock_file.read.return_value
            filename="thumbnail.jpg",
            subdir=f"thumbnails/{mock_video.uploader_user_id}",
            content_type="image/jpeg",
        )
        mock_dependencies["metadata_repo"].create_or_update.assert_any_await_with(
            mock_db_async_session,
            42,
            thumbnail_file_url="gs://bucket/thumbnails/test-user-123/thumbnail.jpg",  # From save_file side_effect
        )

        # Final step: Mark job as completed
        mock_dependencies["job_repo"].update_status.assert_any_await_with(
            mock_db_async_session, 42, ProcessingStatus.COMPLETED
        )

        # DB Commit at the end of successful pipeline
        mock_db_async_session.commit.assert_awaited_once()

        # Cleanup local temp files (sync)
        mock_dependencies["file_utils"].remove_dir.assert_called_once_with(
            "/tmp/test_dir"
        )

    @patch("apps.core.services.video_processing_service.AsyncSessionLocal")
    async def test_execute_processing_pipeline_error(
        self,
        mock_AsyncSessionLocal: MagicMock,  # Patched AsyncSessionLocal factory
        service: VideoProcessingService,
        mock_dependencies: dict,
    ):
        """Test handling of errors in the processing pipeline."""
        # Setup mock for the async context manager produced by AsyncSessionLocal()
        mock_db_async_cm = AsyncMock()  # This is the context manager object
        mock_db_async_session = AsyncMock(
            spec=AsyncSession
        )  # This is the session yielded by __aenter__
        mock_AsyncSessionLocal.return_value = mock_db_async_cm
        mock_db_async_cm.__aenter__.return_value = mock_db_async_session

        # Mock job and related objects
        mock_video = AsyncMock(spec=VideoModel)
        mock_video.original_filename = "test_video.mp4"
        mock_video.uploader_user_id = "test-user-123"

        mock_job = AsyncMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video

        # job_repo.get_by_id is async
        mock_dependencies["job_repo"].get_by_id.return_value = mock_job

        # Mock file utilities
        mock_dependencies["file_utils"].create_temp_dir.return_value = "/tmp/test_dir"

        # Set up an error during processing
        mock_dependencies[
            "ffmpeg_utils"
        ].get_video_metadata_sync.side_effect = Exception("FFmpeg error")

        # Call the method
        await service._execute_processing_pipeline(
            42, "gs://bucket/uploads/test-user-123/test_video.mp4"
        )

        # Verify error handling
        mock_dependencies["job_repo"].update_status.assert_any_call(
            mock_db_async_session, 42, ProcessingStatus.FAILED
        )
        mock_dependencies["job_repo"].add_processing_stage.assert_awaited_once_with(
            mock_db_async_session, 42, "Error: FFmpeg error"
        )

        # Verify cleanup still happens
        mock_dependencies["file_utils"].remove_dir.assert_called_once_with(
            "/tmp/test_dir"
        )
        mock_db_async_session.commit.assert_awaited_once()

    @patch("apps.core.services.video_processing_service.AsyncSessionLocal")
    async def test_execute_processing_pipeline_job_not_found(
        self,
        mock_AsyncSessionLocal: MagicMock,
        service: VideoProcessingService,
        mock_dependencies: dict,
    ):
        """Test pipeline behavior when the initial job ID is not found."""
        mock_db_async_cm = AsyncMock()
        mock_db_async_session = AsyncMock(spec=AsyncSession)
        mock_AsyncSessionLocal.return_value = mock_db_async_cm
        mock_db_async_cm.__aenter__.return_value = mock_db_async_session

        # Simulate job_repo.get_by_id returning None
        mock_dependencies["job_repo"].get_by_id.return_value = None

        # Temp dir might still be created before job is fetched, or not, depending on service logic.
        # If it is, we need to mock its creation and assert its removal.
        temp_dir_path = "/tmp/job_not_found_dir"
        mock_dependencies["file_utils"].create_temp_dir.return_value = temp_dir_path

        job_id_not_found = 999
        video_url = "gs://bucket/uploads/some_video.mp4"

        await service._execute_processing_pipeline(job_id_not_found, video_url)

        # Verify that no processing steps were attempted if job not found early.
        # For example, ffmpeg_utils should not have been called.
        mock_dependencies["ffmpeg_utils"].extract_audio_sync.assert_not_called()
        mock_dependencies["ffmpeg_utils"].get_video_metadata_sync.assert_not_called()
        mock_dependencies["ai_adapter"].transcribe_audio.assert_not_awaited()

        # Verify no status updates were attempted for a non-existent job ID on job_repo.
        # If job_repo.update_status was called with job_id_not_found, it would likely fail or be a no-op.
        # We are checking that the service logic bails out before trying to update status.
        # Count calls to job_repo.update_status with specific non-existent job_id
        update_status_calls = [
            call_args
            for call_args in mock_dependencies["job_repo"].update_status.await_args_list
            if call_args[0][1] == job_id_not_found  # args[0] is db, args[1] is job_id
        ]
        assert len(update_status_calls) == 0

        # Check that commit/rollback were not called as no db changes should have been made related to this job.
        mock_db_async_session.commit.assert_not_awaited()
        mock_db_async_session.rollback.assert_not_awaited()

        # Check if temp dir cleanup was still called if it was created.
        # This depends on the service's try/finally structure for temp dir management.
        # If create_temp_dir is called regardless, remove_dir should also be called.
        if mock_dependencies["file_utils"].create_temp_dir.called:
            mock_dependencies["file_utils"].remove_dir.assert_called_once_with(
                temp_dir_path
            )
        else:
            mock_dependencies["file_utils"].remove_dir.assert_not_called()

    async def test_get_job_details_found(
        self,
        service: VideoProcessingService,
        mock_db_async: AsyncMock,
        mock_dependencies: dict,
    ):
        """Test retrieving job details when job exists and user is owner."""
        mock_video = AsyncMock(spec=VideoModel)
        mock_video.uploader_user_id = "test-user-123"

        mock_job = AsyncMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video  # Link video to job for uploader_user_id check

        mock_dependencies["job_repo"].get_by_id.return_value = mock_job

        result = await service.get_job_details(mock_db_async, 42, "test-user-123")

        assert result is mock_job
        mock_dependencies["job_repo"].get_by_id.assert_awaited_once_with(
            mock_db_async, 42
        )

    async def test_get_job_details_not_found(
        self,
        service: VideoProcessingService,
        mock_db_async: AsyncMock,
        mock_dependencies: dict,
    ):
        """Test retrieving job details when job does not exist."""
        mock_dependencies["job_repo"].get_by_id.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            await service.get_job_details(mock_db_async, 999, "test-user-123")

        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Job not found"
        mock_dependencies["job_repo"].get_by_id.assert_awaited_once_with(
            mock_db_async, 999
        )

    async def test_get_job_details_unauthorized(
        self,
        service: VideoProcessingService,
        mock_db_async: AsyncMock,
        mock_dependencies: dict,
    ):
        """Test retrieving job details when user is not the owner."""
        mock_video = AsyncMock(spec=VideoModel)
        mock_video.uploader_user_id = "other-user-456"  # Different owner

        mock_job = AsyncMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video

        mock_dependencies["job_repo"].get_by_id.return_value = mock_job

        with pytest.raises(HTTPException) as excinfo:
            await service.get_job_details(
                mock_db_async, 42, "test-user-123"
            )  # Current user is test-user-123

        assert (
            excinfo.value.status_code == 404
        )  # Or 403 Forbidden, depending on service logic
        # The original test asserted 404, so we keep it consistent.
        # A 403 might be more semantically correct if the job exists but user can't access.
        # However, often services return 404 to avoid revealing existence of a resource.
        assert excinfo.value.detail == "Job not found"
        mock_dependencies["job_repo"].get_by_id.assert_awaited_once_with(
            mock_db_async, 42
        )
