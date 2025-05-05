"""
Unit tests for the VideoJob domain model.
"""

from datetime import datetime

import pytest
from video_processor.domain.models.enums import ProcessingStage, ProcessingStatus
from video_processor.domain.models.job import VideoJob
from video_processor.domain.models.metadata import VideoMetadata
from video_processor.domain.models.video import Video


@pytest.fixture
def sample_video():
    """Create a sample video for testing."""
    return Video(
        id="video123",
        file_path="/path/to/video.mp4",
        file_name="video.mp4",
        duration=60.0,
    )


@pytest.fixture
def sample_metadata():
    """Create sample metadata for testing."""
    return VideoMetadata(
        title="Test Video",
        description="This is a test video",
        tags=["test", "video"],
    )


def test_job_creation(sample_video):
    """Test that a VideoJob can be created with minimal attributes."""
    job = VideoJob(job_id="job123", video=sample_video)

    assert job.job_id == "job123"
    assert job.video.id == "video123"
    assert job.status == ProcessingStatus.PENDING
    assert job.current_stage == ProcessingStage.DOWNLOAD
    assert job.completed_stages == []
    assert job.error_message is None
    assert job.processed_path is None
    assert job.output_files == {}
    assert job.youtube_video_id is None
    assert isinstance(job.created_at, datetime)
    assert isinstance(job.updated_at, datetime)
    assert job.metadata.title == ""  # Default empty title


def test_create_new_job(sample_video):
    """Test creation of a new job from a video."""
    job = VideoJob.create_new(sample_video)

    assert job.job_id.startswith(f"job-{sample_video.id}-")
    assert job.video == sample_video
    assert job.metadata.title == "Video"  # From filename "video.mp4"
    assert job.status == ProcessingStatus.PENDING


def test_job_with_metadata(sample_video, sample_metadata):
    """Test job creation with metadata."""
    job = VideoJob(
        job_id="job123",
        video=sample_video,
        metadata=sample_metadata,
    )

    assert job.metadata.title == "Test Video"
    assert job.metadata.description == "This is a test video"
    assert job.metadata.tags == ["test", "video"]


def test_update_status(sample_video):
    """Test updating job status."""
    job = VideoJob(job_id="job123", video=sample_video)
    original_updated_at = job.updated_at

    # Small delay to ensure timestamp changes
    job.update_status(ProcessingStatus.IN_PROGRESS)

    assert job.status == ProcessingStatus.IN_PROGRESS
    assert job.updated_at > original_updated_at

    # Test with error message
    job.update_status(ProcessingStatus.FAILED, "Something went wrong")

    assert job.status == ProcessingStatus.FAILED
    assert job.error_message == "Something went wrong"


def test_move_to_stage(sample_video):
    """Test moving to a new processing stage."""
    job = VideoJob(job_id="job123", video=sample_video)
    original_updated_at = job.updated_at

    # Initial stage is DOWNLOAD and should be moved to completed
    job.move_to_stage(ProcessingStage.EXTRACT_AUDIO)

    assert job.current_stage == ProcessingStage.EXTRACT_AUDIO
    assert ProcessingStage.DOWNLOAD in job.completed_stages
    assert job.updated_at > original_updated_at

    # Move to next stage
    job.move_to_stage(ProcessingStage.GENERATE_TRANSCRIPT)

    assert job.current_stage == ProcessingStage.GENERATE_TRANSCRIPT
    assert ProcessingStage.EXTRACT_AUDIO in job.completed_stages
    assert len(job.completed_stages) == 2


def test_complete_current_stage(sample_video):
    """Test completing the current stage."""
    job = VideoJob(job_id="job123", video=sample_video)
    original_updated_at = job.updated_at

    job.complete_current_stage()

    assert ProcessingStage.DOWNLOAD in job.completed_stages
    assert job.current_stage == ProcessingStage.DOWNLOAD  # Hasn't changed
    assert job.updated_at > original_updated_at


def test_is_stage_completed(sample_video):
    """Test checking if a stage is completed."""
    job = VideoJob(job_id="job123", video=sample_video)

    assert not job.is_stage_completed(ProcessingStage.DOWNLOAD)

    job.complete_current_stage()

    assert job.is_stage_completed(ProcessingStage.DOWNLOAD)
    assert not job.is_stage_completed(ProcessingStage.EXTRACT_AUDIO)


