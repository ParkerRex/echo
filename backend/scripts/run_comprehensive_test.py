#!/usr/bin/env python3
"""
Comprehensive test script for the Video Processor application.
This script:
1. Sets up the test environment
2. Runs the test with a real video file
3. Verifies the outputs
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
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
    Set up the test environment by creating the necessary directories and
    copying the test video file.

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

    # Set the PORT environment variable
    os.environ["PORT"] = str(port)

    # Start the Flask app in a separate process
    logger.info(f"Starting Flask application on port {port}...")

    # Use subprocess to run the Flask app
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            'import sys; sys.path.append("."); '
            "from video_processor.main import run_app; "
            "run_app(debug=True)",
        ],
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


def check_output_file(file_path, file_type):
    """
    Check if an output file exists and log its status.

    Args:
        file_path: Path to the file to check
        file_type: Description of the file type for logging

    Returns:
        bool: True if file exists and is not empty
    """
    logger.info(f"Checking for {file_type} file: {file_path}")
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ {file_type} file not found")
        return False

    file_size = os.path.getsize(file_path)
    if file_size == 0:
        logger.warning(f"⚠️ {file_type} file is empty")
        return False

    logger.info(f"✅ {file_type} file exists ({file_size} bytes)")
    return True


def preview_file_content(file, logger):
    """
    Try to preview the content of a file and log the first part of it.

    Args:
        file: Path to the file to preview
        logger: Logger instance to use for logging
    """
    try:
        with open(file, "r") as f:
            content = f.read(500)  # Read first 500 characters
            logger.info(f"Content preview: {content[:100]}...")
    except Exception:
        # If that fails, try to read as binary
        try:
            with open(file, "rb") as f:
                content = f.read(100)  # Just read a bit in binary mode
                logger.info(f"Binary content (hex): {content.hex()[:100]}")
        except Exception as e:
            logger.error(f"Could not read file: {e}")


def verify_outputs(video_file):
    """
    Verify that the outputs were generated correctly.

    Args:
        video_file: Path to the input video file

    Returns:
        bool: True if all required outputs were found
    """
    logger.info("Verifying outputs...")

    # Extract base name from the video file
    base_name = os.path.basename(video_file).rsplit(".", 1)[0]

    # Define output paths
    output_dir = os.path.join("outputs", base_name)

    if not os.path.exists(output_dir):
        logger.error(f"❌ Output directory not found: {output_dir}")
        return False

    logger.info(f"Output directory: {output_dir}")

    # List of required output files and their types
    required_outputs = [
        (os.path.join(output_dir, "audio.wav"), "Audio"),
        (os.path.join(output_dir, "transcript.txt"), "Transcript"),
        (os.path.join(output_dir, "subtitles.vtt"), "Subtitles"),
        (os.path.join(output_dir, "shownotes.md"), "Shownotes"),
        (os.path.join(output_dir, "chapters.json"), "Chapters"),
        (os.path.join(output_dir, "metadata.json"), "Metadata"),
    ]

    # Check all required output files
    missing_files = 0
    for output_file, file_type in required_outputs:
        if not check_output_file(output_file, file_type):
            missing_files += 1

    if missing_files > 0:
        logger.warning(f"⚠️ {missing_files} required output files are missing")

    # Check processed video files
    processed_daily_dir = os.path.join(output_dir, "processed-daily", base_name)
    processed_main_dir = os.path.join(output_dir, "processed-main", base_name)

    total_files = 0
    for directory in [processed_daily_dir, processed_main_dir]:
        if os.path.exists(directory):
            files = os.listdir(directory)
            logger.info(f"Files in {directory}: {files}")
            total_files += len(files)

            # Preview content of some key files
            for file in files:
                if (
                    file.endswith(".txt")
                    or file.endswith(".vtt")
                    or file.endswith(".json")
                ):
                    file_path = os.path.join(directory, file)
                    logger.info(f"Previewing {file_path}")
                    preview_file_content(file_path, logger)

    if total_files == 0:
        logger.warning("⚠️ No processed files found")
    else:
        logger.info(f"✅ Found {total_files} processed files")

    # Return success if we found at least some outputs
    success = missing_files == 0 and total_files > 0
    logger.info(f"Verification {'succeeded' if success else 'failed'}")
    return success


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
