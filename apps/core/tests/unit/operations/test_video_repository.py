"""
Unit tests for the VideoRepository.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from apps.core.models.video_model import VideoModel
from apps.core.operations.video_repository import VideoRepository


@pytest.fixture
def mock_db_session():
    """Create a mock SQLAlchemy database session."""
    mock_session = MagicMock(spec=Session)

    # Mock the query builder
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query

    # Mock the filter
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter

    # Mock first()
    mock_filter.first.return_value = None

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

    def test_create(self, mock_db_session, sample_video_data):
        """Test creating a new video."""
        # Call the repository method
        video = VideoRepository.create(mock_db_session, **sample_video_data)

        # Verify the video model was created correctly
        assert isinstance(video, VideoModel)
        assert video.uploader_user_id == sample_video_data["uploader_user_id"]
        assert video.original_filename == sample_video_data["original_filename"]
        assert video.storage_path == sample_video_data["storage_path"]
        assert video.content_type == sample_video_data["content_type"]
        assert video.size_bytes == sample_video_data["size_bytes"]

        # Verify the session operations
        mock_db_session.add.assert_called_once_with(video)
        mock_db_session.flush.assert_called_once()

    def test_get_by_id_found(self, mock_db_session, sample_video_data):
        """Test retrieving a video by ID when it exists."""
        # Create a mock video model to be returned
        mock_video = VideoModel(**sample_video_data)
        mock_video.id = 123

        # Configure the mock to return our video
        mock_db_session.query().filter().first.return_value = mock_video

        # Call the repository method
        video = VideoRepository.get_by_id(mock_db_session, 123)

        # Verify the result
        assert video is mock_video
        assert video.id == 123

        # Verify correct query was constructed
        mock_db_session.query.assert_called_once_with(VideoModel)
        mock_db_session.query().filter.assert_called_once()  # Hard to test exact filter

    def test_get_by_id_not_found(self, mock_db_session):
        """Test retrieving a video by ID when it doesn't exist."""
        # Configure the mock to return None
        mock_db_session.query().filter().first.return_value = None

        # Call the repository method
        video = VideoRepository.get_by_id(mock_db_session, 999)

        # Verify the result
        assert video is None

        # Verify correct query was constructed
        mock_db_session.query.assert_called_once_with(VideoModel)
        mock_db_session.query().filter.assert_called_once()

    def test_db_error_handling(self, mock_db_session, sample_video_data):
        """Test handling of database errors."""
        # Configure the mock to raise an exception during flush
        mock_db_session.flush.side_effect = Exception("Database error")

        # Call the repository method and expect the exception to propagate
        with pytest.raises(Exception) as excinfo:
            VideoRepository.create(mock_db_session, **sample_video_data)

        # Verify the error message
        assert "Database error" in str(excinfo.value)

        # Verify the session operations
        mock_db_session.add.assert_called_once()  # Video was added
        mock_db_session.flush.assert_called_once()  # Flush was attempted
