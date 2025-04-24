#!/usr/bin/env python3
"""
Real API Test Script for the Video Processor application.
This script runs the video processor with real API calls to see actual outputs.
"""

import os
import sys
import time
import json
import logging
import argparse
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the video_processor module
sys.path.append(str(Path(__file__).parent.parent))


def setup_test_environment(video_file, clean=False):
    """
    Set up the test environment by creating the necessary directories and copying the test video file.

    Args:
        video_file: The name of the video file to use for testing
        clean: Whether to clean the test environment before setting it up
    """
    # Define paths
    test_data_dir = Path("test_data")
    daily_raw_dir = test_data_dir / "daily-raw"
    processed_daily_dir = test_data_dir / "processed-daily"

    # Create directories if they don't exist
    daily_raw_dir.mkdir(exist_ok=True, parents=True)
    processed_daily_dir.mkdir(exist_ok=True, parents=True)

    # Clean the test environment if requested
    if clean:
        logger.info("Cleaning test environment...")
        # Remove all files in daily-raw
        for file in daily_raw_dir.glob("*"):
            if file.is_file():
                file.unlink()

        # Remove all directories in processed-daily
        for dir in processed_daily_dir.glob("*"):
            if dir.is_dir():
                shutil.rmtree(dir)

    # Copy the test video file to daily-raw
    source_file = test_data_dir / video_file
    if not source_file.exists():
        logger.error(f"Test video file {source_file} does not exist!")
        return False

    target_file = daily_raw_dir / video_file
    shutil.copy2(source_file, target_file)
    logger.info(f"Copied test video file to {target_file}")

    return True


def process_video_with_real_apis(video_file):
    """
    Process the video file using real API calls.

    Args:
        video_file: The name of the video file to process
    """
    import subprocess
    import tempfile
    import shutil
    from google.oauth2 import service_account
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel, Part

    # Set environment variables for real API calls
    os.environ["TESTING_MODE"] = "false"
    os.environ["REAL_API_TEST"] = "true"
    os.environ["LOCAL_OUTPUT"] = "true"  # Write outputs to local filesystem

    # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to point to the service account file
    service_account_path = Path("@credentials/service_account.json").absolute()
    if not service_account_path.exists():
        logger.error(f"Service account credentials not found at {service_account_path}")
        logger.error(
            "Please place your service account credentials at @credentials/service_account.json"
        )
        return False

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_path)

    logger.info(f"Using service account credentials from {service_account_path}")

    # Authenticate with Google Cloud using the service account
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(service_account_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        logger.info(
            f"Successfully authenticated with service account: {credentials.service_account_email}"
        )
    except Exception as e:
        logger.error(f"Failed to authenticate with service account: {e}")
        return False

    # Initialize Vertex AI with the project ID from the service account
    project_id = credentials.project_id
    logger.info(f"Initializing Vertex AI with project ID: {project_id}")
    vertexai.init(project=project_id, location="us-central1")

    # Process the video locally instead of using GCS
    with tempfile.TemporaryDirectory() as tmpdir:
        # Define paths
        test_data_dir = Path("test_data")
        source_video_path = test_data_dir / video_file
        video_path = Path(tmpdir) / video_file
        audio_path = Path(tmpdir) / f"{Path(video_file).stem}.wav"

        # Copy the video file to the temp directory
        shutil.copy2(source_video_path, video_path)
        logger.info(f"Copied video file to {video_path}")

        # Extract audio using ffmpeg
        logger.info(f"Extracting audio from {video_path} to {audio_path}...")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",  # Overwrite output files without asking
                    "-i",
                    str(video_path),
                    "-vn",  # No video output
                    "-acodec",
                    "pcm_s16le",  # Standard WAV format
                    "-ar",
                    "16000",  # Audio sample rate
                    "-ac",
                    "1",  # Mono audio
                    str(audio_path),
                ],
                check=True,
            )
            logger.info("Audio extraction complete.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract audio: {e}")
            return False

        # Call Gemini API
        logger.info(f"Calling Gemini API with audio from {audio_path}...")
        try:
            # Read the audio file
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # Create a Part object with the audio data
            audio_part = Part.from_data(mime_type="audio/wav", data=audio_bytes)

            # Initialize the Gemini model
            model = GenerativeModel("gemini-2.0-flash-001")
            logger.info("Using gemini-2.0-flash-001 model")

            # Generate transcript
            logger.info("Generating transcript...")
            transcript_response = model.generate_content(
                [
                    "Generate a transcript of this audio. Format it as plain text with no timestamps or speaker labels.",
                    audio_part,
                ]
            )
            transcript = transcript_response.text

            # Generate subtitles
            logger.info("Generating subtitles...")
            subtitles_response = model.generate_content(
                [
                    "Generate WebVTT subtitles for this audio. Include proper timestamps.",
                    audio_part,
                ]
            )
            subtitles_vtt = subtitles_response.text

            # Generate shownotes
            logger.info("Generating shownotes...")
            shownotes_response = model.generate_content(
                [
                    "Generate detailed shownotes for this audio in Markdown format. Include key points and timestamps.",
                    audio_part,
                ]
            )
            shownotes = shownotes_response.text

            # Generate chapters
            logger.info("Generating chapters...")
            chapters_response = model.generate_content(
                [
                    "Generate chapters for this audio. Format as 'MM:SS - Chapter Title' with one chapter per line.",
                    audio_part,
                ]
            )
            chapters = chapters_response.text

            # Generate title
            logger.info("Generating title...")
            title_response = model.generate_content(
                [
                    "Generate a concise, engaging title for this audio content.",
                    audio_part,
                ]
            )
            title = title_response.text

            logger.info("Gemini API calls complete.")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return False

        # Save the outputs to the processed directory
        base_name = Path(video_file).stem
        processed_dir_name = base_name.replace(" ", "-")
        processed_dir = test_data_dir / "processed-daily" / processed_dir_name
        processed_dir.mkdir(exist_ok=True, parents=True)

        # Write the outputs to files
        logger.info(f"Saving outputs to {processed_dir}...")
        try:
            with open(processed_dir / "transcript.txt", "w") as f:
                f.write(transcript)

            with open(processed_dir / "subtitles.vtt", "w") as f:
                f.write(subtitles_vtt)

            with open(processed_dir / "shownotes.txt", "w") as f:
                f.write(shownotes)

            with open(processed_dir / "chapters.txt", "w") as f:
                f.write(chapters)

            with open(processed_dir / "title.txt", "w") as f:
                f.write(title)

            # Copy the video file to the processed directory
            shutil.copy2(source_video_path, processed_dir / video_file)

            logger.info("All outputs saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Error saving outputs: {e}")
            return False


