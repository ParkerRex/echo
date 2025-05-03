#!/usr/bin/env python3
"""
Local testing script for the Video Processor application.
This script simulates a Cloud Run environment and GCS events locally.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import requests

# Add the parent directory to the path so we can import the video_processor module
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set environment variables for testing
os.environ["TESTING_MODE"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "automations-457120"


def create_mock_gcs_event(bucket_name, file_name):
    """
    Create a mock GCS event payload similar to what Cloud Run would receive.

    Args:
        bucket_name: The name of the GCS bucket
        file_name: The name of the file in the bucket

    Returns:
        dict: A dictionary representing the GCS event
    """
    return {
        "bucket": bucket_name,
        "name": file_name,
        "metageneration": "1",
        "timeCreated": "2023-04-21T10:00:00.000Z",
        "updated": "2023-04-21T10:00:00.000Z",
    }


def send_local_request(event_data, port=8080):
    """
    Send a request to the locally running Flask application.

    Args:
        event_data: The GCS event data to send
        port: The port the Flask app is running on

    Returns:
        requests.Response: The response from the Flask app
    """
    headers = {
        "Content-Type": "application/json",
        "Ce-Id": "test-event-id",
        "Ce-Type": "google.cloud.storage.object.v1.finalized",
        "Ce-Source": "//storage.googleapis.com/projects/_/buckets/{bucket}".format(
            bucket=event_data["bucket"]
        ),
        "Ce-Subject": f"objects/{event_data['name']}",
    }

    url = f"http://localhost:{port}/"
    logger.info(f"Sending request to {url}")
    logger.info(f"Headers: {json.dumps(headers, indent=2)}")
    logger.info(f"Payload: {json.dumps(event_data, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=event_data)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        return response
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to connect to {url}. Is the Flask app running?")
        sys.exit(1)


def run_flask_app(port=8080):
    """
    Run the Flask application in a separate process.
    """
    from video_processor.main import run_app

    logger.info(f"Starting Flask application on port {port}...")
    # Set the PORT environment variable
    os.environ["PORT"] = str(port)
    run_app(debug=True)


def main():
    parser = argparse.ArgumentParser(
        description="Test the Video Processor application locally"
    )
    parser.add_argument(
        "--bucket", default="automations-videos", help="The GCS bucket name"
    )
    parser.add_argument("--file", required=True, help="The file name in the GCS bucket")
    parser.add_argument(
        "--port", type=int, default=8080, help="The port to run the Flask app on"
    )
    parser.add_argument(
        "--run-server",
        action="store_true",
        help="Run the Flask server (otherwise assumes it's already running)",
    )

    args = parser.parse_args()

    if args.run_server:
        # Run the Flask app in this process
        run_flask_app(port=args.port)
    else:
        # Send a request to an already running Flask app
        event_data = create_mock_gcs_event(args.bucket, args.file)
        send_local_request(event_data, args.port)


if __name__ == "__main__":
    main()