def test_add_output_file(sample_video):
    """Test adding output files."""
    job = VideoJob(job_id="job123", video=sample_video)
    original_updated_at = job.updated_at

    job.add_output_file("transcript", "/path/to/transcript.txt")

    assert job.output_files["transcript"] == "/path/to/transcript.txt"
    assert job.updated_at > original_updated_at

    job.add_output_file("subtitles", "/path/to/subtitles.vtt")

    assert len(job.output_files) == 2
    assert job.output_files["subtitles"] == "/path/to/subtitles.vtt"


def test_fail(sample_video):
    """Test marking a job as failed."""
    job = VideoJob(job_id="job123", video=sample_video)
    original_updated_at = job.updated_at

    job.fail("Processing error")

    assert job.status == ProcessingStatus.FAILED
    assert job.error_message == "Processing error"
    assert job.updated_at > original_updated_at


def test_complete(sample_video):
    """Test marking a job as completed."""
    job = VideoJob(job_id="job123", video=sample_video)
    original_updated_at = job.updated_at

    job.complete()

    assert job.status == ProcessingStatus.COMPLETED
    assert job.current_stage == ProcessingStage.COMPLETE
    assert ProcessingStage.DOWNLOAD in job.completed_stages  # Current stage was added
    assert job.updated_at > original_updated_at
    assert job.is_complete() is True


def test_is_complete(sample_video):
    """Test checking if a job is complete."""
    job = VideoJob(job_id="job123", video=sample_video)

    assert job.is_complete() is False

    job.update_status(ProcessingStatus.COMPLETED)

    assert job.is_complete() is True


def test_to_dict(sample_video, sample_metadata):
    """Test conversion to dictionary."""
    job = VideoJob(
        job_id="job123",
        video=sample_video,
        metadata=sample_metadata,
        processed_path="/processed/video.mp4",
        youtube_video_id="yt12345",
    )

    job_dict = job.to_dict()

    assert job_dict["job_id"] == "job123"
    assert isinstance(job_dict["video"], dict)
    assert job_dict["video"]["id"] == "video123"
    assert isinstance(job_dict["created_at"], str)
    assert isinstance(job_dict["updated_at"], str)
    assert isinstance(job_dict["metadata"], dict)
    assert job_dict["metadata"]["title"] == "Test Video"
    assert job_dict["status"] == "PENDING"
    assert job_dict["current_stage"] == "DOWNLOAD"
    assert job_dict["completed_stages"] == []
    assert job_dict["processed_path"] == "/processed/video.mp4"
    assert job_dict["youtube_video_id"] == "yt12345"


def test_from_dict(sample_video, sample_metadata):
    """Test creation from dictionary."""
    # Create a timestamp for testing
    now = datetime.now()

    job_dict = {
        "job_id": "job123",
        "video": sample_video.to_dict(),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "metadata": sample_metadata.to_dict(),
        "status": "IN_PROGRESS",
        "current_stage": "GENERATE_TRANSCRIPT",
        "completed_stages": ["DOWNLOAD", "EXTRACT_AUDIO"],
        "error_message": None,
        "processed_path": "/processed/video.mp4",
        "output_files": {
            "transcript": "/path/to/transcript.txt",
            "subtitles": "/path/to/subtitles.vtt",
        },
        "youtube_video_id": "yt12345",
    }

    job = VideoJob.from_dict(job_dict)

    assert job.job_id == "job123"
    assert job.video.id == "video123"
    assert job.created_at.isoformat() == now.isoformat()
    assert job.updated_at.isoformat() == now.isoformat()
    assert job.metadata.title == "Test Video"
    assert job.status == ProcessingStatus.IN_PROGRESS
    assert job.current_stage == ProcessingStage.GENERATE_TRANSCRIPT
    assert len(job.completed_stages) == 2
    assert ProcessingStage.DOWNLOAD in job.completed_stages
    assert ProcessingStage.EXTRACT_AUDIO in job.completed_stages
    assert job.processed_path == "/processed/video.mp4"
    assert job.output_files["transcript"] == "/path/to/transcript.txt"
    assert job.output_files["subtitles"] == "/path/to/subtitles.vtt"
    assert job.youtube_video_id == "yt12345"
