"""
Unit tests for the VideoProcessingService.
"""

import os
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest
from fastapi import BackgroundTasks, HTTPException

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
        "video_repo": MagicMock(),
        "job_repo": MagicMock(),
        "metadata_repo": MagicMock(),
        "storage": AsyncMock(),
        "ai_adapter": AsyncMock(),
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
def mock_db():
    """Mock SQLAlchemy Session."""
    return MagicMock()


@pytest.fixture
def mock_background_tasks():
    """Mock FastAPI BackgroundTasks."""
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
        service,
        mock_db,
        mock_background_tasks,
        mock_dependencies,
        sample_video_data,
    ):
        """Test initiating video processing pipeline."""
        # Set up mock returns
        mock_dependencies[
            "storage"
        ].save_file.return_value = "gs://bucket/uploads/test-user-123/test_video.mp4"

        mock_video = MagicMock(spec=VideoModel)
        mock_video.id = 1
        mock_dependencies["video_repo"].create.return_value = mock_video

        mock_job = MagicMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_dependencies["job_repo"].create.return_value = mock_job

        # Call the service method
        result = await service.initiate_video_processing(
            db=mock_db,
            **sample_video_data,
            background_tasks=mock_background_tasks,
        )

        # Verify results
        assert result is mock_job

        # Verify storage call
        mock_dependencies["storage"].save_file.assert_called_once_with(
            file_content=sample_video_data["video_content"],
            filename=sample_video_data["original_filename"],
            subdir=f"uploads/{sample_video_data['uploader_user_id']}",
        )

        # Verify video repository call
        mock_dependencies["video_repo"].create.assert_called_once_with(
            db=mock_db,
            uploader_user_id=sample_video_data["uploader_user_id"],
            original_filename=sample_video_data["original_filename"],
            storage_path="gs://bucket/uploads/test-user-123/test_video.mp4",
            content_type=sample_video_data["content_type"],
            size_bytes=len(sample_video_data["video_content"]),
        )

        # Verify job repository call
        mock_dependencies["job_repo"].create.assert_called_once_with(
            db=mock_db,
            video_id=mock_video.id,
            status=ProcessingStatus.PENDING,
            processing_stages=None,
            error_message=None,
        )

        # Verify DB commit
        mock_db.commit.assert_called_once()

        # Verify background task
        mock_background_tasks.add_task.assert_called_once_with(
            service._execute_processing_pipeline,
            mock_job.id,
            "gs://bucket/uploads/test-user-123/test_video.mp4",
        )

    @patch("apps.core.services.video_processing_service.get_db_session")
    async def test_execute_processing_pipeline_success(
        self, mock_get_db_session, service, mock_dependencies
    ):
        """Test successful execution of video processing pipeline."""
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db_session.return_value.__next__.return_value = mock_db

        # Mock job and related objects
        mock_video = MagicMock(spec=VideoModel)
        mock_video.original_filename = "test_video.mp4"
        mock_video.uploader_user_id = "test-user-123"

        mock_job = MagicMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video

        mock_dependencies["job_repo"].get_by_id.return_value = mock_job

        # Mock file utilities
        mock_dependencies["file_utils"].create_temp_dir.return_value = "/tmp/test_dir"

        # Mock ffmpeg utilities
        mock_dependencies["ffmpeg_utils"].get_video_metadata_sync.return_value = {
            "duration": 120.5,
            "resolution": "1920x1080",
            "format": "mp4",
        }

        # Mock AI adapter
        mock_dependencies[
            "ai_adapter"
        ].transcribe_audio.return_value = "This is a test transcript."
        mock_dependencies["ai_adapter"].generate_text.side_effect = [
            "Test Video Title",
            "Test video description.",
            "test, video, processing",
            "Show notes for the test video.",
        ]

        # Mock subtitle utils
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

        # Mock storage URLs
        mock_dependencies["storage"].save_file.side_effect = [
            "gs://bucket/transcripts/test-user-123/transcript.txt",
            "gs://bucket/subtitles/test-user-123/subtitles.vtt",
            "gs://bucket/subtitles/test-user-123/subtitles.srt",
            "gs://bucket/thumbnails/test-user-123/thumbnail.jpg",
        ]

        # Create a mock open to handle file operations
        mock_open = mock_open = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = b"test thumbnail data"

        # Call the method
        with patch("builtins.open", mock_open):
            await service._execute_processing_pipeline(
                42, "gs://bucket/uploads/test-user-123/test_video.mp4"
            )

        # Verify all steps executed in order

        # Step 0: Job status update
        mock_dependencies["job_repo"].update_status.assert_any_call(
            mock_db, 42, ProcessingStatus.PROCESSING
        )

        # Step 1: Metadata extraction
        mock_dependencies["ffmpeg_utils"].get_video_metadata_sync.assert_called_once()
        mock_dependencies["metadata_repo"].create_or_update.assert_any_call(
            mock_db,
            42,
            extracted_video_duration_seconds=120.5,
            extracted_video_resolution="1920x1080",
            extracted_video_format="mp4",
        )

        # Step 2 & 3: Audio extraction and transcription
        mock_dependencies["ffmpeg_utils"].extract_audio_sync.assert_called_once()
        mock_dependencies["ai_adapter"].transcribe_audio.assert_called_once()
        mock_dependencies["metadata_repo"].create_or_update.assert_any_call(
            mock_db,
            42,
            transcript_text="This is a test transcript.",
            transcript_file_url="gs://bucket/transcripts/test-user-123/transcript.txt",
        )

        # Step 4: Content metadata generation
        assert mock_dependencies["ai_adapter"].generate_text.call_count == 4
        mock_dependencies["metadata_repo"].create_or_update.assert_any_call(
            mock_db,
            42,
            title="Test Video Title",
            description="Test video description.",
            tags=["test", "video", "processing"],
            show_notes_text="Show notes for the test video.",
        )

        # Step 5: Subtitles generation
        mock_dependencies["subtitle_utils"].generate_vtt.assert_called_once()
        mock_dependencies["subtitle_utils"].generate_srt.assert_called_once()
        mock_dependencies["metadata_repo"].create_or_update.assert_any_call(
            mock_db,
            42,
            subtitle_files_urls={
                "vtt": "gs://bucket/subtitles/test-user-123/subtitles.vtt",
                "srt": "gs://bucket/subtitles/test-user-123/subtitles.srt",
            },
        )

        # Step 6: Thumbnail extraction
        mock_dependencies["ffmpeg_utils"].extract_frame_sync.assert_called_once()
        mock_dependencies["metadata_repo"].create_or_update.assert_any_call(
            mock_db,
            42,
            thumbnail_file_url="gs://bucket/thumbnails/test-user-123/thumbnail.jpg",
        )

        # Final step: Mark job as completed
        mock_dependencies["job_repo"].update_status.assert_any_call(
            mock_db, 42, ProcessingStatus.COMPLETED
        )

        # Verify cleanup
        mock_dependencies["file_utils"].cleanup_temp_dir.assert_called_once_with(
            "/tmp/test_dir"
        )
        mock_db.close.assert_called_once()

    @patch("apps.core.services.video_processing_service.get_db_session")
    async def test_execute_processing_pipeline_error(
        self, mock_get_db_session, service, mock_dependencies
    ):
        """Test handling of errors in the processing pipeline."""
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db_session.return_value.__next__.return_value = mock_db

        # Mock job and related objects
        mock_video = MagicMock(spec=VideoModel)
        mock_video.original_filename = "test_video.mp4"
        mock_video.uploader_user_id = "test-user-123"

        mock_job = MagicMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video

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
            mock_db, 42, ProcessingStatus.FAILED
        )
        mock_dependencies["job_repo"].add_processing_stage.assert_called_once_with(
            mock_db, 42, "Error: FFmpeg error"
        )

        # Verify cleanup still happens
        mock_dependencies["file_utils"].cleanup_temp_dir.assert_called_once_with(
            "/tmp/test_dir"
        )
        mock_db.close.assert_called_once()

    @patch("apps.core.services.video_processing_service.get_db_session")
    async def test_execute_processing_pipeline_job_not_found(
        self, mock_get_db_session, service, mock_dependencies
    ):
        """Test handling of job not found in the processing pipeline."""
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db_session.return_value.__next__.return_value = mock_db

        # Mock job not found
        mock_dependencies["job_repo"].get_by_id.return_value = None

        # Mock file utilities
        mock_dependencies["file_utils"].create_temp_dir.return_value = "/tmp/test_dir"

        # Call the method
        await service._execute_processing_pipeline(
            999, "gs://bucket/uploads/test-user-123/test_video.mp4"
        )

        # Verify error handling
        mock_dependencies["job_repo"].add_processing_stage.assert_called_once()
        assert (
            "Job 999 not found"
            in mock_dependencies["job_repo"].add_processing_stage.call_args[0][2]
        )

        # Verify cleanup still happens
        mock_dependencies["file_utils"].cleanup_temp_dir.assert_called_once_with(
            "/tmp/test_dir"
        )
        mock_db.close.assert_called_once()

    async def test_get_job_details_found(self, service, mock_db, mock_dependencies):
        """Test retrieving job details when job exists and user is owner."""
        # Setup mock job
        mock_video = MagicMock(spec=VideoModel)
        mock_video.uploader_user_id = "test-user-123"

        mock_job = MagicMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video

        mock_dependencies["job_repo"].get_by_id.return_value = mock_job

        # Call the method
        result = await service.get_job_details(mock_db, 42, "test-user-123")

        # Verify results
        assert result is mock_job
        mock_dependencies["job_repo"].get_by_id.assert_called_once_with(mock_db, 42)

    async def test_get_job_details_not_found(self, service, mock_db, mock_dependencies):
        """Test retrieving job details when job does not exist."""
        # Setup mock job not found
        mock_dependencies["job_repo"].get_by_id.return_value = None

        # Call the method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await service.get_job_details(mock_db, 999, "test-user-123")

        # Verify exception
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Job not found"
        mock_dependencies["job_repo"].get_by_id.assert_called_once_with(mock_db, 999)

    async def test_get_job_details_unauthorized(
        self, service, mock_db, mock_dependencies
    ):
        """Test retrieving job details when user is not the owner."""
        # Setup mock job with different owner
        mock_video = MagicMock(spec=VideoModel)
        mock_video.uploader_user_id = "other-user-456"

        mock_job = MagicMock(spec=VideoJobModel)
        mock_job.id = 42
        mock_job.video = mock_video

        mock_dependencies["job_repo"].get_by_id.return_value = mock_job

        # Call the method and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await service.get_job_details(mock_db, 42, "test-user-123")

        # Verify exception
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Job not found"
        mock_dependencies["job_repo"].get_by_id.assert_called_once_with(mock_db, 42)
