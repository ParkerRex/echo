"""
YouTube authentication utilities.

This module provides utilities for YouTube OAuth authentication and token management.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from video_processor.domain.exceptions import PublishingError

# Configure logger
logger = logging.getLogger(__name__)

# YouTube API constants
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def get_youtube_auth_url(
    client_secrets_file: str,
    scopes: Optional[List[str]] = None,
    redirect_uri: str = "http://localhost:8080",
) -> str:
    """
    Generate a YouTube authentication URL.

    Args:
        client_secrets_file: Path to the client secrets file
        scopes: List of OAuth scopes (default: upload and read)
        redirect_uri: OAuth redirect URI

    Returns:
        Authentication URL for the user to visit

    Raises:
        PublishingError: If the URL generation fails
    """
    try:
        scopes = scopes or DEFAULT_SCOPES

        # Create flow instance to manage OAuth 2.0 authorization flow
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file, scopes=scopes
        )

        # Set redirect URI
        flow.redirect_uri = redirect_uri

        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type="offline", prompt="consent", include_granted_scopes="true"
        )

        return auth_url

    except Exception as e:
        logger.error(f"Failed to generate YouTube auth URL: {str(e)}")
        raise PublishingError(f"Failed to generate YouTube auth URL: {str(e)}")


def exchange_code_for_token(
    client_secrets_file: str,
    code: str,
    redirect_uri: str = "http://localhost:8080",
    scopes: Optional[List[str]] = None,
    token_file: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Exchange an authorization code for OAuth tokens.

    Args:
        client_secrets_file: Path to the client secrets file
        code: Authorization code from callback
        redirect_uri: OAuth redirect URI
        scopes: List of OAuth scopes (default: upload and read)
        token_file: Path to save the token (optional)

    Returns:
        Dictionary containing token information

    Raises:
        PublishingError: If the token exchange fails
    """
    try:
        scopes = scopes or DEFAULT_SCOPES

        # Create flow instance to manage OAuth 2.0 authorization flow
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file, scopes=scopes
        )

        # Set redirect URI
        flow.redirect_uri = redirect_uri

        # Exchange authorization code for access and refresh tokens
        flow.fetch_token(code=code)

        # Get credentials from flow
        credentials = flow.credentials

        # Convert credentials to a dictionary
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        # Save token to file if specified
        if token_file:
            save_token(token_data, token_file)

        return token_data

    except Exception as e:
        logger.error(f"Failed to exchange code for token: {str(e)}")
        raise PublishingError(f"Failed to exchange code for token: {str(e)}")


def save_token(token_data: Dict[str, Any], token_file: str) -> None:
    """
    Save token data to a file.

    Args:
        token_data: Dictionary containing token information
        token_file: Path to save the token

    Raises:
        PublishingError: If saving the token fails
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(token_file)), exist_ok=True)

        # Write token data to file
        with open(token_file, "w") as f:
            json.dump(token_data, f, indent=2)

        logger.info(f"Token saved to {token_file}")

    except Exception as e:
        logger.error(f"Failed to save token to {token_file}: {str(e)}")
        raise PublishingError(f"Failed to save token: {str(e)}")


def load_token(token_file: str) -> Dict[str, Any]:
    """
    Load token data from a file.

    Args:
        token_file: Path to the token file

    Returns:
        Dictionary containing token information

    Raises:
        PublishingError: If loading the token fails
    """
    try:
        if not os.path.exists(token_file):
            raise PublishingError(f"Token file not found: {token_file}")

        # Read token data from file
        with open(token_file, "r") as f:
            token_data = json.load(f)

        logger.info(f"Token loaded from {token_file}")
        return token_data

    except Exception as e:
        logger.error(f"Failed to load token from {token_file}: {str(e)}")
        raise PublishingError(f"Failed to load token: {str(e)}")


def refresh_token(token_file: str) -> Dict[str, Any]:
    """
    Refresh an OAuth token and update the token file.

    Args:
        token_file: Path to the token file

    Returns:
        Updated dictionary containing token information

    Raises:
        PublishingError: If refreshing the token fails
    """
    try:
        # Load current token data
        token_data = load_token(token_file)

        # Create credentials object
        credentials = google.oauth2.credentials.Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get(
                "token_uri", "https://oauth2.googleapis.com/token"
            ),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes", DEFAULT_SCOPES),
        )

        # Refresh token
        credentials.refresh(Request())

        # Update token data
        token_data["token"] = credentials.token

        # Save updated token
        save_token(token_data, token_file)

        logger.info("Token refreshed successfully")
        return token_data

    except RefreshError as e:
        logger.error(f"Failed to refresh token, authentication required: {str(e)}")
        raise PublishingError(
            f"Failed to refresh token, re-authentication required: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        raise PublishingError(f"Failed to refresh token: {str(e)}")


def get_authenticated_service(
    token_file: str,
    auto_refresh: bool = True,
    api_service_name: str = YOUTUBE_API_SERVICE_NAME,
    api_version: str = YOUTUBE_API_VERSION,
) -> Any:
    """
    Build an authenticated YouTube API service.

    Args:
        token_file: Path to the token file
        auto_refresh: Whether to automatically refresh the token if expired
        api_service_name: YouTube API service name
        api_version: YouTube API version

    Returns:
        Authenticated YouTube API service

    Raises:
        PublishingError: If authentication fails
    """
    try:
        # Load token data
        token_data = load_token(token_file)

        # Create credentials object
        credentials = google.oauth2.credentials.Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get(
                "token_uri", "https://oauth2.googleapis.com/token"
            ),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes", DEFAULT_SCOPES),
        )

        # Check if token is expired and refresh if needed
        if auto_refresh and not credentials.valid:
            try:
                credentials.refresh(Request())

                # Update token file with refreshed token
                token_data["token"] = credentials.token
                save_token(token_data, token_file)

                logger.info("Token refreshed automatically")

            except RefreshError as e:
                logger.error(
                    f"Failed to refresh token, authentication required: {str(e)}"
                )
                raise PublishingError(
                    f"Token expired and cannot be refreshed. Please re-authenticate: {str(e)}"
                )

        # Build and return authenticated service
        service = build(
            api_service_name,
            api_version,
            credentials=credentials,
            cache_discovery=False,
        )

        logger.info(f"Authenticated {api_service_name} service created")
        return service

    except Exception as e:
        logger.error(f"Failed to create authenticated service: {str(e)}")
        raise PublishingError(f"Failed to create authenticated service: {str(e)}")
