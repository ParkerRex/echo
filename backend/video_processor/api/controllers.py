"""
API endpoint controllers.
"""

from types import SimpleNamespace
from typing import Any, Dict, Optional, Tuple, Union

from flask import Response, jsonify

from video_processor.config import get_settings
from video_processor.services.storage import get_storage_service
from video_processor.utils.error_handling import handle_exceptions
from video_processor.utils.logging import get_logger

logger = get_logger(__name__)


def health_check() -> str:
    """
    Simple health check endpoint.

    Returns:
        Response indicating service is running
    """
    return "✅ Service is up and running."


def handle_gcs_event(
    event: Dict[str, Any], process_video_func: Optional[Any] = None
) -> Tuple[str, int]:
    """
    Handle a GCS event triggered by a file upload.

    Args:
        event: The event data (from request JSON)
        process_video_func: Optional function to process the video event

    Returns:
        Tuple of (response message, status code)
    """
    try:
        # Extract event data based on structure
        if isinstance(event, dict) and "data" in event:
            # Basic check for CloudEvent structure within POST body
            cloud_event_data = event.get("data", event)  # Use inner data if exists
        else:
            # Fallback or handle non-CloudEvent POST
            logger.warning("Received non-standard POST data format.")
            cloud_event_data = event  # Process raw data

        # Ensure data is accessible like an object for process_uploaded_video
        # If process_uploaded_video expects attributes like event.data.bucket
        cloud_event_obj = SimpleNamespace(**cloud_event_data)

        logger.info(
            f"📥 Received event data for: "
            f"{cloud_event_obj.name if hasattr(cloud_event_obj, 'name') else 'Unknown'}"
        )

        # Call the appropriate processor function
        if hasattr(cloud_event_obj, "bucket") and hasattr(cloud_event_obj, "name"):
            # Import here to avoid circular imports
            from video_processor.core.processors.video import process_video_event

            # Use the provided function or the default
            processor = (
                process_video_func
                if process_video_func is not None
                else process_video_event
            )

            # Process the event
            processor(cloud_event_obj.bucket, cloud_event_obj.name)
            return "✅ Event processed.", 200
        else:
            logger.error("cloud_event_obj missing required attributes: bucket, name")
            return "❌ Invalid event payload.", 400
    except Exception as e:
        logger.exception("❌ Error handling GCS event")
        return f"❌ Failed to handle event: {str(e)}", 500


@handle_exceptions(fallback_return=(jsonify({"error": "Internal server error"}), 500))
def get_gcs_upload_url(data: Dict[str, Any]) -> Union[Response, Tuple[Response, int]]:
    """
    Generate a signed URL for uploading a file to GCS.

    Args:
        data: Request data containing filename and content_type

    Returns:
        JSON response with upload URL and file info, or error response
    """
    settings = get_settings()

    # Validate request data
    filename = data.get("filename")
    content_type = data.get("content_type", "video/mp4")

    if not filename:
        return jsonify({"error": "Missing filename"}), 400

    # Get bucket name from settings
    bucket_name = settings.gcs_upload_bucket
    if not bucket_name:
        return jsonify({"error": "GCS bucket not configured"}), 500

    # Generate the upload URL
    storage_service = get_storage_service()
    object_path = f"videos/{filename}"

    try:
        # Generate signed URL for upload (PUT)
        url = storage_service.get_signed_url(
            bucket=bucket_name,
            path=object_path,
            expiration_minutes=15,
            http_method="PUT",
            content_type=content_type,
        )

        # Create GCS URL for later reference
        gcs_url = f"https://storage.googleapis.com/{bucket_name}/{object_path}"

        return (
            jsonify(
                {
                    "url": url,
                    "bucket": bucket_name,
                    "object_path": object_path,
                    "gcs_url": gcs_url,
                }
            ),
            200,
        )
    except Exception as e:
        logger.exception("❌ Error generating GCS signed URL")
        return jsonify({"error": f"Failed to generate signed URL: {str(e)}"}), 500
