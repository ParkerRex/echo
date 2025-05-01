import os
import sys
import argparse
import google_auth_oauthlib.flow
from google.cloud import secretmanager

# --- Configuration ---
# Download this file from Google Cloud Console > APIs & Services > Credentials
# Important: DO NOT COMMIT THIS FILE OR THE GENERATED TOKEN!
CLIENT_SECRETS_FILE = "./credentials/client_secret.json"  # Path to client secrets file

# The scopes must match exactly what your Cloud Function will need.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# --- Secret Manager Config (Optional: To save the token directly) ---
# Set these if you want the script to attempt saving the token automatically
# Requires google-cloud-secret-manager library and authentication
SAVE_TO_SECRET_MANAGER = False  # Set to True to enable saving
PROJECT_ID = "automations-457120"

# Secret IDs for each channel
SECRET_IDS = {"daily": "youtube-daily-refresh-token", "main": "youtube-refresh-token"}


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
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate YouTube OAuth tokens for video uploads"
    )
    parser.add_argument(
        "--channel",
        choices=["daily", "main"],
        default="daily",
        help="The YouTube channel to generate tokens for (daily or main)",
    )
    parser.add_argument(
        "--save", action="store_true", help="Save the token directly to Secret Manager"
    )
    args = parser.parse_args()

    # Set channel and secret ID based on arguments
    channel = args.channel
    secret_id_to_save = SECRET_IDS[channel]
    save_to_secret_manager = args.save or SAVE_TO_SECRET_MANAGER

    # Print header
    print("\n" + "=" * 80)
    print(f"YouTube OAuth Token Generator for {channel.upper()} Channel")
    print("=" * 80)

    # Check if client secrets file exists
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"\nError: Client secrets file not found at '{CLIENT_SECRETS_FILE}'")
        print("\nTo obtain this file:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create an OAuth 2.0 Client ID (Web application type)")
        print("3. Add http://localhost:8080 as an authorized redirect URI")
        print(
            "4. Download the JSON file and save it as 'client_secret.json' in the docs directory"
        )
        return

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )

    # Run the console flow instead of local server
    print("\nStarting OAuth authentication flow...")
    print(
        "\nIMPORTANT: You will need to authenticate with the Google account that owns the YouTube channel."
    )
    print("\nPlease visit the following URL in your browser:")
    auth_url, _ = flow.authorization_url(prompt="consent")
    print(f"\n{auth_url}\n")
    print("After authorizing, Google will provide you with a code.")
    code = input("Enter the authorization code here: ")
    flow.fetch_token(code=code)
    credentials = flow.credentials
    # credentials = flow.run_local_server(port=0) # Old local server method

    # The credentials object now contains the refresh token.
    refresh_token = credentials.refresh_token

    print("\n" + "=" * 40)
    print("Authentication successful!")
    print("=" * 40)
    print(f"\nChannel: {channel.upper()}")
    print(f"Secret ID: {secret_id_to_save}")
    print(f"Refresh Token: {refresh_token}")
    print(
        "\nIMPORTANT: This refresh token allows offline access to your YouTube account."
    )
    print("Keep it secure and do not commit it to version control!")

    # Optionally save to Secret Manager
    if save_to_secret_manager and refresh_token:
        print(f"\nAttempting to save refresh token to Secret Manager...")
        print(f"Project: {PROJECT_ID}")
        print(f"Secret ID: {secret_id_to_save}")
        save_refresh_token_to_secret(PROJECT_ID, secret_id_to_save, refresh_token)
    else:
        print("\nAutomatic saving to Secret Manager is disabled.")
        print("\nTo manually save the token:")
        print(
            f"1. Go to https://console.cloud.google.com/security/secret-manager?project={PROJECT_ID}"
        )
        print(f"2. Create or update the secret '{secret_id_to_save}'")
        print("3. Add a new version with the refresh token as the value")
        print("\nYou'll also need to create/update these secrets:")
        print(
            f"- '{secret_id_to_save.replace('refresh_token', 'client_id')}': The client ID from your OAuth credentials"
        )
        print(
            f"- '{secret_id_to_save.replace('refresh_token', 'client_secret')}': The client secret from your OAuth credentials"
        )


if __name__ == "__main__":
    main()