def display_outputs(video_file):
    """
    Display the outputs generated by the video processor.

    Args:
        video_file: The name of the video file that was processed
    """
    # Define paths
    test_data_dir = Path("test_data")
    video_name = Path(video_file).stem

    # Handle spaces in filenames - the processor replaces spaces with hyphens
    processed_dir_name = video_name.replace(" ", "-")
    processed_dir = test_data_dir / "processed-daily" / processed_dir_name

    # Also try with the original name if the hyphenated version doesn't exist
    if not processed_dir.exists():
        processed_dir = test_data_dir / "processed-daily" / video_name

    # Also check if any directory in processed-daily contains the output files
    if not processed_dir.exists():
        for dir_path in (test_data_dir / "processed-daily").glob("*"):
            if dir_path.is_dir():
                logger.info(f"Found directory: {dir_path}")
                # Check if this directory contains any of the expected output files
                if any(
                    (dir_path / f).exists() for f in ["transcript.txt", "subtitles.vtt"]
                ):
                    processed_dir = dir_path
                    logger.info(f"Found output files in: {processed_dir}")
                    break

    if not processed_dir.exists():
        logger.error(f"No processed directory found for {video_file}")
        return False

    logger.info(f"Displaying outputs from {processed_dir}:")

    # List of output files to display
    output_files = [
        "transcript.txt",
        "subtitles.vtt",
        "shownotes.txt",
        "chapters.txt",
        "title.txt",
    ]

    for file_name in output_files:
        file_path = processed_dir / file_name
        if file_path.exists():
            logger.info(f"\n{'=' * 40}\n{file_name.upper()}\n{'=' * 40}")
            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()
                    print(content)
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        else:
            logger.warning(f"Output file {file_name} not found")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test the Video Processor with real API calls"
    )
    parser.add_argument(
        "--video",
        default="Satya Nadella on Vibe Coding.mp4",
        help="The name of the video file to use for testing",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean the test environment before running the test",
    )
    parser.add_argument(
        "--display-only",
        action="store_true",
        help="Only display outputs from a previous run",
    )

    args = parser.parse_args()

    if args.display_only:
        display_outputs(args.video)
        return

    # Set up the test environment
    if not setup_test_environment(args.video, args.clean):
        logger.error("Failed to set up test environment!")
        sys.exit(1)

    # Process the video with real API calls
    if process_video_with_real_apis(args.video):
        logger.info("Video processing completed successfully!")

        # Display the outputs
        display_outputs(args.video)
    else:
        logger.error("Video processing failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
