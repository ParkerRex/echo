"""
Unit tests for domain enums.
"""

from video_processor.domain.models.enums import ProcessingStage, ProcessingStatus


def test_processing_stage_values():
    """Test the existence and order of processing stage enum values."""
    stages = list(ProcessingStage)

    # Verify all expected stages exist
    assert ProcessingStage.DOWNLOAD in stages
    assert ProcessingStage.EXTRACT_AUDIO in stages
    assert ProcessingStage.GENERATE_TRANSCRIPT in stages
    assert ProcessingStage.GENERATE_SUBTITLES in stages
    assert ProcessingStage.GENERATE_SHOWNOTES in stages
    assert ProcessingStage.GENERATE_CHAPTERS in stages
    assert ProcessingStage.GENERATE_TITLES in stages
    assert ProcessingStage.UPLOAD_OUTPUTS in stages
    assert ProcessingStage.UPLOAD_TO_YOUTUBE in stages
    assert ProcessingStage.COMPLETE in stages

    # Test that DOWNLOAD is the first stage
    assert stages[0] == ProcessingStage.DOWNLOAD

    # Test that COMPLETE is the last stage
    assert stages[-1] == ProcessingStage.COMPLETE


def test_processing_status_values():
    """Test the existence and properties of processing status enum values."""
    statuses = list(ProcessingStatus)

    # Verify all expected statuses exist
    assert ProcessingStatus.PENDING in statuses
    assert ProcessingStatus.IN_PROGRESS in statuses
    assert ProcessingStatus.COMPLETED in statuses
    assert ProcessingStatus.FAILED in statuses
    assert ProcessingStatus.PARTIAL in statuses

    # Test enum properties
    assert str(ProcessingStatus.PENDING) == "ProcessingStatus.PENDING"
    assert ProcessingStatus.PENDING.name == "PENDING"


def test_processing_stage_comparisons():
    """Test that enum stages can be properly compared."""
    # Test identity comparison
    assert ProcessingStage.DOWNLOAD is ProcessingStage.DOWNLOAD
    assert ProcessingStage.DOWNLOAD is not ProcessingStage.EXTRACT_AUDIO

    # Test equality comparison
    assert ProcessingStage.DOWNLOAD == ProcessingStage.DOWNLOAD
    assert ProcessingStage.DOWNLOAD != ProcessingStage.EXTRACT_AUDIO

    # Test ordering based on declaration order
    assert ProcessingStage.DOWNLOAD.value < ProcessingStage.EXTRACT_AUDIO.value
    assert (
        ProcessingStage.GENERATE_TRANSCRIPT.value > ProcessingStage.EXTRACT_AUDIO.value
    )
    assert ProcessingStage.COMPLETE.value > ProcessingStage.UPLOAD_TO_YOUTUBE.value
