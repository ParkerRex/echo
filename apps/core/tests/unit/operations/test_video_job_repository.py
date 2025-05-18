"""
Unit tests for the VideoJobRepository.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.operations.video_job_repository import VideoJobRepository


@pytest.fixture
def mock_db_session_async() -> AsyncMock:
    """Create a mock SQLAlchemy AsyncSession."""
    mock_session = AsyncMock(spec=AsyncSession)

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

    @pytest.mark.asyncio
    async def test_create(self, mock_db_session_async: AsyncMock, sample_job_data):
        """Test creating a new video job."""
        job = await VideoJobRepository.create(
            mock_db_session_async,
            video_id=sample_job_data["video_id"],
            status=sample_job_data["status"],
        )

        assert isinstance(job, VideoJobModel)
        assert job.video_id == sample_job_data["video_id"]
        assert job.status == sample_job_data["status"]

        mock_db_session_async.add.assert_called_once()
        mock_db_session_async.flush.assert_awaited_once()
        mock_db_session_async.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_with_defaults(self, mock_db_session_async: AsyncMock):
        """Test creating a job with default values."""
        job = await VideoJobRepository.create(mock_db_session_async, video_id=42)

        assert isinstance(job, VideoJobModel)
        assert job.video_id == 42
        assert job.status == ProcessingStatus.PENDING

        mock_db_session_async.add.assert_called_once()
        mock_db_session_async.flush.assert_awaited_once()
        mock_db_session_async.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, mock_db_session_async: AsyncMock, sample_job_data
    ):
        """Test retrieving a job by ID when it exists."""
        mock_job_instance = VideoJobModel(**sample_job_data)
        mock_job_instance.id = 123

        mock_execute_result = AsyncMock()
        mock_scalars_result = AsyncMock()

        mock_db_session_async.execute.return_value = mock_execute_result
        mock_execute_result.scalars.return_value = mock_scalars_result
        mock_scalars_result.first.return_value = mock_job_instance

        job = await VideoJobRepository.get_by_id(mock_db_session_async, 123)

        assert job is mock_job_instance
        assert job.id == 123
        mock_db_session_async.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_db_session_async: AsyncMock):
        """Test retrieving a job by ID when it doesn't exist."""
        mock_execute_result = AsyncMock()
        mock_scalars_result = AsyncMock()

        mock_db_session_async.execute.return_value = mock_execute_result
        mock_execute_result.scalars.return_value = mock_scalars_result
        mock_scalars_result.first.return_value = None

        job = await VideoJobRepository.get_by_id(mock_db_session_async, 999)

        assert job is None
        mock_db_session_async.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_status(
        self, mock_db_session_async: AsyncMock, sample_job_data
    ):
        """Test updating a job's status."""
        mock_job_to_update = VideoJobModel(**sample_job_data)  # type: ignore
        mock_job_to_update.id = 123

        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = mock_job_to_update

            updated_job = await VideoJobRepository.update_status(
                mock_db_session_async, 123, ProcessingStatus.PROCESSING
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 123)
            assert updated_job is not None  # Explicitly assert not None
            if updated_job:  # Guard subsequent attribute access
                assert updated_job is mock_job_to_update
                assert updated_job.status == ProcessingStatus.PROCESSING
                assert updated_job.error_message is None

            mock_db_session_async.flush.assert_awaited_once()
            # Ensure refresh is called with the object that get_by_id returned (which is mock_job_to_update)
            mock_db_session_async.refresh.assert_awaited_once_with(mock_job_to_update)

    @pytest.mark.asyncio
    async def test_update_status_with_error(
        self, mock_db_session_async: AsyncMock, sample_job_data
    ):
        """Test updating a job's status with an error message."""
        mock_job_to_update = VideoJobModel(**sample_job_data)  # type: ignore
        mock_job_to_update.id = 123

        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = mock_job_to_update

            error_msg = "Something went wrong"
            updated_job = await VideoJobRepository.update_status(
                mock_db_session_async,
                123,
                ProcessingStatus.FAILED,
                error_message=error_msg,
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 123)
            assert updated_job is not None  # Explicitly assert not None
            if updated_job:  # Guard subsequent attribute access
                assert updated_job is mock_job_to_update
                assert updated_job.status == ProcessingStatus.FAILED
                assert updated_job.error_message == error_msg

            mock_db_session_async.flush.assert_awaited_once()
            mock_db_session_async.refresh.assert_awaited_once_with(mock_job_to_update)

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, mock_db_session_async: AsyncMock):
        """Test updating status when job doesn't exist."""
        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = None  # Simulate job not found

            updated_job = await VideoJobRepository.update_status(
                mock_db_session_async, 999, ProcessingStatus.PROCESSING
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 999)
            assert updated_job is None
            assert mock_db_session_async.flush.await_count == 0
            assert mock_db_session_async.refresh.await_count == 0

    @pytest.mark.asyncio
    async def test_add_processing_stage_new_list(
        self, mock_db_session_async: AsyncMock
    ):
        """Test adding a processing stage to a job with no existing stages."""
        mock_job = VideoJobModel(video_id=42, processing_stages=None)  # type: ignore
        mock_job.id = 123

        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = mock_job

            stage = "transcription_started"
            updated_job = await VideoJobRepository.add_processing_stage(
                mock_db_session_async, 123, stage
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 123)
            assert updated_job is not None
            if updated_job:
                assert updated_job is mock_job
                # The repository method should handle initializing the list
                assert updated_job.processing_stages == [stage]

            mock_db_session_async.flush.assert_awaited_once()
            mock_db_session_async.refresh.assert_awaited_once_with(mock_job)

    @pytest.mark.asyncio
    async def test_add_processing_stage_existing_list(
        self, mock_db_session_async: AsyncMock
    ):
        """Test adding a processing stage to a job with existing stages."""
        existing_stages = ["upload_complete", "validation_complete"]
        mock_job = VideoJobModel(video_id=42, processing_stages=existing_stages)  # type: ignore
        mock_job.id = 123

        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = mock_job

            new_stage = "transcription_started"
            updated_job = await VideoJobRepository.add_processing_stage(
                mock_db_session_async, 123, new_stage
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 123)
            assert updated_job is not None
            if updated_job:
                assert updated_job is mock_job  # The same instance is modified
                assert updated_job.processing_stages == existing_stages + [new_stage]

            mock_db_session_async.flush.assert_awaited_once()
            mock_db_session_async.refresh.assert_awaited_once_with(mock_job)

    @pytest.mark.asyncio
    async def test_add_processing_stage_json_string(
        self, mock_db_session_async: AsyncMock
    ):
        """Test adding a processing stage when stages are stored as a JSON string."""
        existing_stages_json = json.dumps(["upload_complete"])
        # Ensure the mock_job.processing_stages is set as if read from DB (i.e., already a string)
        mock_job = VideoJobModel(video_id=42, processing_stages=existing_stages_json)  # type: ignore
        mock_job.id = 123

        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = mock_job

            new_stage = "validation_complete"
            updated_job = await VideoJobRepository.add_processing_stage(
                mock_db_session_async, 123, new_stage
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 123)
            assert updated_job is not None
            if updated_job:  # Guard attribute access
                assert updated_job is mock_job
                # The repository method should deserialize, append, and reserialize (or store as list if column type allows)
                # Assuming the repository method correctly handles JSON string to list conversion and back, or stores as Python list directly.
                # If it stores as Python list, then this assertion is fine.
                # If it converts back to JSON string, this assertion needs to change.
                # Based on VideoJobModel.processing_stages being potentially `JSON` type which SQLAlchemy handles,
                # it likely becomes a Python list in the model instance after load/modification.
                current_stages = json.loads(
                    existing_stages_json
                )  # Before adding new_stage
                current_stages.append(new_stage)
                assert updated_job.processing_stages == current_stages

            mock_db_session_async.flush.assert_awaited_once()
            mock_db_session_async.refresh.assert_awaited_once_with(mock_job)

    @pytest.mark.asyncio
    async def test_add_processing_stage_invalid_json(
        self, mock_db_session_async: AsyncMock
    ):
        """Test adding a stage when processing_stages is an invalid JSON string."""
        mock_job = VideoJobModel(video_id=42, processing_stages="not_a_valid_json[")  # type: ignore
        mock_job.id = 123

        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = mock_job

            new_stage = "validation_complete"
            # Depending on how add_processing_stage handles json.JSONDecodeError,
            # this might raise an exception, or log an error and initialize stages to [new_stage].
            # For this test, let's assume it logs error and initializes a new list.
            # If it's expected to raise, use pytest.raises.
            updated_job = await VideoJobRepository.add_processing_stage(
                mock_db_session_async, 123, new_stage
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 123)
            assert updated_job is not None
            if updated_job:
                assert updated_job is mock_job
                # Assuming repository initializes to [new_stage] on JSON error
                assert updated_job.processing_stages == [new_stage]

            mock_db_session_async.flush.assert_awaited_once()
            mock_db_session_async.refresh.assert_awaited_once_with(mock_job)

    @pytest.mark.asyncio
    async def test_add_processing_stage_not_found(
        self, mock_db_session_async: AsyncMock
    ):
        """Test adding a processing stage when the job doesn't exist."""
        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = None  # Simulate job not found

            new_stage = "transcription_started"
            updated_job = await VideoJobRepository.add_processing_stage(
                mock_db_session_async, 999, new_stage
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 999)
            assert updated_job is None
            assert mock_db_session_async.flush.await_count == 0
            assert mock_db_session_async.refresh.await_count == 0

    @pytest.mark.asyncio
    async def test_add_processing_stage_non_list_object(
        self, mock_db_session_async: AsyncMock
    ):
        """Test adding a stage when processing_stages is not a list or JSON list (e.g., a dict)."""
        # This scenario depends on how robust the add_processing_stage method is.
        # It might raise a TypeError, or attempt to handle it gracefully.
        # Let's assume it attempts to initialize to a new list with the stage.
        mock_job = VideoJobModel(video_id=42, processing_stages={"key": "value"})  # type: ignore
        mock_job.id = 123

        with patch(
            "apps.core.operations.video_job_repository.VideoJobRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get_by_id:
            mock_get_by_id.return_value = mock_job

            new_stage = "processing_initiated"
            updated_job = await VideoJobRepository.add_processing_stage(
                mock_db_session_async, 123, new_stage
            )

            mock_get_by_id.assert_awaited_once_with(mock_db_session_async, 123)
            assert updated_job is not None
            if updated_job:
                assert updated_job is mock_job
                # Assuming it re-initializes or similar graceful handling
                assert updated_job.processing_stages == [new_stage]

            mock_db_session_async.flush.assert_awaited_once()
            mock_db_session_async.refresh.assert_awaited_once_with(mock_job)
