"""
Unit tests for the VideoProcessorService.
"""

from unittest.mock import MagicMock, patch

import pytest
from video_processor.application.services.video_processor import VideoProcessorService
from video_processor.domain.models.enums import ProcessingStage, ProcessingStatus
from video_processor.domain.models.job import VideoJob

from tests.mocks.ai import MockAIAdapter
from tests.mocks.storage import MockStorageAdapter


@pytest.fixture
def mock_services():
    """Create mock services needed by the VideoProcessorService."""
    mock_transcription = MagicMock()
    mock_transcription.generate_transcript.return_value = "Mocked transcript content"

    mock_subtitle = MagicMock()
    mock_subtitle.generate_vtt.return_value = (
        "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nMocked subtitle content"
    )
    mock_subtitle.generate_srt.return_value = (
        "1\n00:00:00,000 --> 00:00:05,000\nMocked subtitle content"
    )

    mock_metadata = MagicMock()
    mock_metadata.generate_title.return_value = "Generated Video Title"
    mock_metadata.generate_description.return_value = "Generated video description"
    mock_metadata.generate_tags.return_value = ["tag1", "tag2", "tag3"]

    return {
        "transcription": mock_transcription,
        "subtitle": mock_subtitle,
        "metadata": mock_metadata,
    }


@patch("video_processor.application.services.video_processor.extract_audio")
@patch("video_processor.application.services.video_processor.extract_frame")
@patch("video_processor.application.services.video_processor.get_video_metadata")
def test_video_processor_service_instantiation(
    mock_get_metadata, mock_extract_frame, mock_extract_audio
):
    """Test that the VideoProcessorService can be instantiated with dependencies."""
    storage = MockStorageAdapter()
    ai = MockAIAdapter()

    service = VideoProcessorService(
        storage_adapter=storage,
        ai_adapter=ai,
        output_bucket="test-bucket",
        local_output_dir="/tmp/test-output",
    )

    assert service._storage == storage
    assert service._ai == ai
    assert service._output_bucket == "test-bucket"
    assert service._local_output_dir == "/tmp/test-output"
    assert service._transcription_service is not None
    assert service._subtitle_service is not None
    assert service._metadata_service is not None


@patch("video_processor.application.services.video_processor.TranscriptionService")
@patch("video_processor.application.services.video_processor.SubtitleService")
@patch("video_processor.application.services.video_processor.MetadataService")
@patch("video_processor.application.services.video_processor.extract_audio")
@patch("video_processor.application.services.video_processor.extract_frame")
@patch("video_processor.application.services.video_processor.get_video_metadata")
@patch("tempfile.TemporaryDirectory")
def test_process_video_success_flow(
    mock_temp_dir,
    mock_get_metadata,
    mock_extract_frame,
    mock_extract_audio,
    MockMetadataService,
    MockSubtitleService,
    MockTranscriptionService,
    test_video,
    test_metadata,
):
    """Test the successful video processing flow."""
    # Configure mocks
    mock_temp_dir.return_value.__enter__.return_value = "/tmp/mock"
    mock_get_metadata.return_value = {
        "duration": 60.0,
        "resolution": (1920, 1080),
        "format": "mp4",
    }

    # Mock service instances
    mock_transcription = MockTranscriptionService.return_value
    mock_transcription.generate_transcript.return_value = "Mocked transcript content"

    mock_subtitle = MockSubtitleService.return_value
    mock_subtitle.generate_vtt.return_value = "WEBVTT content"
    mock_subtitle.generate_srt.return_value = "SRT content"

    mock_metadata = MockMetadataService.return_value
    mock_metadata.generate_title.return_value = "Generated Title"
    mock_metadata.generate_description.return_value = "Generated Description"
    mock_metadata.generate_tags.return_value = ["tag1", "tag2"]
    mock_metadata.generate_thumbnail_description.return_value = (
        "A person explaining concepts"
    )

    # Create test objects
    storage = MockStorageAdapter()
    ai = MockAIAdapter()

    job = VideoJob.create_new(test_video)
    job.metadata = test_metadata

    # Create service and process video
    service = VideoProcessorService(storage_adapter=storage, ai_adapter=ai)

    # Mock file paths to avoid file system operations
    with patch("os.path.exists", return_value=True):
        processed_job = service.process_video(job)

    # Verify job was updated correctly
    assert processed_job.status == ProcessingStatus.COMPLETED
    assert processed_job.error_message is None

    # Verify all stages were completed
    assert ProcessingStage.DOWNLOAD in processed_job.completed_stages
    assert ProcessingStage.EXTRACT_AUDIO in processed_job.completed_stages
    assert ProcessingStage.GENERATE_TRANSCRIPT in processed_job.completed_stages
    assert ProcessingStage.GENERATE_SUBTITLES in processed_job.completed_stages
    assert ProcessingStage.GENERATE_SHOWNOTES in processed_job.completed_stages
    assert ProcessingStage.UPLOAD_OUTPUTS in processed_job.completed_stages

    # Verify the core service calls were made
    assert mock_transcription.generate_transcript.called
    assert mock_subtitle.generate_vtt.called
    assert mock_subtitle.generate_srt.called
    assert mock_metadata.generate_title.called
    assert mock_metadata.generate_description.called
    assert mock_metadata.generate_tags.called

    # Verify storage operations
    assert len(storage.files) > 0


