import functions_framework
import requests
import os
import json
from google.cloud import secretmanager

# Environment variables
GCS_BUCKET = os.environ.get("GCS_BUCKET", "automations-youtube-videos-2025")
# AUPHONIC_API_KEY = "e35bDjoTVwmbkApaorRwSoODBRT2zFRk" # Removed hardcoded key
PROJECT_ID = "automations-457120"
SECRET_ID = "auphonic-api-key"

# Auphonic preset UUIDs
PRESETS = {
    "daily": "NUhaRc7Uy3JnLYSjgkzkjN",  # parker.m.rex@gmail.com
    "main": "QKiN23RSfTs2AZUfxteBhT",  # me@parkerrex.com
}

# Auphonic service UUIDs
SERVICES = {
    "daily": "AjyidE9UPGg8EQMz5pNhWG",  # Daily service
    "main": "h7gE2gDMRiyaCoKhxHNiLo",  # Main service
}


def get_secret(secret_id, project_id, version_id="latest"):
    """Retrieves a secret version from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


@functions_framework.cloud_event
def trigger_auphonic(cloud_event):
    """Cloud Function triggered by GCS bucket events to start Auphonic processing."""
    try:
        # Retrieve Auphonic API Key from Secret Manager
        auphonic_api_key = get_secret(SECRET_ID, PROJECT_ID)

        # Log the entire event for debugging
        print(f"Received event: {json.dumps(cloud_event.__dict__, indent=2)}")

        data = cloud_event.data
        # Handle nested data
        if "data" in data and "bucket" in data["data"]:
            print("Warning: Nested data detected, using inner data")
            data = data["data"]

        bucket_name = data.get("bucket")
        file_name = data.get("name")

        if not bucket_name or not file_name:
            print(f"Invalid event data: {json.dumps(data, indent=2)}")
            return

        # Extract base filename to use as video title and folder name
        video_title = os.path.splitext(os.path.basename(file_name))[0]
        # Basic sanitization (replace spaces, ensure no trailing slash)
        video_title_sanitized = video_title.replace(" ", "_").strip("/")

        # Determine preset, service, and structured output folder path
        if file_name.startswith("raw-daily/"):
            preset_uuid = PRESETS["daily"]
            service_uuid = SERVICES["daily"]
            # Create path like processed-daily/video_title_sanitized/
            output_gcs_folder_path = f"processed-daily/{video_title_sanitized}"
        elif file_name.startswith("raw-main/"):
            preset_uuid = PRESETS["main"]
            service_uuid = SERVICES["main"]
            # Create path like processed-main/video_title_sanitized/
            output_gcs_folder_path = f"processed-main/{video_title_sanitized}"
        else:
            print(f"File {file_name} not in raw-daily or raw-main, skipping.")
            return

        # Prepare Auphonic API request using standard JSON endpoint
        # file_path = f"gs://{bucket_name}/{file_name}" # No longer needed, use relative name
        url = "https://auphonic.com/api/productions.json"  # Standard API endpoint
        headers = {
            "Authorization": f"Bearer {auphonic_api_key}",  # Use retrieved key
            "Content-Type": "application/json",  # Specify JSON content type
        }
        payload = {  # Use JSON payload instead of files/form-data
            "preset": preset_uuid,
            "input_file": file_name,  # Use relative object path, not gs:// URI
            "service": service_uuid,  # Specify the GCS external service
            "output_basename": output_gcs_folder_path,  # Use the structured GCS folder path
            "action": "start",
            "title": video_title,  # Use original extracted title
        }

        # Log request details
        print(
            f"Calling Auphonic standard API with: url={url}, payload={json.dumps(payload, indent=2)}"
        )

        # Make API call using JSON payload
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(
            f"Started Auphonic production for {file_name}: {json.dumps(response.json(), indent=2)}"
        )
    except KeyError as e:
        print(f"KeyError: {e}")
        print(f"Event data: {json.dumps(cloud_event.__dict__, indent=2)}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"Failed to start Auphonic production for {file_name}: {e}")
        print(f"Response content: {response.text}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Failed to start Auphonic production for {file_name}: {e}")
        raise
