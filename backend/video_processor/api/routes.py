"""
API routes and endpoint definitions.
"""

from typing import Tuple, Union

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from video_processor.utils.logging import get_logger

from .controllers import (
    get_gcs_upload_url,
    handle_gcs_event,
    health_check,
)

logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Create and configure a Flask application instance.

    Returns:
        Configured Flask application instance
    """
    # Use settings if needed later
    # settings = get_settings()

    try:
        # Create Flask app
        app = Flask(__name__)
        # Enable CORS for all routes and origins
        CORS(app)
        logger.info("✅ Flask app initialized with CORS enabled")

        # Register routes
        _register_routes(app)

        return app
    except Exception as e:
        logger.error(f"❌ Error initializing Flask: {e}", exc_info=True)
        raise


def _register_routes(app: Flask) -> None:
    """
    Register routes with the Flask application.
    """

    # Health check endpoint
    @app.route("/", methods=["GET"])
    def _health_check() -> str:
        return health_check()

    # GCS event handler endpoint
    @app.route("/", methods=["POST"])
    def _handle_gcs_event() -> Tuple[str, int]:
        try:
            event = request.get_json()

            # Extract CloudEvent headers for structured event handling
            event_id = request.headers.get("Ce-Id")
            event_type = request.headers.get("Ce-Type")
            event_source = request.headers.get("Ce-Source")
            event_subject = request.headers.get("Ce-Subject")

            if event_id:
                logger.info(
                    f"Received CloudEvent: ID={event_id}, Type={event_type}, "
                    f"Source={event_source}, Subject={event_subject}"
                )

            # Process the event
            result, status_code = handle_gcs_event(event)
            return result, status_code
        except Exception:
            logger.exception("❌ Error handling POST request")
            return "❌ Failed to handle event.", 500

    # GCS upload URL endpoint
    @app.route("/api/gcs-upload-url", methods=["POST"])
    def _get_gcs_upload_url() -> Union[Response, Tuple[Response, int]]:
        try:
            data = request.get_json()
            result = get_gcs_upload_url(data)

            if (
                isinstance(result, tuple)
                and len(result) == 2
                and isinstance(result[1], int)
            ):
                return result[0], result[1]
            return result
        except Exception:
            logger.exception("❌ Error generating GCS signed URL")
            return jsonify({"error": "Failed to generate signed URL"}), 500
