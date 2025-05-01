"""
Unit tests for the API module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import json

from video_processor.api.routes import create_app
from video_processor.api.controllers import health_check, handle_gcs_event, get_gcs_upload_url


def test_health_check():
    """Test health_check endpoint."""
    response = health_check()
    assert "up and running" in response


def test_handle_gcs_event_success():
    """Test handle_gcs_event with successful processing."""
    # Create event data
    event_data = {
        "bucket": "test-bucket",
        "name": "daily-raw/test_video.mp4"
    }
    
    # Mock processor function
    mock_processor = MagicMock()
    
    # Call the function
    result, status_code = handle_gcs_event(event_data, mock_processor)
    
    # Verify result
    assert status_code == 200
    assert "processed" in result
    
    # Verify processor was called
    mock_processor.assert_called_once_with("test-bucket", "daily-raw/test_video.mp4")


def test_handle_gcs_event_invalid_data():
    """Test handle_gcs_event with invalid event data."""
    # Create invalid event data (missing required fields)
    event_data = {
        "some_field": "some_value"
    }
    
    # Call the function
    result, status_code = handle_gcs_event(event_data, None)
    
    # Verify result
    assert status_code == 400
    assert "Invalid" in result


def test_handle_gcs_event_processor_error():
    """Test handle_gcs_event with processor error."""
    # Create event data
    event_data = {
        "bucket": "test-bucket",
        "name": "daily-raw/test_video.mp4"
    }
    
    # Mock processor function that raises an exception
    mock_processor = MagicMock()
    mock_processor.side_effect = Exception("Test error")
    
    # Call the function
    result, status_code = handle_gcs_event(event_data, mock_processor)
    
    # Verify result
    assert status_code == 500
    assert "Failed" in result


@patch("video_processor.api.controllers.get_storage_service")
@patch("video_processor.api.controllers.get_settings")
def test_get_gcs_upload_url_success(mock_get_settings, mock_get_storage_service):
    """Test get_gcs_upload_url with successful URL generation."""
    # Create request data
    request_data = {
        "filename": "test_video.mp4",
        "content_type": "video/mp4"
    }
    
    # Mock settings
    mock_settings_instance = MagicMock()
    mock_settings_instance.gcs_upload_bucket = "test-bucket"
    mock_get_settings.return_value = mock_settings_instance
    
    # Mock storage service
    mock_storage_service_instance = MagicMock()
    mock_storage_service_instance.get_signed_url.return_value = "https://test-signed-url.com"
    mock_get_storage_service.return_value = mock_storage_service_instance
    
    # Call the function
    response = get_gcs_upload_url(request_data)
    
    # Verify response
    assert response.status_code == 200
    
    # Parse response JSON
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data["url"] == "https://test-signed-url.com"
    assert response_data["bucket"] == "test-bucket"
    assert "videos/test_video.mp4" in response_data["object_path"]
    
    # Verify storage service was called
    mock_storage_service_instance.get_signed_url.assert_called_once()
    call_args = mock_storage_service_instance.get_signed_url.call_args[1]
    assert call_args["bucket"] == "test-bucket"
    assert call_args["path"] == "videos/test_video.mp4"
    assert call_args["http_method"] == "PUT"
    assert call_args["content_type"] == "video/mp4"


@patch("video_processor.api.controllers.get_settings")
def test_get_gcs_upload_url_missing_filename(mock_get_settings):
    """Test get_gcs_upload_url with missing filename."""
    # Create request data with missing filename
    request_data = {
        "content_type": "video/mp4"
    }
    
    # Mock settings
    mock_settings_instance = MagicMock()
    mock_settings_instance.gcs_upload_bucket = "test-bucket"
    mock_get_settings.return_value = mock_settings_instance
    
    # Call the function
    response = get_gcs_upload_url(request_data)
    
    # Verify response
    assert response.status_code == 400
    
    # Parse response JSON
    response_data = json.loads(response.get_data(as_text=True))
    assert "error" in response_data
    assert "Missing filename" in response_data["error"]


def test_create_app():
    """Test create_app function."""
    # Create app with default processor
    app = create_app()
    assert app is not None
    
    # Test app has the expected routes
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/" in rules
    assert "/api/gcs-upload-url" in rules
    
    # Create app with custom processor
    mock_processor = MagicMock()
    app = create_app(mock_processor)
    assert app is not None


def test_flask_routes():
    """Test Flask routes integration with controllers."""
    # Create test app with mock processor
    mock_processor = MagicMock()
    app = create_app(mock_processor)
    app.testing = True
    client = app.test_client()
    
    # Test health check endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert b"up and running" in response.data
    
    # Test GCS event endpoint with valid data
    gcs_event = {
        "bucket": "test-bucket",
        "name": "daily-raw/test_video.mp4"
    }
    response = client.post("/", json=gcs_event)
    assert response.status_code == 200
    assert b"processed" in response.data
    
    # Verify processor was called
    mock_processor.assert_called_once_with("test-bucket", "daily-raw/test_video.mp4")