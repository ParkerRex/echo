import os
import json
import logging
from flask import Flask, request
from typing import Callable, Optional, Tuple, Any

# Import the process_video_event function
from .process_uploaded_video import process_video_event

# Configure logging
logging.basicConfig(level=logging.INFO)


def create_app(process_func: Optional[Callable] = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        process_func: Optional function to use for processing video events.
                     Useful for testing with a mock function.

    Returns:
        Flask application instance
    """
    flask_app = Flask(__name__)

    # Use the provided process function or default to the real one
    video_processor = process_func if process_func is not None else process_video_event

    @flask_app.route("/", methods=["POST"])
    def handle_gcs_event():
        """Handles incoming CloudEvents from GCS via Eventarc/Cloud Run."""
        event_id = request.headers.get("Ce-Id")
        event_type = request.headers.get("Ce-Type")
        event_source = request.headers.get("Ce-Source")
        event_subject = request.headers.get("Ce-Subject")

        logging.info(
            f"Received CloudEvent: ID={event_id}, Type={event_type}, Source={event_source}, Subject={event_subject}"
        )

        try:
            # Get the JSON payload (CloudEvent data)
            event_data = request.get_json()

            if not event_data or "bucket" not in event_data or "name" not in event_data:
                logging.error(f"Invalid event payload: {json.dumps(event_data)}")
                return ("Invalid event payload", 400)

            bucket = event_data["bucket"]
            name = event_data["name"]

            logging.info(f"Processing gs://{bucket}/{name}")

            # Call the core processing function using the injected or default processor
            video_processor(bucket, name)

            logging.info(f"Successfully processed gs://{bucket}/{name}")
            # Return 2xx response to acknowledge the event
            return ("", 204)

        except Exception as e:
            logging.error(
                f"Error processing event for {event_subject}: {e}", exc_info=True
            )
            # Return 500 to indicate failure, potentially causing Eventarc to retry
            return ("Internal Server Error", 500)

    return flask_app


# Create the application instance
app = create_app()


def run_app(debug=True):
    """Run the Flask application for local development.

    Args:
        debug: Whether to run the app in debug mode
    """
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    # This section is for local development testing
    # Gunicorn will directly run the 'app' object in production
    run_app(debug=True)
