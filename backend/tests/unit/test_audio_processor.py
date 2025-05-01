"""
Unit tests for the AudioProcessor class.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, call

from video_processor.core.processors.audio import AudioProcessor
from video_processor.utils.error_handling import VideoProcessingError


def test_init():
    """Test AudioProcessor initialization."""
    processor = AudioProcessor()
    assert processor.testing_mode is False
    
    processor = AudioProcessor(testing_mode=True)
    assert processor.testing_mode is True


def test_extract_audio_testing_mode():
    """Test extract_audio method in testing mode."""
    processor = AudioProcessor(testing_mode=True)
    output_path = os.path.join(os.path.dirname(__file__), "test_output.wav")
    
    try:
        result = processor.extract_audio("/path/to/nonexistent/video.mp4", output_path)
        
        # Check result is the output path
        assert result == output_path
        
        # Check file was created
        assert os.path.exists(output_path)
        
        # Verify it's a WAV file (at least check the header)
        with open(output_path, "rb") as f:
            header = f.read(12)
            assert header.startswith(b"RIFF") and b"WAVE" in header
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_extract_audio_file_not_found():
    """Test extract_audio method with nonexistent file."""
    processor = AudioProcessor(testing_mode=False)
    
    with pytest.raises(VideoProcessingError) as excinfo:
        processor.extract_audio("/path/to/nonexistent/video.mp4")
    
    # Verify the error message
    assert "does not exist" in str(excinfo.value)


@patch("video_processor.core.processors.audio.subprocess.run")
def test_extract_audio_runs_ffmpeg(mock_subprocess_run, sample_video_file):
    """Test extract_audio runs ffmpeg with correct parameters."""
    processor = AudioProcessor(testing_mode=False)
    output_path = os.path.join(os.path.dirname(__file__), "test_output.wav")
    
    # Mock subprocess.run to return successfully
    mock_subprocess_result = MagicMock()
    mock_subprocess_run.return_value = mock_subprocess_result
    
    # Also mock the file validity check
    with patch("video_processor.core.processors.audio.AudioProcessor._check_file_validity", 
               return_value="MP4 file"):
        try:
            result = processor.extract_audio(sample_video_file, output_path)
            
            # Check result is the output path
            assert result == output_path
            
            # Verify ffmpeg was called with correct args
            mock_subprocess_run.assert_called_once()
            args = mock_subprocess_run.call_args[0][0]
            
            # Basic checks on the ffmpeg command
            assert args[0] == "ffmpeg"
            assert "-y" in args  # Overwrite without asking
            assert "-i" in args and args[args.index("-i")+1] == sample_video_file
            assert "-vn" in args  # No video output
            assert "-ar" in args and args[args.index("-ar")+1] == "16000"  # Sample rate
            assert "-ac" in args and args[args.index("-ac")+1] == "1"  # Mono
            assert args[-1] == output_path  # Output path
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)


@patch("video_processor.core.processors.audio.subprocess.run")
def test_extract_audio_fallback_to_dummy(mock_subprocess_run, sample_video_file):
    """Test extract_audio fallback to dummy file on ffmpeg failure."""
    processor = AudioProcessor(testing_mode=False)
    output_path = os.path.join(os.path.dirname(__file__), "test_output.wav")
    
    # Make ffmpeg fail
    mock_subprocess_run.side_effect = Exception("ffmpeg error")
    
    # Make the file validity check pass
    with patch("video_processor.core.processors.audio.AudioProcessor._check_file_validity", 
               return_value="MP4 file"):
        try:
            result = processor.extract_audio(sample_video_file, output_path)
            
            # Check result is the output path
            assert result == output_path
            
            # Check dummy file was created
            assert os.path.exists(output_path)
            
            # Verify it's a WAV file (at least check the header)
            with open(output_path, "rb") as f:
                header = f.read(12)
                assert header.startswith(b"RIFF") and b"WAVE" in header
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)


@patch("video_processor.core.processors.audio.subprocess.run")
def test_check_file_validity(mock_subprocess_run):
    """Test _check_file_validity method."""
    processor = AudioProcessor()
    
    # Mock subprocess.run to return successfully with MP4 info
    mock_result = MagicMock()
    mock_result.stdout = "test_file: ISO Media, MP4 v2 [ISO 14496-14]"
    mock_subprocess_run.return_value = mock_result
    
    result = processor._check_file_validity("test_file.mp4")
    assert result == mock_result.stdout
    
    # Mock subprocess.run to return successfully with non-video info
    mock_result.stdout = "test_file: ASCII text"
    result = processor._check_file_validity("test_file.txt")
    assert result is None
    
    # Mock subprocess.run to raise exception
    mock_subprocess_run.side_effect = Exception("command failed")
    result = processor._check_file_validity("test_file.mp4")
    assert result is None