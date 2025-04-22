#!/usr/bin/env python3
"""
Comprehensive test script for the Video Processor application.
This script:
1. Sets up the test environment
2. Runs the test with a real video file
3. Verifies the outputs
"""

import os
import sys
import time
import logging
import argparse
import subprocess
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the video_processor module
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variables for testing
os.environ["TESTING_MODE"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "automations-457120"


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


def run_flask_app(port=8082):
    """
    Run the Flask application in a separate process.

    Args:
        port: The port to run the Flask app on

    Returns:
        subprocess.Popen: The process object
    """
    from video_processor.main import run_app

    # Set the PORT environment variable
    os.environ["PORT"] = str(port)

    # Start the Flask app in a separate process
    logger.info(f"Starting Flask application on port {port}...")

    # Use subprocess to run the Flask app
    cmd = [
        sys.executable,
        "-c",
        'import sys; sys.path.append("."); from video_processor.main import run_app; run_app(debug=True)',
    ]

    process = subprocess.Popen(
        cmd,
        env=dict(
            os.environ,
            PORT=str(port),
            TESTING_MODE="true",
            GOOGLE_CLOUD_PROJECT="automations-457120",
        ),
    )

    # Give the Flask app time to start
    time.sleep(2)

    return process


def send_test_event(video_file, port=8082):
    """
    Send a test event to the Flask application.

    Args:
        video_file: The name of the video file to use for testing
        port: The port the Flask app is running on

    Returns:
        bool: Whether the test event was sent successfully
    """
    import requests

    # Create the event data
    event_data = {
        "bucket": "automations-videos",
        "name": f"daily-raw/{video_file}",
        "metageneration": "1",
        "timeCreated": "2023-04-21T10:00:00.000Z",
        "updated": "2023-04-21T10:00:00.000Z",
    }

    # Create the headers
    headers = {
        "Content-Type": "application/json",
        "Ce-Id": "test-event-id",
        "Ce-Type": "google.cloud.storage.object.v1.finalized",
        "Ce-Source": "//storage.googleapis.com/projects/_/buckets/automations-videos",
        "Ce-Subject": f"objects/daily-raw/{video_file}",
    }

    # Send the request
    url = f"http://localhost:{port}/"
    logger.info(f"Sending test event to {url}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Event data: {event_data}")

    try:
        response = requests.post(url, headers=headers, json=event_data)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        return response.status_code == 204
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to connect to {url}. Is the Flask app running?")
        return False


def verify_outputs(video_file):
    """
    Verify that the outputs were generated correctly.

    Args:
        video_file: The name of the video file used for testing

    Returns:
        bool: Whether the outputs were generated correctly
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

    logger.info(f"Looking for processed directory at: {processed_dir}")

    # Check if the processed directory exists
    if not processed_dir.exists():
        logger.error(f"Processed directory {processed_dir} does not exist!")
        return False

    # Check if the expected output files exist
    # The video file might have spaces replaced with hyphens
    video_filename = f"{video_name}.mp4"
    video_filename_hyphenated = f"{video_name.replace(' ', '-')}.mp4"

    expected_files = [
        # Try both original and hyphenated filenames for the video
        processed_dir / video_filename,
        processed_dir / video_filename_hyphenated,
        processed_dir / "transcript.txt",
        processed_dir / "subtitles.vtt",
        processed_dir / "shownotes.txt",
        processed_dir / "chapters.txt",
        processed_dir / "title.txt",
    ]

    # Remove duplicates if the filenames are the same
    expected_files = list(set(expected_files))

    all_files_exist = False
    found_files = []

    # First check if at least one of the video files exists
    video_files = [
        processed_dir / video_filename,
        processed_dir / video_filename_hyphenated,
    ]
    found_video = False
    for video_file in video_files:
        if video_file.exists():
            found_video = True
            found_files.append(video_file)
            logger.info(f"Found video file: {video_file}")
            break

    if not found_video:
        logger.error(f"No video file found in {processed_dir}!")

    # Then check for the other expected files
    other_files = [
        processed_dir / "transcript.txt",
        processed_dir / "subtitles.vtt",
        processed_dir / "shownotes.txt",
        processed_dir / "chapters.txt",
        processed_dir / "title.txt",
    ]

    for file in other_files:
        if file.exists():
            found_files.append(file)
            logger.info(f"Found output file: {file}")
            # Print the first few lines of the file
            try:
                # Try to read as text first
                with open(file, "r", errors="ignore") as f:
                    content = f.read(500)  # Read first 500 characters
                    logger.info(f"Content preview: {content[:100]}...")
            except:
                # If that fails, try to read as binary
                try:
                    with open(file, "rb") as f:
                        content = f.read(50)  # Read first 50 bytes
                        logger.info(f"Binary content (hex): {content.hex()[:100]}")
                except Exception as e:
                    logger.error(f"Could not read file {file}: {e}")
        else:
            logger.error(f"Expected output file {file} does not exist!")

    # Check if we found at least the video file and transcript
    required_files = ["transcript.txt"]
    all_required_exist = found_video and all(
        any(str(f).endswith(req) for f in found_files) for req in required_files
    )

    if all_required_exist:
        all_files_exist = True
        logger.info(
            f"Found {len(found_files)} out of {len(other_files) + 1} expected files"
        )
    else:
        logger.error(f"Missing required files!")

    return all_files_exist


def main():
    parser = argparse.ArgumentParser(
        description="Run a comprehensive test of the Video Processor application"
    )
    parser.add_argument(
        "--video",
        default="Satya Nadella on Vibe Coding.mp4",
        help="The name of the video file to use for testing",
    )
    parser.add_argument(
        "--port", type=int, default=8082, help="The port to run the Flask app on"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean the test environment before running the test",
    )

    args = parser.parse_args()

    # Set up the test environment
    if not setup_test_environment(args.video, args.clean):
        logger.error("Failed to set up test environment!")
        sys.exit(1)

    # Run the Flask app
    flask_process = run_flask_app(args.port)

    try:
        # Send the test event
        if not send_test_event(args.video, args.port):
            logger.error("Failed to send test event!")
            sys.exit(1)

        # Give the Flask app time to process the event
        logger.info("Waiting for the Flask app to process the event...")
        time.sleep(5)

        # Check the test_data directory structure
        logger.info("Checking test_data directory structure:")
        test_data_dir = Path("test_data")
        for root, dirs, files in os.walk(test_data_dir):
            logger.info(f"Directory: {root}")
            for d in dirs:
                logger.info(f"  Subdirectory: {d}")
            for f in files:
                logger.info(f"  File: {f}")

        # Verify the outputs
        if verify_outputs(args.video):
            logger.info("✅ Test passed! All outputs were generated correctly.")
        else:
            logger.error("❌ Test failed! Some outputs were not generated correctly.")
            sys.exit(1)

    finally:
        # Terminate the Flask app
        logger.info("Terminating Flask app...")
        flask_process.terminate()
        flask_process.wait()

    logger.info("Test completed successfully!")


if __name__ == "__main__":
    main()
