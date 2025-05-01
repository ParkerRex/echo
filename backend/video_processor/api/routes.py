"""
API routes and endpoint definitions.
"""
import json
import logging
from types import SimpleNamespace
from typing import Any, Dict, Optional, Tuple, Union

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from ..config import get_settings
from ..utils.logging import get_logger
from .controllers import (
    handle_gcs_event,
    health_check,
    get_gcs_upload_url,
)

logger = get_logger(__name__)


def create_app(process_video_func: Optional[Any] = None) -> Flask:
    """
    Create and configure a Flask application.
    
    Args:
        process_video_func: Optional function to process video events
            (useful for testing with mock functions)
            
    Returns:
        Configured Flask application instance
    """
    settings = get_settings()
    
    try:
        app = Flask(__name__)
        # Enable CORS for all routes and origins
        CORS(app)
        logger.info("✅ Flask app initialized with CORS enabled")
        
        # Register routes
        _register_routes(app, process_video_func)
        
        return app
    except Exception as e:
        logger.error(f"❌ Error initializing Flask: {e}", exc_info=True)
        raise


def _register_routes(app: Flask, process_video_func: Optional[Any] = None) -> None:
    """
    Register routes with the Flask application.
    
    Args:
        app: Flask application instance
        process_video_func: Optional function to process video events
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
            result, status_code = handle_gcs_event(event, process_video_func)
            return result, status_code
        except Exception as e:
            logger.exception("❌ Error handling POST request")
            return "❌ Failed to handle event.", 500
    
    # GCS upload URL endpoint
    @app.route("/api/gcs-upload-url", methods=["POST"])
    def _get_gcs_upload_url() -> Union[Response, Tuple[Response, int]]:
        try:
            data = request.get_json()
            result = get_gcs_upload_url(data)
            
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
                return result[0], result[1]
            return result
        except Exception as e:
            logger.exception("❌ Error generating GCS signed URL")
            return jsonify({"error": "Failed to generate signed URL"}), 500