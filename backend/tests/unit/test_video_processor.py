"""
Unit tests for the video processor core functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from video_processor.core.models import (
    ProcessingStage,
    ProcessingStatus,
    VideoJob,
    VideoMetadata,
)
from video_processor.core.processors.video import process_video, process_video_event
from video_processor.services.storage.gcs import StorageError
from video_processor.utils.error_handling import VideoProcessingError


def test_process_video_event_skips_non_mp4():
    """Test that process_video_event skips non-MP4 files."""
    # Call with non-MP4 file
    process_video_event("test-bucket", "daily-raw/test_file.txt")

    # No assertions needed - function should return without errors


def test_process_video_event_skips_wrong_path():
    """Test that process_video_event skips files not in the correct paths."""
    # Call with file in wrong path
    process_video_event("test-bucket", "wrong-path/test_file.mp4")

    # No assertions needed - function should return without errors


@patch("video_processor.core.processors.video.get_storage_service")
@patch("video_processor.core.processors.video.AudioProcessor")
@patch("video_processor.core.processors.video.tempfile.TemporaryDirectory")
def test_process_video_event_sets_up_job(
    mock_temp_dir, mock_audio_processor_class, mock_get_storage_service
):
    """Test that process_video_event sets up a job correctly."""
    # Set up mocks
    mock_storage_service = MagicMock()
    mock_get_storage_service.return_value = mock_storage_service

    mock_audio_processor = MagicMock()
    mock_audio_processor_class.return_value = mock_audio_processor

    mock_temp_dir_instance = MagicMock()
    mock_temp_dir_instance.__enter__.return_value = "/tmp/test_dir"
    mock_temp_dir.return_value = mock_temp_dir_instance

    # Patch process_video to isolate the job setup
    with patch(
        "video_processor.core.processors.video.process_video"
    ) as mock_process_video:
        # Call the function
        process_video_event("test-bucket", "daily-raw/test_video.mp4")

        # Verify job setup and passing to process_video
        mock_process_video.assert_called_once()

        # Extract the job argument
        job = mock_process_video.call_args[0][0]

        # Verify job properties
        assert job.bucket_name == "test-bucket"
        assert job.file_name == "daily-raw/test_video.mp4"
        assert job.metadata.title == "test_video"
        assert job.metadata.channel == "daily"
        assert job.processed_path == "processed-daily/test_video/"
        assert job.status == ProcessingStatus.PENDING
        assert job.current_stage == ProcessingStage.DOWNLOAD


@patch("video_processor.core.processors.video.get_storage_service")
@patch("video_processor.core.processors.video.AudioProcessor")
@patch("video_processor.core.processors.video.tempfile.TemporaryDirectory")
def test_process_video_normalizes_filename(
    mock_temp_dir, mock_audio_processor_class, mock_get_storage_service
):
    """Test that process_video_event normalizes filenames with spaces."""
    # Set up mocks
    mock_storage_service = MagicMock()
    mock_get_storage_service.return_value = mock_storage_service

    mock_audio_processor = MagicMock()
    mock_audio_processor_class.return_value = mock_audio_processor

    mock_temp_dir_instance = MagicMock()
    mock_temp_dir_instance.__enter__.return_value = "/tmp/test_dir"
    mock_temp_dir.return_value = mock_temp_dir_instance

    # Patch process_video to isolate the job setup
    with patch(
        "video_processor.core.processors.video.process_video"
    ) as mock_process_video:
        # Call the function with a filename containing spaces
        process_video_event("test-bucket", "daily-raw/Test Video With Spaces.mp4")

        # Verify job setup and passing to process_video
        mock_process_video.assert_called_once()

        # Extract the job argument
        job = mock_process_video.call_args[0][0]

        # Verify normalized paths
        assert job.metadata.title == "Test Video With Spaces"
        assert job.processed_path == "processed-daily/Test-Video-With-Spaces/"


def test_process_video_downloads_file():
    """Test process_video downloads the video file."""
    # Create test job
    job = VideoJob(
        bucket_name="test-bucket",
        file_name="daily-raw/test_video.mp4",
        job_id="test-job",
        metadata=VideoMetadata(title="test_video", channel="daily"),
        processed_path="processed-daily/test_video/",
    )

    # Mock storage service
    mock_storage_service = MagicMock()
    mock_storage_service.download_file.return_value = "/tmp/test_dir/test_video.mp4"

    # Mock audio processor
    mock_audio_processor = MagicMock()
    mock_audio_processor.extract_audio.return_value = "/tmp/test_dir/test_video.wav"

    # Mock temporary directory context
    with patch(
        "video_processor.core.processors.video.tempfile.TemporaryDirectory"
    ) as mock_temp_dir:
        mock_temp_dir_instance = MagicMock()
        mock_temp_dir_instance.__enter__.return_value = "/tmp/test_dir"
        mock_temp_dir.return_value = mock_temp_dir_instance

        # Also need to mock get_settings
        with patch(
            "video_processor.core.processors.video.get_settings"
        ) as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.testing_mode = False
            mock_get_settings.return_value = mock_settings

            # Call the function
            process_video(job, mock_storage_service, mock_audio_processor)

            # Verify download was called
            mock_storage_service.download_file.assert_called_once_with(
                "test-bucket",
                "daily-raw/test_video.mp4",
                "/tmp/test_dir/test_video.mp4",
            )

            # Verify job status was updated
            assert job.status == ProcessingStatus.COMPLETED
            assert ProcessingStage.DOWNLOAD in job.completed_stages


def test_process_video_handles_download_error():
    """Test process_video handles download errors."""
    # Create test job
    job = VideoJob(
        bucket_name="test-bucket",
        file_name="daily-raw/test_video.mp4",
        job_id="test-job",
        metadata=VideoMetadata(title="test_video", channel="daily"),
        processed_path="processed-daily/test_video/",
    )

    # Mock storage service that fails on download
    mock_storage_service = MagicMock()
    mock_storage_service.download_file.side_effect = StorageError("Download failed")

    # Mock audio processor
    mock_audio_processor = MagicMock()

    # Mock temporary directory context
    with patch(
        "video_processor.core.processors.video.tempfile.TemporaryDirectory"
    ) as mock_temp_dir:
        mock_temp_dir_instance = MagicMock()
        mock_temp_dir_instance.__enter__.return_value = "/tmp/test_dir"
        mock_temp_dir.return_value = mock_temp_dir_instance

        # Also need to mock get_settings
        with patch(
            "video_processor.core.processors.video.get_settings"
        ) as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.testing_mode = False
            mock_get_settings.return_value = mock_settings

            # Call the function and expect error
            with pytest.raises(VideoProcessingError) as excinfo:
                process_video(job, mock_storage_service, mock_audio_processor)

            # Verify error message
            assert "Download failed" in str(excinfo.value)

            # Verify job status was updated to failed
            assert job.status == ProcessingStatus.FAILED
            assert "Download failed" in job.error_message


def test_add_dummy_outputs():
    """Test the _add_dummy_outputs helper function."""
    from video_processor.core.processors.video import _add_dummy_outputs

    # Create test job
    job = VideoJob(
        bucket_name="test-bucket",
        file_name="daily-raw/test_video.mp4",
        job_id="test-job",
        metadata=VideoMetadata(title="test_video", channel="daily"),
        processed_path="processed-daily/test_video/",
    )

    # Mock storage service
    mock_storage_service = MagicMock()

    # Call the function
    _add_dummy_outputs(job, mock_storage_service)

    # Verify upload_from_string was called for each output file
    assert mock_storage_service.upload_from_string.call_count == 5

    # Verify output files were added to job
    assert len(job.output_files) == 5
    assert "transcript.txt" in job.output_files
    assert "subtitles.vtt" in job.output_files
    assert "shownotes.txt" in job.output_files
    assert "chapters.txt" in job.output_files
    assert "title.txt" in job.output_files
