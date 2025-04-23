#!/usr/bin/env python3
"""
Script to set up YouTube API secrets in Google Cloud Secret Manager.
This script helps create or update the necessary secrets for the YouTube uploader.
"""

import os
import argparse
import json
from google.cloud import secretmanager

# Project ID
PROJECT_ID = "automations-457120"

# Secret IDs for each channel
DAILY_SECRETS = {
    "client_id": "youtube-daily-client-id",
    "client_secret": "youtube-daily-client-secret",
    "refresh_token": "youtube-daily-refresh-token",
}

MAIN_SECRETS = {
    "client_id": "youtube-main-client-id",
    "client_secret": "youtube-main-client-secret",
    "refresh_token": "youtube-refresh-token",
}


def create_or_update_secret(project_id, secret_id, secret_value):
    """Creates a new secret or updates an existing one in Secret Manager.

    Args:
        project_id: Google Cloud project ID
        secret_id: ID of the secret to create or update
        secret_value: Value to store in the secret

    Returns:
        bool: True if successful, False otherwise
    """
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    # Check if the secret already exists
    try:
        secret_path = f"{parent}/secrets/{secret_id}"
        client.get_secret(request={"name": secret_path})
        secret_exists = True
        print(f"Secret {secret_id} already exists.")
    except Exception:
        secret_exists = False
        print(f"Secret {secret_id} does not exist yet.")

    try:
        # Create the secret if it doesn't exist
        if not secret_exists:
            print(f"Creating secret {secret_id}...")
            client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )

        # Add the new secret version
        print(f"Adding new version to secret {secret_id}...")
        response = client.add_secret_version(
            request={
                "parent": f"{parent}/secrets/{secret_id}",
                "payload": {"data": secret_value.encode("UTF-8")},
            }
        )
        print(f"Added secret version: {response.name}")
        return True
    except Exception as e:
        print(f"Error creating/updating secret {secret_id}: {e}")
        return False


def setup_channel_secrets(channel, client_id, client_secret, refresh_token):
    """Sets up all secrets for a specific channel.

    Args:
        channel: Channel name ('daily' or 'main')
        client_id: OAuth client ID
        client_secret: OAuth client secret
        refresh_token: OAuth refresh token

    Returns:
        bool: True if all secrets were set up successfully, False otherwise
    """
    secrets = DAILY_SECRETS if channel == "daily" else MAIN_SECRETS

    success = True

    # Set up client ID
    if client_id:
        if not create_or_update_secret(PROJECT_ID, secrets["client_id"], client_id):
            success = False

    # Set up client secret
    if client_secret:
        if not create_or_update_secret(
            PROJECT_ID, secrets["client_secret"], client_secret
        ):
            success = False

    # Set up refresh token
    if refresh_token:
        if not create_or_update_secret(
            PROJECT_ID, secrets["refresh_token"], refresh_token
        ):
            success = False

    return success


def load_client_secrets(file_path):
    """Loads client ID and secret from a client_secret.json file.

    Args:
        file_path: Path to the client_secret.json file

    Returns:
        tuple: (client_id, client_secret) or (None, None) if loading fails
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        # Extract client ID and secret based on the file format
        if "web" in data:
            return data["web"]["client_id"], data["web"]["client_secret"]
        elif "installed" in data:
            return data["installed"]["client_id"], data["installed"]["client_secret"]
        else:
            print(f"Unknown format in {file_path}")
            return None, None
    except Exception as e:
        print(f"Error loading client secrets from {file_path}: {e}")
        return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Set up YouTube API secrets in Secret Manager"
    )
    parser.add_argument(
        "--channel",
        choices=["daily", "main", "both"],
        default="both",
        help="Which channel to set up secrets for",
    )
    parser.add_argument(
        "--client-secrets-file",
        help="Path to client_secret.json file from Google Cloud Console",
    )
    parser.add_argument("--client-id", help="OAuth client ID")
    parser.add_argument("--client-secret", help="OAuth client secret")
    parser.add_argument("--refresh-token", help="OAuth refresh token")

    args = parser.parse_args()

    # Load client ID and secret from file if provided
    client_id = args.client_id
    client_secret = args.client_secret

    if args.client_secrets_file:
        file_client_id, file_client_secret = load_client_secrets(
            args.client_secrets_file
        )
        if file_client_id and file_client_secret:
            client_id = client_id or file_client_id
            client_secret = client_secret or file_client_secret

    # Check if we have at least one value to set
    if not any([client_id, client_secret, args.refresh_token]):
        print("Error: No values provided to store in Secret Manager.")
        print(
            "Please provide at least one of: --client-id, --client-secret, --refresh-token, or --client-secrets-file"
        )
        return 1

    # Set up secrets for the specified channel(s)
    if args.channel in ["daily", "both"]:
        print("\n=== Setting up secrets for DAILY channel ===")
        if setup_channel_secrets("daily", client_id, client_secret, args.refresh_token):
            print("✅ Successfully set up secrets for DAILY channel")
        else:
            print("❌ Failed to set up some secrets for DAILY channel")

    if args.channel in ["main", "both"]:
        print("\n=== Setting up secrets for MAIN channel ===")
        if setup_channel_secrets("main", client_id, client_secret, args.refresh_token):
            print("✅ Successfully set up secrets for MAIN channel")
        else:
            print("❌ Failed to set up some secrets for MAIN channel")

    return 0


if __name__ == "__main__":
    exit(main())
