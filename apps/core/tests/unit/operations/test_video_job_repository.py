"""
Unit tests for the VideoJobRepository.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.operations.video_job_repository import VideoJobRepository


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
def sample_job_data():
    """Sample video job data for testing."""
    return {
        "video_id": 42,
        "status": ProcessingStatus.PENDING,
        "processing_stages": [],
        "error_message": None,
    }


class TestVideoJobRepository:
    """Test cases for the VideoJobRepository class."""

    def test_create(self, mock_db_session, sample_job_data):
        """Test creating a new video job."""
        # Call the repository method
        job = VideoJobRepository.create(
            mock_db_session,
            video_id=sample_job_data["video_id"],
            status=sample_job_data["status"],
            processing_stages=sample_job_data["processing_stages"],
            error_message=sample_job_data["error_message"],
        )

        # Verify the job model was created correctly
        assert isinstance(job, VideoJobModel)
        assert job.video_id == sample_job_data["video_id"]
        assert job.status == sample_job_data["status"]
        assert job.processing_stages == sample_job_data["processing_stages"]
        assert job.error_message == sample_job_data["error_message"]

        # Verify the session operations
        mock_db_session.add.assert_called_once_with(job)
        mock_db_session.flush.assert_called_once()

    def test_create_with_defaults(self, mock_db_session):
        """Test creating a job with default values."""
        # Call with minimal required parameters
        job = VideoJobRepository.create(mock_db_session, video_id=42)

        # Verify defaults were applied
        assert isinstance(job, VideoJobModel)
        assert job.video_id == 42
        assert job.status == ProcessingStatus.PENDING
        assert job.processing_stages is None
        assert job.error_message is None

        # Verify the session operations
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    def test_get_by_id_found(self, mock_db_session, sample_job_data):
        """Test retrieving a job by ID when it exists."""
        # Create a mock job model to be returned
        mock_job = VideoJobModel(**sample_job_data)
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        job = VideoJobRepository.get_by_id(mock_db_session, 123)

        # Verify the result
        assert job is mock_job
        assert job.id == 123

        # Verify correct query was constructed
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.query().filter.assert_called_once()

    def test_get_by_id_not_found(self, mock_db_session):
        """Test retrieving a job by ID when it doesn't exist."""
        # Configure the mock to return None
        mock_db_session.query().filter().first.return_value = None

        # Call the repository method
        job = VideoJobRepository.get_by_id(mock_db_session, 999)

        # Verify the result
        assert job is None

        # Verify correct query was constructed
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.query().filter.assert_called_once()

    def test_update_status(self, mock_db_session, sample_job_data):
        """Test updating a job's status."""
        # Create a mock job model to be returned
        mock_job = VideoJobModel(**sample_job_data)
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        updated_job = VideoJobRepository.update_status(
            mock_db_session, 123, ProcessingStatus.PROCESSING
        )

        # Verify the result
        assert updated_job is mock_job
        assert updated_job.status == ProcessingStatus.PROCESSING
        assert updated_job.error_message is None  # No change

        # Verify correct query and session operations
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_called_once()

    def test_update_status_with_error(self, mock_db_session, sample_job_data):
        """Test updating a job's status with an error message."""
        # Create a mock job model to be returned
        mock_job = VideoJobModel(**sample_job_data)
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        error_msg = "Something went wrong"
        updated_job = VideoJobRepository.update_status(
            mock_db_session, 123, ProcessingStatus.FAILED, error_message=error_msg
        )

        # Verify the result
        assert updated_job is mock_job
        assert updated_job.status == ProcessingStatus.FAILED
        assert updated_job.error_message == error_msg

        # Verify correct query and session operations
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_called_once()

    def test_update_status_not_found(self, mock_db_session):
        """Test updating status when job doesn't exist."""
        # Configure the mock to return None
        mock_db_session.query().filter().first.return_value = None

        # Call the repository method
        updated_job = VideoJobRepository.update_status(
            mock_db_session, 999, ProcessingStatus.PROCESSING
        )

        # Verify the result
        assert updated_job is None

        # Verify correct query was constructed and flush not called
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_not_called()

    def test_add_processing_stage_new_list(self, mock_db_session):
        """Test adding a processing stage to a job with no existing stages."""
        # Create a mock job with no processing stages
        mock_job = VideoJobModel(video_id=42, processing_stages=None)
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        stage = "transcription_started"
        updated_job = VideoJobRepository.add_processing_stage(
            mock_db_session, 123, stage
        )

        # Verify the result
        assert updated_job is mock_job
        assert updated_job.processing_stages == [stage]

        # Verify correct query and session operations
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_called_once()

    def test_add_processing_stage_existing_list(self, mock_db_session):
        """Test adding a processing stage to a job with existing stages."""
        # Create a mock job with existing processing stages
        existing_stages = ["upload_complete", "validation_complete"]
        mock_job = VideoJobModel(video_id=42, processing_stages=existing_stages)
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        new_stage = "transcription_started"
        updated_job = VideoJobRepository.add_processing_stage(
            mock_db_session, 123, new_stage
        )

        # Verify the result
        assert updated_job is mock_job
        assert updated_job.processing_stages == existing_stages + [new_stage]

        # Verify correct query and session operations
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_called_once()

    def test_add_processing_stage_json_string(self, mock_db_session):
        """Test adding a processing stage when stages are stored as a JSON string."""
        # Create a mock job with processing stages as JSON string
        existing_stages = json.dumps(["upload_complete"])
        mock_job = VideoJobModel(video_id=42, processing_stages=existing_stages)
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        new_stage = "validation_complete"
        updated_job = VideoJobRepository.add_processing_stage(
            mock_db_session, 123, new_stage
        )

        # Verify the result
        assert updated_job is mock_job
        assert updated_job.processing_stages == ["upload_complete", new_stage]

        # Verify correct query and session operations
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_called_once()

    def test_add_processing_stage_invalid_json(self, mock_db_session):
        """Test adding a processing stage when stages contain invalid JSON."""
        # Create a mock job with invalid JSON string
        mock_job = VideoJobModel(video_id=42, processing_stages="{invalid json")
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        new_stage = "validation_complete"
        updated_job = VideoJobRepository.add_processing_stage(
            mock_db_session, 123, new_stage
        )

        # Verify the result
        assert updated_job is mock_job
        assert updated_job.processing_stages == [new_stage]  # Should start fresh list

        # Verify correct query and session operations
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_called_once()

    def test_add_processing_stage_not_found(self, mock_db_session):
        """Test adding a processing stage when job doesn't exist."""
        # Configure the mock to return None
        mock_db_session.query().filter().first.return_value = None

        # Call the repository method
        updated_job = VideoJobRepository.add_processing_stage(
            mock_db_session, 999, "transcription_started"
        )

        # Verify the result
        assert updated_job is None

        # Verify correct query was constructed and flush not called
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_not_called()

    def test_add_processing_stage_non_list_object(self, mock_db_session):
        """Test adding a processing stage when stages are a non-list object."""
        # Create a mock job with non-list object for stages
        mock_job = VideoJobModel(video_id=42, processing_stages={"key": "value"})
        mock_job.id = 123

        # Configure the mock to return our job
        mock_db_session.query().filter().first.return_value = mock_job

        # Call the repository method
        new_stage = "transcription_started"
        updated_job = VideoJobRepository.add_processing_stage(
            mock_db_session, 123, new_stage
        )

        # Verify the result
        assert updated_job is mock_job
        assert updated_job.processing_stages == [new_stage]  # Should create new list

        # Verify correct query and session operations
        mock_db_session.query.assert_called_once_with(VideoJobModel)
        mock_db_session.flush.assert_called_once()
