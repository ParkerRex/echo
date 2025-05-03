from video_processor.core.processors.video import process_video_event


def test_skip_non_mp4_files(mocker):
    """Test that process_video_event skips non-MP4 files."""
    # Call the function with a non-MP4 file
    process_video_event("test-bucket", "daily-raw/test_file.txt")

    # Verify that the function returns early
    mock_get_storage_service = mocker.patch(
        "video_processor.core.processors.video.get_storage_service"
    )
    mock_get_storage_service.assert_not_called()


def test_skip_incorrect_path(mocker):
    """Test that process_video_event skips files not in the correct paths."""
    # Call the function with a file in the wrong path
    process_video_event("test-bucket", "wrong-path/test_file.mp4")

    # Verify that the function returns early
    mock_get_storage_service = mocker.patch(
        "video_processor.core.processors.video.get_storage_service"
    )
    mock_get_storage_service.assert_not_called()
