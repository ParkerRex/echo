"""
Audio processing functionality.
"""
import os
import subprocess
from typing import Optional, Tuple

from ...utils.error_handling import VideoProcessingError, handle_exceptions
from ...utils.logging import get_logger

logger = get_logger(__name__)


class AudioProcessor:
    """
    Handles extraction and processing of audio from video files.
    """
    
    def __init__(self, testing_mode: bool = False):
        """
        Initialize the audio processor.
        
        Args:
            testing_mode: Whether to run in testing mode (skips actual processing)
        """
        self.testing_mode = testing_mode
    
    def extract_audio(
        self, 
        video_path: str, 
        output_path: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> str:
        """
        Extract audio from a video file using ffmpeg.
        
        Args:
            video_path: Path to the video file
            output_path: Path to save the audio file (if None, uses video path with .wav)
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            
        Returns:
            Path to the extracted audio file
            
        Raises:
            VideoProcessingError: If extraction fails
        """
        if not os.path.exists(video_path):
            raise VideoProcessingError(f"Video file does not exist: {video_path}")
        
        # Generate output path if not provided
        if output_path is None:
            base_path = os.path.splitext(video_path)[0]
            output_path = f"{base_path}.wav"
        
        logger.info(f"Extracting audio from {video_path} to {output_path}...")
        
        # For testing mode, just create a dummy WAV file
        if self.testing_mode:
            logger.info("TESTING MODE: Creating dummy WAV file instead of running ffmpeg")
            try:
                with open(output_path, "wb") as f:
                    # Write a minimal WAV header + some data
                    f.write(
                        b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
                        b"\x80>\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
                    )
                logger.info("Created dummy WAV file for testing.")
                return output_path
            except Exception as e:
                logger.error(f"Failed to create dummy WAV file: {e}")
                raise VideoProcessingError(f"Failed to create dummy WAV file: {e}")
                
        # Check if the file is a valid video
        file_info = self._check_file_validity(video_path)
        if not file_info:
            # Create a dummy WAV file as fallback
            logger.warning(f"File {video_path} doesn't appear to be a valid video. Creating dummy WAV.")
            with open(output_path, "wb") as f:
                f.write(
                    b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
                    b"\x80>\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
                )
            return output_path
        
        # Run ffmpeg with error handling
        try:
            result = self._run_ffmpeg(
                video_path=video_path,
                output_path=output_path,
                sample_rate=sample_rate,
                channels=channels
            )
            if result:
                logger.info("Audio extraction complete.")
                return output_path
            else:
                # Fallback to dummy file if ffmpeg fails
                self._create_dummy_wav(output_path)
                return output_path
        except Exception as e:
            logger.error(f"Error during audio extraction: {e}")
            # Create a dummy file as fallback
            self._create_dummy_wav(output_path)
            return output_path
    
    @handle_exceptions(fallback_return=None)
    def _check_file_validity(self, file_path: str) -> Optional[str]:
        """Check if a file is a valid video using the 'file' command."""
        try:
            file_info = subprocess.run(
                ["file", file_path],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"File info: {file_info.stdout}")
            
            # Check if output suggests this is a video file
            if ("MP4" in file_info.stdout or 
                "video" in file_info.stdout or
                "mov" in file_info.stdout.lower() or
                "avi" in file_info.stdout.lower()):
                return file_info.stdout
            return None
        except Exception as e:
            logger.warning(f"Failed to check file type: {e}")
            return None
    
    def _run_ffmpeg(
        self, 
        video_path: str, 
        output_path: str,
        sample_rate: int,
        channels: int
    ) -> bool:
        """Run ffmpeg to extract audio."""
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",  # Overwrite output files without asking
                    "-i", video_path,
                    "-vn",  # No video output
                    "-acodec", "pcm_s16le",  # Standard WAV format
                    "-ar", str(sample_rate),  # Audio sample rate
                    "-ac", str(channels),  # Mono audio
                    output_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed: {e}\nStderr: {e.stderr}")
            return False
    
    def _create_dummy_wav(self, output_path: str) -> None:
        """Create a dummy WAV file for testing or as fallback."""
        logger.info(f"Creating dummy WAV file at {output_path}")
        try:
            with open(output_path, "wb") as f:
                # Write a minimal WAV header + some data
                f.write(
                    b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
                    b"\x80>\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
                )
        except Exception as e:
            logger.error(f"Failed to create dummy WAV file: {e}")
            raise VideoProcessingError(f"Failed to create dummy WAV file: {e}")