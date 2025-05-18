"""
Unit tests for the VideoMetadataRepository.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.models.video_metadata_model import VideoMetadataModel
from apps.core.operations.video_metadata_repository import VideoMetadataRepository


@pytest.fixture
def mock_db_session_async() -> AsyncMock:
    """Create a mock SQLAlchemy AsyncSession."""
    mock_session = AsyncMock(spec=AsyncSession)
    # Specific chain setup (execute, scalars, first) will be done in tests as needed.
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

    @pytest.mark.asyncio
    async def test_create_new_metadata(
        self, mock_db_session_async: AsyncMock, sample_metadata_data
    ):
        """Test creating new metadata when none exists."""
        # Configure the mock for the internal get_by_job_id call to return None
        mock_execute_result_get = AsyncMock()
        mock_scalars_result_get = AsyncMock()
        mock_db_session_async.execute.return_value = (
            mock_execute_result_get  # This will be for the get call
        )
        mock_execute_result_get.scalars.return_value = mock_scalars_result_get
        mock_scalars_result_get.first.return_value = None  # Simulate metadata not found

        # Call the repository method (which is now async)
        metadata = await VideoMetadataRepository.create_or_update(
            mock_db_session_async,  # Use the async mock session
            job_id=sample_metadata_data["job_id"],
            title=sample_metadata_data["title"],
            description=sample_metadata_data["description"],
        )

        # Verify the metadata model was created correctly
        assert isinstance(metadata, VideoMetadataModel)
        assert metadata.job_id == sample_metadata_data["job_id"]
        assert metadata.title == sample_metadata_data["title"]
        assert metadata.description == sample_metadata_data["description"]
        assert metadata.tags is None  # Not provided in this call
        assert metadata.transcript_text is None  # Not provided

        # Verify session operations
        # execute was called once for the initial get_by_job_id check
        mock_db_session_async.execute.assert_awaited_once()
        mock_db_session_async.add.assert_called_once()  # metadata instance passed to add
        mock_db_session_async.flush.assert_awaited_once()
        # Assuming create_or_update also refreshes the new instance
        mock_db_session_async.refresh.assert_awaited_once_with(metadata)

    @pytest.mark.asyncio
    async def test_update_existing_metadata(
        self, mock_db_session_async: AsyncMock, sample_metadata_data
    ):
        """Test updating existing metadata."""
        existing_metadata_instance = VideoMetadataModel(
            job_id=sample_metadata_data["job_id"],
            title="Old Title",
            description="Old Description",
        )

        # Configure the mock for the internal get_by_job_id call to return existing_metadata_instance
        mock_execute_result_get = AsyncMock()
        mock_scalars_result_get = AsyncMock()
        # Reset execute mock if it's the same instance from a previous test/setup in a class
        # For function-scoped mock_db_session_async, it's a fresh mock each time.
        mock_db_session_async.execute.return_value = mock_execute_result_get
        mock_execute_result_get.scalars.return_value = mock_scalars_result_get
        mock_scalars_result_get.first.return_value = existing_metadata_instance

        new_title = "Updated Title"
        new_tags = ["updated", "tags"]
        updated_metadata = await VideoMetadataRepository.create_or_update(
            mock_db_session_async,
            job_id=sample_metadata_data["job_id"],
            title=new_title,
            tags=new_tags,
        )

        # Verify the metadata was updated correctly
        assert updated_metadata is existing_metadata_instance
        assert updated_metadata.title == new_title
        assert updated_metadata.tags == new_tags
        assert updated_metadata.description == "Old Description"  # Unchanged

        # Verify session operations
        mock_db_session_async.execute.assert_awaited_once()  # For get_by_job_id
        mock_db_session_async.add.assert_not_called()  # No new object added
        mock_db_session_async.flush.assert_awaited_once()
        mock_db_session_async.refresh.assert_awaited_once_with(
            existing_metadata_instance
        )

    @pytest.mark.asyncio
    async def test_update_multiple_fields(
        self, mock_db_session_async: AsyncMock, sample_metadata_data
    ):
        """Test updating multiple fields at once."""
        existing_metadata_instance = VideoMetadataModel(
            job_id=sample_metadata_data["job_id"],
        )

        # Mock the internal get_by_job_id call
        mock_execute_result_get = AsyncMock()
        mock_scalars_result_get = AsyncMock()
        mock_db_session_async.execute.return_value = mock_execute_result_get
        mock_execute_result_get.scalars.return_value = mock_scalars_result_get
        mock_scalars_result_get.first.return_value = existing_metadata_instance

        # Call the repository method with multiple fields
        updated_metadata = await VideoMetadataRepository.create_or_update(
            mock_db_session_async,
            job_id=sample_metadata_data["job_id"],
            **sample_metadata_data,  # Update with all fields from the fixture
        )

        assert updated_metadata is existing_metadata_instance
        for key, value in sample_metadata_data.items():
            # job_id is part of the key for lookup, not an updatable field by kwargs in this manner usually
            # if key != "job_id":
            # The create_or_update likely iterates through kwargs and sets them.
            assert getattr(updated_metadata, key) == value

        mock_db_session_async.execute.assert_awaited_once()
        mock_db_session_async.add.assert_not_called()
        mock_db_session_async.flush.assert_awaited_once()
        mock_db_session_async.refresh.assert_awaited_once_with(
            existing_metadata_instance
        )

    @pytest.mark.asyncio
    async def test_get_by_job_id_found(
        self, mock_db_session_async: AsyncMock, sample_metadata_data
    ):
        """Test retrieving metadata by job_id when it exists."""
        mock_metadata_instance = VideoMetadataModel(**sample_metadata_data)  # type: ignore

        mock_execute_result = AsyncMock()
        mock_scalars_result = AsyncMock()
        mock_db_session_async.execute.return_value = mock_execute_result
        mock_execute_result.scalars.return_value = mock_scalars_result
        mock_scalars_result.first.return_value = mock_metadata_instance

        metadata = await VideoMetadataRepository.get_by_job_id(
            mock_db_session_async, sample_metadata_data["job_id"]
        )

        assert metadata is mock_metadata_instance
        if metadata:  # Guard for linter
            assert metadata.job_id == sample_metadata_data["job_id"]

        mock_db_session_async.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_job_id_not_found(self, mock_db_session_async: AsyncMock):
        """Test retrieving metadata by job_id when it doesn't exist."""
        mock_execute_result = AsyncMock()
        mock_scalars_result = AsyncMock()
        mock_db_session_async.execute.return_value = mock_execute_result
        mock_execute_result.scalars.return_value = mock_scalars_result
        mock_scalars_result.first.return_value = None  # Simulate not found

        metadata = await VideoMetadataRepository.get_by_job_id(
            mock_db_session_async, 999
        )

        assert metadata is None
        mock_db_session_async.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_with_empty_kwargs(self, mock_db_session_async: AsyncMock):
        """Test creating metadata with only job_id."""
        # Mock the internal get_by_job_id call to return None
        mock_execute_result_get = AsyncMock()
        mock_scalars_result_get = AsyncMock()
        mock_db_session_async.execute.return_value = mock_execute_result_get
        mock_execute_result_get.scalars.return_value = mock_scalars_result_get
        mock_scalars_result_get.first.return_value = None  # No existing metadata

        job_id_val = 123
        metadata = await VideoMetadataRepository.create_or_update(
            mock_db_session_async,
            job_id=job_id_val,
            # No other kwargs passed
        )

        assert isinstance(metadata, VideoMetadataModel)
        if metadata:  # Guard for linter
            assert metadata.job_id == job_id_val
            assert metadata.title is None
            assert metadata.description is None
            assert metadata.tags is None

        mock_db_session_async.execute.assert_awaited_once()
        mock_db_session_async.add.assert_called_once()  # With the new metadata instance
        mock_db_session_async.flush.assert_awaited_once()
        if metadata:  # metadata will not be None here due to creation path
            mock_db_session_async.refresh.assert_awaited_once_with(metadata)
