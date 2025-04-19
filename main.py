import os
import json
import requests
from functions_framework import cloud_event
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


def get_secret(secret_id, project_id):
    print(f"DEBUG: Fetching secret '{secret_id}' from project '{project_id}'")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    secret_value = response.payload.data.decode("UTF-8")
    print("DEBUG: Secret successfully retrieved")
    return secret_value

@cloud_event
def trigger_auphonic(cloud_event):
    print("DEBUG: Function triggered")

    try:
        # Retrieve Auphonic API Key from Secret Manager
        print("DEBUG: Attempting to retrieve Auphonic API key")
        auphonic_api_key = get_secret(SECRET_ID, PROJECT_ID)
        print("DEBUG: Retrieved API key:", auphonic_api_key)

        # Log the entire event for debugging
        print(f"DEBUG: Received event: {json.dumps(cloud_event.__dict__, indent=2)}")

        data = cloud_event.data
        print("DEBUG: Extracted data:", data)

        # Handle nested data
        if "data" in data and "bucket" in data["data"]:
            print("DEBUG: Nested data detected, using inner data")
            data = data["data"]

        bucket_name = data.get("bucket")
        file_name = data.get("name")
        print(f"DEBUG: Bucket: {bucket_name}, File: {file_name}")

        if not bucket_name or not file_name:
            print(f"DEBUG: Invalid event data: {json.dumps(data, indent=2)}")
            return

        # Extract base filename to use as video title and folder name
        video_title = os.path.splitext(os.path.basename(file_name))[0]
        video_title_sanitized = video_title.replace(" ", "_").strip("/")
        print(f"DEBUG: Video title: {video_title}, Sanitized: {video_title_sanitized}")

        # Determine preset, service, and output path
        if file_name.startswith("raw-daily/"):
            preset_uuid = PRESETS["daily"]
            service_uuid = SERVICES["daily"]
            output_gcs_folder_path = f"processed-daily/{video_title_sanitized}"
        elif file_name.startswith("raw-main/"):
            preset_uuid = PRESETS["main"]
            service_uuid = SERVICES["main"]
            output_gcs_folder_path = f"processed-main/{video_title_sanitized}"
        else:
            print(f"DEBUG: File {file_name} not in raw-daily or raw-main, skipping.")
            return

        print(f"DEBUG: Preset UUID: {preset_uuid}, Service UUID: {service_uuid}, Output folder: {output_gcs_folder_path}")

        # Prepare Auphonic API request
        url = "https://auphonic.com/api/productions.json"
        headers = {
            "Authorization": f"Bearer {auphonic_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "preset": preset_uuid,
            "input_file": file_name,
            "service": service_uuid,
            "output_basename": output_gcs_folder_path,
            "action": "start",
            "title": video_title,
        }
        print(f"DEBUG: Calling Auphonic API with: url={url}, payload={json.dumps(payload, indent=2)}")

        # Make API call with error handling
        try:
            response = requests.post(url, headers=headers, json=payload)
            print("DEBUG: Response status:", response.status_code)
            response.raise_for_status()
            print(f"DEBUG: Auphonic response: {json.dumps(response.json(), indent=2)}")
        except requests.exceptions.RequestException as req_err:
            print(f"DEBUG: Request to Auphonic failed: {req_err}")
            raise

    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        raise
