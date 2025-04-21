import os
import google_auth_oauthlib.flow
from google.cloud import secretmanager

# --- Configuration ---
# Download this file from Google Cloud Console > APIs & Services > Credentials
# Important: DO NOT COMMIT THIS FILE OR THE GENERATED TOKEN!
CLIENT_SECRETS_FILE = (
    "./docs/client_secret.json"  # Assumes file is in the same directory
)

# The scopes must match exactly what your Cloud Function will need.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# --- Secret Manager Config (Optional: To save the token directly) ---
# Set these if you want the script to attempt saving the token automatically
# Requires google-cloud-secret-manager library and authentication
SAVE_TO_SECRET_MANAGER = False  # Set to True to enable saving
PROJECT_ID = "automations-457120"
# The secret ID where the refresh token should be stored for the DAILY uploader
SECRET_ID_TO_SAVE = "youtube-daily-refresh-token"


def save_refresh_token_to_secret(project_id, secret_id, token):
    """Saves the refresh token to Google Cloud Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}/secrets/{secret_id}"

        # Add a new secret version with the refresh token payload
        response = client.add_secret_version(
            request={
                "parent": parent,
                "payload": {"data": token.encode("UTF-8")},
            }
        )
        print(f"Saved refresh token to secret manager version: {response.name}")
        print(
            f"IMPORTANT: Ensure your Cloud Function service account has the 'Secret Manager Secret Accessor' role for {secret_id}."
        )

    except Exception as e:
        print(f"\nError saving token to Secret Manager for secret '{secret_id}': {e}")
        print("Please save the refresh token manually.")


def main():
    # Check if client secrets file exists
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"Error: Client secrets file not found at '{CLIENT_SECRETS_FILE}'")
        print(
            "Please download it from the Google Cloud Console and place it in this directory."
        )
        return

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )

    # Run the console flow instead of local server
    print("\nStarting console authentication flow...")
    print("Please visit the following URL in your browser:")
    auth_url, _ = flow.authorization_url(prompt="consent")
    print(auth_url)
    print("\nAfter authorizing, Google will provide you with a code.")
    code = input("Enter the authorization code here: ")
    flow.fetch_token(code=code)
    credentials = flow.credentials
    # credentials = flow.run_local_server(port=0) # Old local server method

    # The credentials object now contains the refresh token.
    refresh_token = credentials.refresh_token

    print("\nAuthentication successful!")
    print("-" * 40)
    print(f"Obtained Refresh Token: {refresh_token}")
    print("-" * 40)
    print(
        "\nIMPORTANT: Store this refresh token securely! This token allows offline access."
    )
    print(
        f"You need to store this token in Google Secret Manager under the ID: '{SECRET_ID_TO_SAVE}' (for the daily uploader). Remember to also store the client ID and client secret."
    )

    # Optionally save to Secret Manager
    if SAVE_TO_SECRET_MANAGER and refresh_token:
        print(
            f"\nAttempting to save refresh token to Secret Manager (Secret ID: {SECRET_ID_TO_SAVE})..."
        )
        save_refresh_token_to_secret(PROJECT_ID, SECRET_ID_TO_SAVE, refresh_token)
    else:
        print("\nAutomatic saving to Secret Manager is disabled.")
        print(
            f"Please manually create or update the secret '{SECRET_ID_TO_SAVE}' in project '{PROJECT_ID}' with the refresh token above."
        )


if __name__ == "__main__":
    main()
