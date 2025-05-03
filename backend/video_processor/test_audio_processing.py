#!/usr/bin/env python3
"""
Test script to verify the audio processing with Gemini API.
"""

import logging
import os
import subprocess
import tempfile

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set project ID directly for testing
PROJECT_ID = "automations-457120"  # Use the same project ID as in the main code
REGION = "us-central1"


def test_audio_processing():
    """Test audio processing with a sample WAV file."""
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=REGION)
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple test audio file using ffmpeg
        test_audio_path = os.path.join(tmpdir, "test_audio.wav")

        # Generate a simple test tone using ffmpeg
        logging.info(f"Generating test audio file at {test_audio_path}...")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",  # Overwrite output files without asking
                    "-f",
                    "lavfi",  # Use libavfilter
                    "-i",
                    "sine=frequency=440:duration=5",  # Generate a 5-second 440Hz tone
                    "-ar",
                    "16000",  # Audio sample rate
                    "-ac",
                    "1",  # Mono audio
                    test_audio_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info("Test audio generation complete.")
        except subprocess.CalledProcessError as e:
            logging.error(f"ffmpeg failed: {e}\nStderr: {e.stderr}")
            return

        # Read the audio file and create a proper Part object
        logging.info("Reading audio file and creating Part object...")
        try:
            with open(test_audio_path, "rb") as f:
                audio_bytes = f.read()

            # Create a Part object with the correct MIME type
            audio_part = Part.from_data(mime_type="audio/wav", data=audio_bytes)

            # Test the transcript generation with our own implementation
            logging.info("Testing transcript generation...")

            # Define a simple transcript function for testing
            def generate_test_transcript(audio_part):
                """Test function to generate a transcript from audio data."""
                transcription_model = GenerativeModel("gemini-2.0-flash-001")
                prompt = (
                    "Generate a transcription of the audio, only extract speech "
                    "and ignore background audio."
                )
                response = transcription_model.generate_content(
                    [prompt, audio_part],
                    generation_config={"temperature": 0.2},
                )
                return response.text.strip()

            transcript = generate_test_transcript(audio_part)
            logging.info(f"Generated transcript: {transcript}")

            logging.info("Test completed successfully!")
        except Exception as e:
            logging.error(f"Error during testing: {e}")


if __name__ == "__main__":
    test_audio_processing()
