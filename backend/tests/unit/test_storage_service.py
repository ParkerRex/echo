"""
Unit tests for storage services.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from video_processor.services.storage import GCSStorageService, LocalStorageService
from video_processor.services.storage.factory import get_storage_service
from video_processor.utils.error_handling import StorageError


class TestLocalStorageService:
    """Tests for LocalStorageService."""

    def test_init(self):
        """Test LocalStorageService initialization."""
        service = LocalStorageService(base_path="/tmp/test_storage")
        assert service.base_path == "/tmp/test_storage"

        # Clean up
        if os.path.exists("/tmp/test_storage"):
            os.rmdir("/tmp/test_storage")

    def test_get_bucket_path(self):
        """Test _get_bucket_path method."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = LocalStorageService(base_path=tmp_dir)
            bucket_path = service._get_bucket_path("test-bucket")
            assert bucket_path == os.path.join(tmp_dir, "test-bucket")

    def test_get_file_path(self):
        """Test _get_file_path method."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = LocalStorageService(base_path=tmp_dir)
            file_path = service._get_file_path("test-bucket", "path/to/file.txt")
            assert file_path == os.path.join(tmp_dir, "test-bucket", "path/to/file.txt")

    def test_upload_from_string(self):
        """Test upload_from_string method."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = LocalStorageService(base_path=tmp_dir)

            # Test with string content
            result = service.upload_from_string(
                "test-bucket", "Test content", "test_file.txt"
            )
            assert result == "test_file.txt"

            # Verify file was created with correct content
            file_path = os.path.join(tmp_dir, "test-bucket", "test_file.txt")
            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == "Test content"

    def test_file_exists(self):
        """Test file_exists method."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = LocalStorageService(base_path=tmp_dir)

            # Create a test file
            os.makedirs(os.path.join(tmp_dir, "test-bucket"), exist_ok=True)
            test_file_path = os.path.join(tmp_dir, "test-bucket", "test_file.txt")
            with open(test_file_path, "w") as f:
                f.write("Test content")

            # Test file exists
            assert service.file_exists("test-bucket", "test_file.txt") is True

            # Test file doesn't exist
            assert service.file_exists("test-bucket", "nonexistent.txt") is False

    def test_get_signed_url(self):
        """Test get_signed_url method."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = LocalStorageService(base_path=tmp_dir)

            # Create a test file
            os.makedirs(os.path.join(tmp_dir, "test-bucket"), exist_ok=True)
            test_file_path = os.path.join(tmp_dir, "test-bucket", "test_file.txt")
            with open(test_file_path, "w") as f:
                f.write("Test content")

            # Get signed URL
            url = service.get_signed_url("test-bucket", "test_file.txt")

            # Verify it's a file:// URL
            assert url.startswith("file://")
            assert test_file_path in url


class TestGCSStorageService:
    """Tests for GCSStorageService."""

    def test_init(self, mock_storage_client):
        """Test GCSStorageService initialization."""
        mock_client, _, _ = mock_storage_client

        # Test with provided client
        service = GCSStorageService(client=mock_client)
        assert service.client is mock_client

        # Test with default client creation
        with patch(
            "video_processor.services.storage.gcs.storage.Client"
        ) as mock_client_class:
            mock_client_class.return_value = mock_client
            service = GCSStorageService()
            mock_client_class.assert_called_once()
            assert service.client is mock_client

    def test_download_file(self, mock_storage_client):
        """Test download_file method."""
        mock_client, mock_bucket, mock_blob = mock_storage_client

        service = GCSStorageService(client=mock_client)

        # Set up mocks
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True

        # Test download
        with tempfile.TemporaryDirectory() as tmp_dir:
            dest_path = os.path.join(tmp_dir, "downloaded.txt")
            result = service.download_file("test-bucket", "test_file.txt", dest_path)

            # Verify result
            assert result == dest_path

            # Verify mocks called correctly
            mock_client.bucket.assert_called_once_with("test-bucket")
            mock_bucket.blob.assert_called_once_with("test_file.txt")
            mock_blob.exists.assert_called_once()
            mock_blob.download_to_filename.assert_called_once_with(dest_path)

    def test_download_file_nonexistent(self, mock_storage_client):
        """Test download_file with nonexistent file."""
        mock_client, mock_bucket, mock_blob = mock_storage_client

        service = GCSStorageService(client=mock_client)

        # Set up mocks
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = False

        # Test download
        with tempfile.TemporaryDirectory() as tmp_dir:
            dest_path = os.path.join(tmp_dir, "downloaded.txt")

            # Should raise StorageError
            with pytest.raises(StorageError) as excinfo:
                service.download_file("test-bucket", "nonexistent.txt", dest_path)

            # Verify error message
            assert "does not exist" in str(excinfo.value)

    def test_upload_from_string(self, mock_storage_client):
        """Test upload_from_string method."""
        mock_client, mock_bucket, mock_blob = mock_storage_client

        service = GCSStorageService(client=mock_client)

        # Set up mocks
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Test with string content
        result = service.upload_from_string(
            "test-bucket", "Test content", "test_file.txt"
        )

        # Verify result
        assert result == "test_file.txt"

        # Verify mocks called correctly
        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test_file.txt")
        mock_blob.upload_from_string.assert_called_once_with("Test content")

    def test_move_file(self, mock_storage_client):
        """Test move_file method."""
        mock_client, mock_bucket, mock_blob = mock_storage_client

        service = GCSStorageService(client=mock_client)

        # Set up mocks
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True

        # Test move
        result = service.move_file("test-bucket", "source.txt", "destination.txt")

        # Verify result
        assert result is True

        # Verify mocks called correctly
        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("source.txt")
        mock_blob.exists.assert_called_once()
        mock_bucket.copy_blob.assert_called_once_with(
            mock_blob, mock_bucket, "destination.txt"
        )
        mock_blob.delete.assert_called_once()


def test_get_storage_service_testing_mode():
    """Test get_storage_service in testing mode."""
    with patch(
        "video_processor.services.storage.factory.get_settings"
    ) as mock_get_settings:
        # Mock settings to return testing_mode=False, local_output=False
        mock_settings = MagicMock()
        mock_settings.testing_mode = False
        mock_settings.local_output = False
        mock_get_settings.return_value = mock_settings

        # Test with testing_mode=True override
        service = get_storage_service(testing_mode=True)
        assert isinstance(service, LocalStorageService)

        # Test with local_output=True override
        service = get_storage_service(local_output=True)
        assert isinstance(service, LocalStorageService)

        # Test with both False
        with patch(
            "video_processor.services.storage.factory.GCSStorageService",
            return_value=MagicMock(spec=GCSStorageService),
        ) as mock_gcs:
            service = get_storage_service()
            assert mock_gcs.called
            assert not isinstance(service, LocalStorageService)
