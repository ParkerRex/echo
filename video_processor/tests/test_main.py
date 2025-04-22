"""
Tests for the main.py module.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the root directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the main module - authentication is handled by environment variables or mocked in conftest.py
try:
    from video_processor import main
except Exception as e:
    # If there's an authentication error, we'll mock the authentication
    import os
    import sys
    from unittest.mock import patch

    # Mock the authentication
    with patch("google.auth.default", return_value=(None, "automations-457120")):
        from video_processor import main


@pytest.fixture
def mock_process_video_event():
    """Mock for the process_video_event function."""
    return MagicMock()


@pytest.fixture
def test_client(mock_process_video_event):
    """Create a test client for the Flask app with mocked dependencies."""
    # Create a test app with the mock process function
    test_app = main.create_app(process_func=mock_process_video_event)
    test_app.config["TESTING"] = True

    # Create a test client
    with test_app.test_client() as client:
        yield client, mock_process_video_event


@pytest.fixture
def gcs_event_data():
    """Create a sample GCS event data."""
    return {
        "bucket": "test-bucket",
        "name": "daily-raw/test_video.mp4",
        "contentType": "video/mp4",
        "size": "1000000",
    }


def test_handle_gcs_event_success(test_client, gcs_event_data):
    """Test successful handling of a GCS event."""
    client, mock_processor = test_client

    # Create headers that mimic CloudEvent format
    headers = {
        "Ce-Id": "test-event-id",
        "Ce-Type": "google.cloud.storage.object.v1.finalized",
        "Ce-Source": "test-source",
        "Ce-Subject": "test-subject",
    }

    # Send a POST request with the event data
    response = client.post("/", json=gcs_event_data, headers=headers)

    # Check that the response is successful (204 No Content)
    assert response.status_code == 204

    # Verify that process_video_event was called with the correct arguments
    mock_processor.assert_called_once_with(
        gcs_event_data["bucket"], gcs_event_data["name"]
    )


def test_handle_gcs_event_invalid_payload(test_client):
    """Test handling of an invalid event payload."""
    client, _ = test_client

    # Send a POST request with an invalid payload (missing required fields)
    response = client.post(
        "/", json={"invalid": "payload"}, headers={"Ce-Id": "test-event-id"}
    )

    # Check that the response indicates a bad request
    assert response.status_code == 400


def test_handle_gcs_event_processing_error(test_client, gcs_event_data):
    """Test handling of an error during event processing."""
    client, mock_processor = test_client

    # Configure the mock to raise an exception
    mock_processor.side_effect = Exception("Test error")

    # Send a POST request with the event data
    response = client.post("/", json=gcs_event_data, headers={"Ce-Id": "test-event-id"})

    # Check that the response indicates a server error
    assert response.status_code == 500


def test_create_app():
    """Test the create_app function."""
    # Test creating an app with the default processor
    app1 = main.create_app()
    assert app1 is not None

    # Test creating an app with a custom processor
    mock_processor = MagicMock()
    app2 = main.create_app(process_func=mock_processor)
    assert app2 is not None


def test_run_app():
    """Test the run_app function."""
    with patch("video_processor.main.app.run") as mock_run:
        # Call the run_app function
        main.run_app(debug=False)

        # Verify app.run was called with the correct arguments
        mock_run.assert_called_once_with(host="0.0.0.0", port=8080, debug=False)
