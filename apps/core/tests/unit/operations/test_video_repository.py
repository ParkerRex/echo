"""
Unit tests for the VideoRepository.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.models.video_model import VideoModel
from apps.core.operations.video_repository import VideoRepository


@pytest.fixture
def mock_db_session_async() -> AsyncMock:
    """Create a mock SQLAlchemy AsyncSession."""
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def sample_video_data():
    """Sample video data for testing."""
    return {
        "uploader_user_id": "test-user-123",
        "original_filename": "test_video.mp4",
        "storage_path": "uploads/test-user-123/abc123.mp4",
        "content_type": "video/mp4",
        "size_bytes": 1024000,
    }


class TestVideoRepository:
    """Test cases for the VideoRepository class."""

    @pytest.mark.asyncio
    async def test_create(self, mock_db_session_async: AsyncMock, sample_video_data):
        """Test creating a new video."""
        video = await VideoRepository.create(mock_db_session_async, **sample_video_data)

        assert isinstance(video, VideoModel)
        assert video.uploader_user_id == sample_video_data["uploader_user_id"]
        assert video.original_filename == sample_video_data["original_filename"]
        assert video.storage_path == sample_video_data["storage_path"]
        assert video.content_type == sample_video_data["content_type"]
        assert video.size_bytes == sample_video_data["size_bytes"]

        mock_db_session_async.add.assert_called_once_with(video)
        mock_db_session_async.flush.assert_awaited_once()
        mock_db_session_async.refresh.assert_awaited_once_with(video)

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, mock_db_session_async: AsyncMock, sample_video_data
    ):
        """Test retrieving a video by ID when it exists."""
        mock_video_instance = VideoModel(**sample_video_data)
        mock_video_instance.id = 123

        mock_execute_result = AsyncMock()
        mock_scalars_result = AsyncMock()
        mock_db_session_async.execute.return_value = mock_execute_result
        mock_execute_result.scalars.return_value = mock_scalars_result
        mock_scalars_result.first.return_value = mock_video_instance

        video = await VideoRepository.get_by_id(mock_db_session_async, 123)

        assert video is mock_video_instance
        if video:
            assert video.id == 123
        mock_db_session_async.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_db_session_async: AsyncMock):
        """Test retrieving a video by ID when it doesn't exist."""
        mock_execute_result = AsyncMock()
        mock_scalars_result = AsyncMock()
        mock_db_session_async.execute.return_value = mock_execute_result
        mock_execute_result.scalars.return_value = mock_scalars_result
        mock_scalars_result.first.return_value = None

        video = await VideoRepository.get_by_id(mock_db_session_async, 999)

        assert video is None
        mock_db_session_async.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_db_error_handling(
        self, mock_db_session_async: AsyncMock, sample_video_data
    ):
        """Test handling of database errors during create's flush."""
        mock_db_session_async.flush = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(Exception) as excinfo:
            await VideoRepository.create(mock_db_session_async, **sample_video_data)

        assert "Database error" in str(excinfo.value)
        mock_db_session_async.add.assert_called_once()
        mock_db_session_async.flush.assert_awaited_once()
