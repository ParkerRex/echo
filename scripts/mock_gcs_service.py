#!/usr/bin/env python3
"""
Mock GCS service for local testing.
This service simulates GCS events and sends them to the video processor.
"""

import os
import json
import logging
import argparse
import requests
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Default configuration
VIDEO_PROCESSOR_URL = os.environ.get(
    "VIDEO_PROCESSOR_URL", "http://video-processor:8080"
)
TEST_DATA_DIR = os.environ.get("TEST_DATA_DIR", "/app/test_data")

# Add environment variables for testing
os.environ["TESTING_MODE"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "automations-457120"

# Mock Google Cloud libraries
from unittest.mock import MagicMock
import sys

sys.modules["google.cloud.storage"] = MagicMock()
sys.modules["google.cloud.aiplatform"] = MagicMock()
sys.modules["vertexai"] = MagicMock()


def create_gcs_event(bucket_name, file_name):
    """
    Create a GCS event payload similar to what Cloud Run would receive.

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


def send_event_to_processor(event_data):
    """
    Send a GCS event to the video processor.

    Args:
        event_data: The GCS event data to send

    Returns:
        requests.Response: The response from the video processor
    """
    headers = {
        "Content-Type": "application/json",
        "Ce-Id": "test-event-id",
        "Ce-Type": "google.cloud.storage.object.v1.finalized",
        "Ce-Source": f"//storage.googleapis.com/projects/_/buckets/{event_data['bucket']}",
        "Ce-Subject": f"objects/{event_data['name']}",
    }

    logger.info(f"Sending event to {VIDEO_PROCESSOR_URL}")
    logger.info(f"Headers: {json.dumps(headers, indent=2)}")
    logger.info(f"Payload: {json.dumps(event_data, indent=2)}")

    try:
        response = requests.post(VIDEO_PROCESSOR_URL, headers=headers, json=event_data)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        return response
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to {VIDEO_PROCESSOR_URL}: {e}")
        return None


@app.route("/", methods=["GET"])
def index():
    """Root endpoint that returns information about the mock service."""
    return jsonify(
        {
            "service": "Mock GCS Service",
            "description": "Simulates GCS events for local testing",
            "endpoints": {
                "/trigger": "POST - Trigger a GCS event",
                "/list-test-files": "GET - List available test files",
            },
        }
    )


@app.route("/trigger", methods=["POST"])
def trigger_event():
    """Endpoint to trigger a GCS event."""
    data = request.get_json()

    if not data or "bucket" not in data or "name" not in data:
        return jsonify({"error": "Invalid request. Required fields: bucket, name"}), 400

    bucket = data["bucket"]
    name = data["name"]

    event_data = create_gcs_event(bucket, name)
    response = send_event_to_processor(event_data)

    if response:
        return jsonify(
            {
                "success": True,
                "message": f"Event sent for gs://{bucket}/{name}",
                "processor_status_code": response.status_code,
                "processor_response": response.text,
            }
        )
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Failed to send event for gs://{bucket}/{name}",
                }
            ),
            500,
        )


@app.route("/list-test-files", methods=["GET"])
def list_test_files():
    """Endpoint to list available test files."""
    try:
        files = os.listdir(TEST_DATA_DIR)
        return jsonify({"test_files": files})
    except Exception as e:
        return jsonify({"error": f"Failed to list test files: {str(e)}"}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock GCS service for local testing")
    parser.add_argument(
        "--port", type=int, default=8081, help="Port to run the service on"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the service on")

    args = parser.parse_args()

    logger.info(f"Starting mock GCS service on {args.host}:{args.port}")
    logger.info(f"Video processor URL: {VIDEO_PROCESSOR_URL}")
    logger.info(f"Test data directory: {TEST_DATA_DIR}")

    app.run(host=args.host, port=args.port, debug=True)
