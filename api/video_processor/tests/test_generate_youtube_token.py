"""
Tests for the generate_youtube_token.py module.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add the root directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from video_processor import generate_youtube_token


def test_save_refresh_token_to_secret(mock_secretmanager_client):
    """Test saving a refresh token to Secret Manager."""
    with patch(
        "video_processor.generate_youtube_token.secretmanager.SecretManagerServiceClient",
        return_value=mock_secretmanager_client,
    ):
        # Call the function
        generate_youtube_token.save_refresh_token_to_secret(
            "test-project", "test-secret", "test-token"
        )

        # Verify the correct API call was made
        mock_secretmanager_client.add_secret_version.assert_called_once_with(
            request={
                "parent": "projects/test-project/secrets/test-secret",
                "payload": {"data": b"test-token"},
            }
        )


def test_main_client_secrets_not_found():
    """Test main function when client secrets file is not found."""
    # Mock the argument parser
    mock_args = MagicMock()
    mock_args.channel = "daily"
    mock_args.save = False

    with patch("argparse.ArgumentParser.parse_args", return_value=mock_args):
        with patch("os.path.exists", return_value=False):
            with patch("builtins.print") as mock_print:
                # Call the function
                generate_youtube_token.main()

                # Verify error message was printed
                mock_print.assert_any_call(
                    f"\nError: Client secrets file not found at "
                    f"'{generate_youtube_token.CLIENT_SECRETS_FILE}'"
                )


def test_main_successful_flow():
    """Test successful flow of the main function."""
    # Mock the argument parser
    mock_args = MagicMock()
    mock_args.channel = "daily"
    mock_args.save = False

    mock_flow = MagicMock()
    mock_credentials = MagicMock()
    mock_credentials.refresh_token = "test-refresh-token"
    mock_flow.credentials = mock_credentials

    # Mock the authorization URL
    mock_flow.authorization_url.return_value = ("https://example.com/auth", None)

    # Mock the fetch_token method
    mock_flow.fetch_token.return_value = None

    with patch("argparse.ArgumentParser.parse_args", return_value=mock_args):
        with patch("os.path.exists", return_value=True):
            with patch(
                "google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file",
                return_value=mock_flow,
            ):
                with patch("builtins.input", return_value="test-code"):
                    with patch("builtins.print") as mock_print:
                        # Disable auto-saving to Secret Manager
                        with patch.object(
                            generate_youtube_token, "SAVE_TO_SECRET_MANAGER", False
                        ):
                            # Call the function
                            generate_youtube_token.main()

                            # Verify the flow was used correctly
                            mock_flow.authorization_url.assert_called_once_with(
                                prompt="consent"
                            )
                            mock_flow.fetch_token.assert_called_once_with(
                                code="test-code"
                            )

                            # Verify the refresh token was printed
                            mock_print.assert_any_call(
                                "Refresh Token: test-refresh-token"
                            )


def test_main_with_secret_manager_saving():
    """Test main function with saving to Secret Manager enabled."""
    # Mock the argument parser
    mock_args = MagicMock()
    mock_args.channel = "daily"
    mock_args.save = True

    # Create a mock secret ID
    mock_secret_id = "youtube-daily-refresh-token"

    mock_flow = MagicMock()
    mock_credentials = MagicMock()
    mock_credentials.refresh_token = "test-refresh-token"
    mock_flow.credentials = mock_credentials

    # Mock the authorization URL
    mock_flow.authorization_url.return_value = ("https://example.com/auth", None)

    # Mock the fetch_token method
    mock_flow.fetch_token.return_value = None

    with patch("argparse.ArgumentParser.parse_args", return_value=mock_args):
        with patch.dict(generate_youtube_token.SECRET_IDS, {"daily": mock_secret_id}):
            with patch("os.path.exists", return_value=True):
                with patch(
                    "google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file",
                    return_value=mock_flow,
                ):
                    with patch("builtins.input", return_value="test-code"):
                        with patch("builtins.print"):
                            with patch(
                                "video_processor.generate_youtube_token.save_refresh_token_to_secret"
                            ) as mock_save:
                                # Call the function
                                generate_youtube_token.main()

                                # Verify save_refresh_token_to_secret was called
                                mock_save.assert_called_once_with(
                                    generate_youtube_token.PROJECT_ID,
                                    mock_secret_id,
                                    "test-refresh-token",
                                )
