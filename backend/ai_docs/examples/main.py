"""
Main application entry point.

This module serves as the entry point for the video processing application.
It sets up the dependency injection container, configures services, and
provides the main Cloud Function handler for processing video events.
"""

import logging
import os
from typing import Any, Dict

import functions_framework

from video_processor.application.services.video_processor import VideoProcessorService
from video_processor.domain.models.job import JobStatus
from video_processor.infrastructure.config.container import create_container

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configure testing mode
TESTING_MODE = os.environ.get("TESTING_MODE", "false").lower() == "true"
LOCAL_OUTPUT = os.environ.get("LOCAL_OUTPUT", "false").lower() == "true" or TESTING_MODE

# Create and configure the dependency injection container
container = create_container(testing=TESTING_MODE, local_storage=LOCAL_OUTPUT)

# Get the video processor service from the container
video_processor_service = container.get(VideoProcessorService)


@functions_framework.cloud_event
async def process_video_event(cloud_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cloud Function handler for processing video events.

    This function is triggered by GCS events when a new video is uploaded.
    It extracts metadata from the event and delegates to the video processor
    service for actual processing.

    Args:
        cloud_event: GCS event data

    Returns:
        A dictionary with processing results
    """
    try:
        logger.info(f"Received event: {cloud_event.id}")

        # Extract bucket and file information from the event
        bucket = cloud_event.data["bucket"]
        file_name = cloud_event.data["name"]

        logger.info(f"Processing video: gs://{bucket}/{file_name}")

        # Check if we should process this file
        if not await video_processor_service.should_process(bucket, file_name):
            logger.info(f"Skipping file {file_name} (not a video or already processed)")
            return {"status": "skipped", "file": file_name}

        # Start processing job
        job = await video_processor_service.create_job(bucket, file_name)
        job_id = job.id

        logger.info(f"Created processing job {job_id} for {file_name}")

        # Process the video asynchronously
        # In a production environment, this would typically be offloaded to a task queue
        # or background worker to avoid Cloud Function timeout limits
        processing_result = await video_processor_service.process(job_id)

        if processing_result.status == JobStatus.COMPLETED:
            logger.info(f"Successfully processed {file_name}")
            return {
                "status": "success",
                "job_id": job_id,
                "file": file_name,
                "outputs": processing_result.output_paths,
            }
        else:
            logger.error(f"Failed to process {file_name}: {processing_result.error}")
            return {
                "status": "error",
                "job_id": job_id,
                "file": file_name,
                "error": processing_result.error,
            }

    except Exception as e:
        logger.exception(f"Error processing event: {e}")
        return {"status": "error", "error": str(e)}


@functions_framework.http
async def process_video_http(request):
    """
    HTTP endpoint for triggering video processing.

    This function allows manual triggering of video processing via HTTP
    requests, primarily used for testing or administrative purposes.

    Args:
        request: Flask request object

    Returns:
        Flask response with processing results
    """
    try:
        # Extract bucket and file from request parameters
        request_json = request.get_json(silent=True)

        if not request_json:
            return {"error": "No JSON data provided"}, 400

        bucket = request_json.get("bucket")
        file_name = request_json.get("file")

        if not bucket or not file_name:
            return {"error": "Missing required parameters (bucket, file)"}, 400

        logger.info(f"HTTP trigger for processing: gs://{bucket}/{file_name}")

        # Create a synthetic cloud event and process it
        cloud_event = {
            "id": "manual-trigger",
            "data": {"bucket": bucket, "name": file_name},
        }

        result = await process_video_event(cloud_event)
        return result, 200

    except Exception as e:
        logger.exception(f"Error in HTTP handler: {e}")
        return {"status": "error", "error": str(e)}, 500


if __name__ == "__main__":
    """
    Local development entry point.

    This block is executed when the script is run directly (not as a Cloud Function).
    It provides a way to test the processing logic locally.
    """
    import asyncio
    import sys

    if len(sys.argv) < 3:
        print("Usage: python main.py <bucket_name> <file_name>")
        sys.exit(1)

    bucket = sys.argv[1]
    file_name = sys.argv[2]

    # Create synthetic event for local testing
    test_event = {"id": "local-test", "data": {"bucket": bucket, "name": file_name}}

    # Configure more verbose logging for local testing
    logging.basicConfig(level=logging.DEBUG)

    # Run the event handler
    result = asyncio.run(process_video_event(test_event))
    print(f"Processing result: {result}")
