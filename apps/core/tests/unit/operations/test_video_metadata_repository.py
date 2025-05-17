"""
Unit tests for the VideoMetadataRepository.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from apps.core.models.video_metadata_model import VideoMetadataModel
from apps.core.operations.video_metadata_repository import VideoMetadataRepository


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
def sample_metadata_data():
    """Sample video metadata for testing."""
    return {
        "job_id": 42,
        "title": "Test Video Title",
        "description": "A test video description",
        "tags": ["test", "video", "unittest"],
        "transcript_text": "This is a test transcript.",
        "extracted_video_duration_seconds": 120.5,
        "extracted_video_resolution": "1920x1080",
    }


class TestVideoMetadataRepository:
    """Test cases for the VideoMetadataRepository class."""

    def test_create_new_metadata(self, mock_db_session, sample_metadata_data):
        """Test creating new metadata when none exists."""
        # Configure the mock to return None (no existing metadata)
        mock_db_session.query().filter().first.return_value = None

        # Call the repository method with a subset of fields
        metadata = VideoMetadataRepository.create_or_update(
            mock_db_session,
            job_id=sample_metadata_data["job_id"],
            title=sample_metadata_data["title"],
            description=sample_metadata_data["description"],
        )

        # Verify the metadata model was created correctly
        assert isinstance(metadata, VideoMetadataModel)
        assert metadata.job_id == sample_metadata_data["job_id"]
        assert metadata.title == sample_metadata_data["title"]
        assert metadata.description == sample_metadata_data["description"]

        # Verify other fields are None (not provided in create call)
        assert metadata.tags is None
        assert metadata.transcript_text is None

        # Verify the session operations
        mock_db_session.add.assert_called_once_with(metadata)
        mock_db_session.flush.assert_called_once()

    def test_update_existing_metadata(self, mock_db_session, sample_metadata_data):
        """Test updating existing metadata."""
        # Create a mock existing metadata
        existing_metadata = VideoMetadataModel(
            job_id=sample_metadata_data["job_id"],
            title="Old Title",
            description="Old Description",
        )

        # Configure the mock to return our existing metadata
        mock_db_session.query().filter().first.return_value = existing_metadata

        # Call the repository method with updated fields
        new_title = "Updated Title"
        new_tags = ["updated", "tags"]
        updated_metadata = VideoMetadataRepository.create_or_update(
            mock_db_session,
            job_id=sample_metadata_data["job_id"],
            title=new_title,
            tags=new_tags,
        )

        # Verify the metadata was updated correctly
        assert updated_metadata is existing_metadata  # Same object reference
        assert updated_metadata.title == new_title  # Updated field
        assert updated_metadata.tags == new_tags  # New field
        assert updated_metadata.description == "Old Description"  # Unchanged field

        # Verify the session operations
        mock_db_session.add.assert_not_called()  # No new object added
        mock_db_session.flush.assert_called_once()

    def test_update_multiple_fields(self, mock_db_session, sample_metadata_data):
        """Test updating multiple fields at once."""
        # Create a mock existing metadata with minimal fields
        existing_metadata = VideoMetadataModel(
            job_id=sample_metadata_data["job_id"],
        )

        # Configure the mock to return our existing metadata
        mock_db_session.query().filter().first.return_value = existing_metadata

        # Call the repository method with multiple fields
        updated_metadata = VideoMetadataRepository.create_or_update(
            mock_db_session,
            job_id=sample_metadata_data["job_id"],
            **sample_metadata_data,  # Update with all fields
        )

        # Verify all fields were updated correctly
        assert updated_metadata is existing_metadata  # Same object reference
        for key, value in sample_metadata_data.items():
            if key != "job_id":  # job_id shouldn't change
                assert getattr(updated_metadata, key) == value

        # Verify the session operations
        mock_db_session.flush.assert_called_once()

    def test_get_by_job_id_found(self, mock_db_session, sample_metadata_data):
        """Test retrieving metadata by job_id when it exists."""
        # Create a mock metadata to be returned
        mock_metadata = VideoMetadataModel(**sample_metadata_data)

        # Configure the mock to return our metadata
        mock_db_session.query().filter().first.return_value = mock_metadata

        # Call the repository method
        metadata = VideoMetadataRepository.get_by_job_id(
            mock_db_session, sample_metadata_data["job_id"]
        )

        # Verify the result
        assert metadata is mock_metadata
        assert metadata.job_id == sample_metadata_data["job_id"]

        # Verify correct query was constructed
        mock_db_session.query.assert_called_once_with(VideoMetadataModel)
        mock_db_session.query().filter.assert_called_once()

    def test_get_by_job_id_not_found(self, mock_db_session):
        """Test retrieving metadata by job_id when it doesn't exist."""
        # Configure the mock to return None
        mock_db_session.query().filter().first.return_value = None

        # Call the repository method
        metadata = VideoMetadataRepository.get_by_job_id(mock_db_session, 999)

        # Verify the result
        assert metadata is None

        # Verify correct query was constructed
        mock_db_session.query.assert_called_once_with(VideoMetadataModel)
        mock_db_session.query().filter.assert_called_once()

    def test_create_with_empty_kwargs(self, mock_db_session):
        """Test creating metadata with only job_id."""
        # Configure the mock to return None (no existing metadata)
        mock_db_session.query().filter().first.return_value = None

        # Call the repository method with only job_id
        metadata = VideoMetadataRepository.create_or_update(
            mock_db_session,
            job_id=123,
        )

        # Verify the metadata model was created correctly
        assert isinstance(metadata, VideoMetadataModel)
        assert metadata.job_id == 123
        assert metadata.title is None
        assert metadata.description is None
        assert metadata.tags is None

        # Verify the session operations
        mock_db_session.add.assert_called_once_with(metadata)
        mock_db_session.flush.assert_called_once()