@patch("video_processor.application.services.video_processor.TranscriptionService")
@patch("video_processor.application.services.video_processor.SubtitleService")
@patch("video_processor.application.services.video_processor.MetadataService")
@patch("video_processor.application.services.video_processor.extract_audio")
@patch("video_processor.application.services.video_processor.extract_frame")
@patch("video_processor.application.services.video_processor.get_video_metadata")
@patch("tempfile.TemporaryDirectory")
def test_process_video_file_not_found(
    mock_temp_dir,
    mock_get_metadata,
    mock_extract_frame,
    mock_extract_audio,
    MockMetadataService,
    MockSubtitleService,
    MockTranscriptionService,
    test_video,
):
    """Test handling of file not found error."""
    # Configure mocks
    mock_temp_dir.return_value.__enter__.return_value = "/tmp/mock"

    # Create test objects
    storage = MockStorageAdapter()
    ai = MockAIAdapter()

    job = VideoJob.create_new(test_video)

    # Create service
    service = VideoProcessorService(storage_adapter=storage, ai_adapter=ai)

    # Mock file not existing
    with patch("os.path.exists", return_value=False):
        with pytest.raises(Exception) as excinfo:
            service.process_video(job)

        # Verify exception was raised
        assert "Video file not found" in str(excinfo.value)

    # Verify job status was updated
    assert job.status == ProcessingStatus.FAILED
    assert job.error_message is not None


@patch("video_processor.application.services.video_processor.TranscriptionService")
@patch("video_processor.application.services.video_processor.SubtitleService")
@patch("video_processor.application.services.video_processor.MetadataService")
@patch("video_processor.application.services.video_processor.extract_audio")
@patch("video_processor.application.services.video_processor.extract_frame")
@patch("video_processor.application.services.video_processor.get_video_metadata")
@patch("tempfile.TemporaryDirectory")
def test_process_video_transcript_error(
    mock_temp_dir,
    mock_get_metadata,
    mock_extract_frame,
    mock_extract_audio,
    MockMetadataService,
    MockSubtitleService,
    MockTranscriptionService,
    test_video,
):
    """Test handling of transcript generation error."""
    # Configure mocks
    mock_temp_dir.return_value.__enter__.return_value = "/tmp/mock"
    mock_get_metadata.return_value = {
        "duration": 60.0,
        "resolution": (1920, 1080),
        "format": "mp4",
    }

    # Mock transcript error
    mock_transcription = MockTranscriptionService.return_value
    mock_transcription.generate_transcript.side_effect = Exception(
        "Transcript generation failed"
    )

    # Create test objects
    storage = MockStorageAdapter()
    ai = MockAIAdapter()

    job = VideoJob.create_new(test_video)

    # Create service
    service = VideoProcessorService(storage_adapter=storage, ai_adapter=ai)

    # Run test
    with patch("os.path.exists", return_value=True):
        with pytest.raises(Exception) as excinfo:
            service.process_video(job)

        # Verify exception was raised
        assert "Transcript generation failed" in str(excinfo.value)

    # Verify job status was updated
    assert job.status == ProcessingStatus.FAILED
    assert job.error_message is not None
    assert "Transcript generation failed" in job.error_message
