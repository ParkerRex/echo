from flask import Flask, request
import os
import json
import logging
from process_uploaded_video import process_uploaded_video
from types import SimpleNamespace

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logging.info("🚀 app.py starting...")

try:
    app = Flask(__name__)
    logging.info("✅ Flask app initialized.")
except Exception as e:
    logging.error(f"❌ Error initializing Flask: {e}")
    raise


@app.route("/", methods=["GET"])
def health_check():
    return "✅ Service is up and running."


@app.route("/", methods=["POST"])
def handle_gcs_event():
    try:
        event = request.get_json()
        # Convert dict to object-like if needed (adjust based on actual event structure)
        # This assumes the event structure received by Cloud Run might differ slightly
        # from the structure Functions Framework expects. Check actual logs if issues arise.
        if isinstance(event, dict) and "data" in event:
            # Basic check for CloudEvent structure within POST body
            cloud_event_data = event.get("data", event)  # Use inner data if exists
        else:
            # Fallback or handle non-CloudEvent POST? Adjust as needed.
            logging.warning("Received non-standard POST data format.")
            cloud_event_data = event  # Process raw data?

        # Ensure data is accessible like an object for process_uploaded_video
        # If process_uploaded_video expects attributes like event.data.bucket
        cloud_event_obj = SimpleNamespace(**cloud_event_data)

        logging.info(
            f"📥 Received event data for: {cloud_event_obj.name if hasattr(cloud_event_obj, 'name') else 'Unknown'}"
        )
        # print("Received CloudEvent:") # Redundant if logging works
        # print(json.dumps(event, indent=2)) # Avoid printing potentially large events

        # ✅ Call your actual processor
        process_uploaded_video(cloud_event_obj)  # Pass the object-like data

        return "✅ Event processed.", 200
    except Exception as e:
        logging.exception(
            "❌ Error handling POST request:"
        )  # Use logging.exception for traceback
        return "❌ Failed to handle event.", 500


# --- Add this block for debugging ---
if __name__ == "__main__":
    logging.info("🏁 Attempting to run Flask development server...")
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=True)
        logging.info(
            f"Flask server should be running on port {port}"
        )  # This might not be reached if run blocks
    except Exception as e:
        logging.exception(
            "❌ Failed to start Flask development server:"
        )  # Log exception traceback
        raise
# --- End of added block ---
