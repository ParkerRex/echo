"""
Tests for the main process_video_event function.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, call

# Import the function to test
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from process_uploaded_video import process_video_event


def test_process_video_event_skips_non_mp4(mock_storage_client):
    """Test that process_video_event skips non-MP4 files."""
    # Call the function with a non-MP4 file
    result = process_video_event("test-bucket", "daily-raw/test_file.txt")

    # Verify that the function returns early
    mock_client, mock_bucket, mock_blob = mock_storage_client
    mock_client.bucket.assert_not_called()


def test_process_video_event_skips_wrong_path(mock_storage_client):
    """Test that process_video_event skips files not in the correct paths."""
    # Call the function with a file in the wrong path
    result = process_video_event("test-bucket", "wrong-path/test_file.mp4")

    # Verify that the function returns early
    mock_client, mock_bucket, mock_blob = mock_storage_client
    mock_client.bucket.assert_not_called()


@patch("video_processor.process_uploaded_video.tempfile.TemporaryDirectory")
@patch("video_processor.process_uploaded_video.subprocess.run")
@patch("video_processor.process_uploaded_video.generate_transcript")
@patch("video_processor.process_uploaded_video.generate_vtt")
@patch("video_processor.process_uploaded_video.generate_shownotes")
@patch("video_processor.process_uploaded_video.generate_chapters")
@patch("video_processor.process_uploaded_video.generate_titles")
@patch("video_processor.process_uploaded_video.write_blob")
@patch("video_processor.process_uploaded_video.Part")
def test_process_video_event_success(
    mock_part,
    mock_write_blob,
    mock_generate_titles,
    mock_generate_chapters,
    mock_generate_shownotes,
    mock_generate_vtt,
    mock_generate_transcript,
    mock_subprocess_run,
    mock_temp_dir,
    mock_storage_client,
):
    """Test the full process_video_event function with successful execution."""
    # Set up mocks
    mock_client, mock_bucket, mock_blob = mock_storage_client

    # Mock the temporary directory
    mock_temp_dir_instance = MagicMock()
    mock_temp_dir_instance.__enter__.return_value = "/tmp/mock_dir"
    mock_temp_dir.return_value = mock_temp_dir_instance

    # Mock the subprocess.run result
    mock_subprocess_run.return_value = MagicMock()

    # Mock the Part.from_data method
    mock_audio_part = MagicMock()
    mock_part.from_data.return_value = mock_audio_part

    # Mock the generate_* functions
    mock_generate_transcript.return_value = "Test transcript"
    mock_generate_vtt.return_value = (
        "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest subtitle"
    )
    mock_generate_shownotes.return_value = "Test shownotes"
    mock_generate_chapters.return_value = [
        {"timecode": "00:00", "chapterSummary": "Introduction"},
        {"timecode": "02:30", "chapterSummary": "Main topic"},
    ]
    mock_generate_titles.return_value = {
        "Description": "Test Title",
        "Keywords": "test,keywords",
    }

    # Call the function
    process_video_event("test-bucket", "daily-raw/test_video.mp4")

    # Verify the bucket and blob were accessed
    mock_client.bucket.assert_called_once_with("test-bucket")
    mock_bucket.blob.assert_called_with("daily-raw/test_video.mp4")

    # Verify the blob was downloaded
    mock_blob.download_to_filename.assert_called_once()

    # Verify ffmpeg was called
    mock_subprocess_run.assert_called_once()

    # Verify the audio part was created
    mock_part.from_data.assert_called_once()
    assert mock_part.from_data.call_args[1]["mime_type"] == "audio/wav"

    # Verify all generate functions were called with the audio part
    mock_generate_transcript.assert_called_once_with(mock_audio_part)
    mock_generate_vtt.assert_called_once_with(mock_audio_part)
    mock_generate_shownotes.assert_called_once_with(mock_audio_part)
    mock_generate_chapters.assert_called_once_with(mock_audio_part)
    mock_generate_titles.assert_called_once_with(mock_audio_part)

    # Verify write_blob was called for each output file
    assert (
        mock_write_blob.call_count == 5
    )  # transcript, subtitles, shownotes, chapters, title

    # Verify the original file was moved
    mock_bucket.copy_blob.assert_called_once_with(
        mock_blob, mock_bucket, "processed-daily/test_video/test_video.mp4"
    )
    mock_blob.delete.assert_called_once()


@patch("video_processor.process_uploaded_video.tempfile.TemporaryDirectory")
def test_process_video_event_download_error(mock_temp_dir, mock_storage_client):
    """Test process_video_event handles download errors."""
    # Set up mocks
    mock_client, mock_bucket, mock_blob = mock_storage_client

    # Mock the temporary directory
    mock_temp_dir_instance = MagicMock()
    mock_temp_dir_instance.__enter__.return_value = "/tmp/mock_dir"
    mock_temp_dir.return_value = mock_temp_dir_instance

    # Make the download fail
    mock_blob.download_to_filename.side_effect = Exception("Download failed")

    # Call the function and expect an exception
    with pytest.raises(Exception) as excinfo:
        process_video_event("test-bucket", "daily-raw/test_video.mp4")

    # Verify the exception message
    assert "Download failed" in str(excinfo.value)

    # Verify the bucket and blob were accessed
    mock_client.bucket.assert_called_once_with("test-bucket")
    mock_bucket.blob.assert_called_with("daily-raw/test_video.mp4")


@patch("video_processor.process_uploaded_video.tempfile.TemporaryDirectory")
@patch("video_processor.process_uploaded_video.subprocess.run")
def test_process_video_event_ffmpeg_error(
    mock_subprocess_run, mock_temp_dir, mock_storage_client
):
    """Test process_video_event handles ffmpeg errors."""
    # Set up mocks
    mock_client, mock_bucket, mock_blob = mock_storage_client

    # Mock the temporary directory
    mock_temp_dir_instance = MagicMock()
    mock_temp_dir_instance.__enter__.return_value = "/tmp/mock_dir"
    mock_temp_dir.return_value = mock_temp_dir_instance

    # Make the subprocess.run fail
    mock_subprocess_run.side_effect = Exception("ffmpeg failed")

    # Call the function and expect an exception
    with pytest.raises(Exception) as excinfo:
        process_video_event("test-bucket", "daily-raw/test_video.mp4")

    # Verify the exception message
    assert "ffmpeg failed" in str(excinfo.value)

    # Verify the bucket and blob were accessed
    mock_client.bucket.assert_called_once_with("test-bucket")
    mock_bucket.blob.assert_called_with("daily-raw/test_video.mp4")

    # Verify the blob was downloaded
    mock_blob.download_to_filename.assert_called_once()
