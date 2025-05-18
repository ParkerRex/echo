"""
Unit tests for the file storage service.
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from core.config import Settings

from apps.core.lib.storage.file_storage import FileStorageService


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing local storage."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_settings_local(temp_dir):
    """Create mock settings configured for local storage."""
    settings = Settings()
    settings.STORAGE_BACKEND = "local"
    settings.LOCAL_STORAGE_PATH = temp_dir
    settings.BASE_DIR = Path("/fake/base/dir")  # Not used for local tests
    return settings


@pytest.fixture
def mock_settings_gcs():
    """Create mock settings configured for GCS storage."""
    settings = Settings()
    settings.STORAGE_BACKEND = "gcs"
    settings.GCS_BUCKET_NAME = "test-bucket"
    settings.GOOGLE_APPLICATION_CREDENTIALS_PATH = None  # Use default credentials
    return settings


@pytest.fixture
def mock_gcs_client():
    """Create a mock GCS client."""
    with patch("apps.core.lib.storage.file_storage.storage") as mock_storage:
        # Create mock bucket and blob
        mock_blob = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        # Create mock client
        mock_client = MagicMock()
        mock_client.bucket.return_value = mock_bucket

        # Set up return value for the Client constructor
        mock_storage.Client.return_value = mock_client

        # Set GCS_AVAILABLE to True
        with patch("apps.core.lib.storage.file_storage.GCS_AVAILABLE", True):
            yield mock_client


class TestFileStorageService:
    """Test cases for the FileStorageService class."""

    def test_init_local_storage(self, mock_settings_local):
        """Test initialization with local storage backend."""
        service = FileStorageService(mock_settings_local)

        # Verify the local storage path was set correctly
        assert service.local_storage_path == Path(
            mock_settings_local.LOCAL_STORAGE_PATH
        )

        # Verify the directory was created
        assert os.path.exists(mock_settings_local.LOCAL_STORAGE_PATH)

    def test_init_gcs_storage(self, mock_settings_gcs, mock_gcs_client):
        """Test initialization with GCS storage backend."""
        service = FileStorageService(mock_settings_gcs)

        # Verify the GCS client was initialized
        assert service.gcs_client is not None

    def test_init_gcs_without_dependencies(self, mock_settings_gcs):
        """Test initialization fails when GCS is selected but dependencies aren't available."""
        with patch("apps.core.lib.storage.file_storage.GCS_AVAILABLE", False):
            with pytest.raises(ImportError) as excinfo:
                FileStorageService(mock_settings_gcs)

            assert "Google Cloud Storage dependencies are not installed" in str(
                excinfo.value
            )

    def test_init_gcs_without_bucket(self, mock_gcs_client):
        """Test initialization fails when GCS is selected but no bucket is specified."""
        settings = Settings()
        settings.STORAGE_BACKEND = "gcs"
        settings.GCS_BUCKET_NAME = None

        with pytest.raises(ValueError) as excinfo:
            FileStorageService(settings)

        assert "GCS_BUCKET_NAME must be set" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_init_unsupported_backend(self):
        """Test initialization fails with an unsupported storage backend."""
        settings = Settings()
        settings.STORAGE_BACKEND = "unsupported"

        # This should not raise an error on init, only when methods are called
        service = FileStorageService(settings)

        # But operations should fail
        with pytest.raises(ValueError) as excinfo:
            await service.save_file(b"test content", "test.txt")

        assert "Unsupported storage backend" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_save_file_local(self, mock_settings_local):
        """Test saving a file to local storage."""
        service = FileStorageService(mock_settings_local)

        # Test file data
        test_content = b"This is test content"
        test_filename = "test.txt"

        # Save the file
        relative_path = await service.save_file(test_content, test_filename)

        # Verify the path is returned correctly
        assert relative_path.startswith("uploads/")
        assert relative_path.endswith(".txt")

        # Verify the file was saved
        saved_path = os.path.join(mock_settings_local.LOCAL_STORAGE_PATH, relative_path)
        assert os.path.exists(saved_path)

        # Verify the content
        with open(saved_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == test_content

    @pytest.mark.asyncio
    async def test_save_file_gcs(self, mock_settings_gcs, mock_gcs_client):
        """Test saving a file to GCS."""
        service = FileStorageService(mock_settings_gcs)

        # Test file data
        test_content = b"This is test content"
        test_filename = "test.txt"

        # Save the file
        storage_path = await service.save_file(test_content, test_filename)

        # Verify the path is returned correctly
        assert storage_path.startswith(
            f"gs://{mock_settings_gcs.GCS_BUCKET_NAME}/uploads/"
        )
        assert storage_path.endswith(".txt")

        # Verify the GCS upload was called
        mock_bucket = mock_gcs_client.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.upload_from_string.assert_called_once()

        # Verify the correct parameters were used
        call_args = mock_blob.upload_from_string.call_args[0]
        assert call_args[0] == test_content

    @pytest.mark.asyncio
    async def test_download_file_local(self, mock_settings_local):
        """Test downloading a file from local storage."""
        service = FileStorageService(mock_settings_local)

        # Create a test file
        test_content = b"This is test content for download"
        test_filename = "test_download.txt"
        source_path = await service.save_file(test_content, test_filename)

        # Create a temporary directory for the download destination
        with tempfile.TemporaryDirectory() as dest_dir:
            dest_path = os.path.join(dest_dir, "downloaded.txt")

            # Download the file
            result_path = await service.download_file(source_path, dest_path)

            # Verify the correct path was returned
            assert result_path == dest_path

            # Verify the file was downloaded
            assert os.path.exists(dest_path)

            # Verify the content
            with open(dest_path, "rb") as f:
                downloaded_content = f.read()
            assert downloaded_content == test_content

    @pytest.mark.asyncio
    async def test_download_file_gcs(self, mock_settings_gcs, mock_gcs_client):
        """Test downloading a file from GCS."""
        service = FileStorageService(mock_settings_gcs)

        # Mock GCS URI
        gcs_uri = f"gs://{mock_settings_gcs.GCS_BUCKET_NAME}/test_folder/test.txt"

        # Create a temporary directory for the download destination
        with tempfile.TemporaryDirectory() as dest_dir:
            dest_path = os.path.join(dest_dir, "downloaded.txt")

            # Download the file
            result_path = await service.download_file(gcs_uri, dest_path)

            # Verify the correct path was returned
            assert result_path == dest_path

            # Verify download_to_filename was called on the blob
            mock_bucket = mock_gcs_client.bucket.return_value
            mock_blob = mock_bucket.blob.return_value
            mock_blob.download_to_filename.assert_called_once_with(dest_path)

    @pytest.mark.asyncio
    async def test_get_public_url_local(self, mock_settings_local):
        """Test getting a public URL for a local file."""
        service = FileStorageService(mock_settings_local)

        # Local files don't have public URLs
        url = await service.get_public_url("uploads/test.txt")
        assert url is None

    @pytest.mark.asyncio
    async def test_get_public_url_gcs(self, mock_settings_gcs, mock_gcs_client):
        """Test getting a public URL for a GCS file."""
        service = FileStorageService(mock_settings_gcs)

        # Test with a GCS URI
        gcs_uri = f"gs://{mock_settings_gcs.GCS_BUCKET_NAME}/test_folder/test.txt"
        url = await service.get_public_url(gcs_uri)

        # Verify the URL format
        assert (
            url
            == f"https://storage.googleapis.com/{mock_settings_gcs.GCS_BUCKET_NAME}/test_folder/test.txt"
        )

        # Test with just a blob path
        blob_path = "test_folder/test.txt"
        url = await service.get_public_url(blob_path)

        # Verify the URL format
        assert (
            url
            == f"https://storage.googleapis.com/{mock_settings_gcs.GCS_BUCKET_NAME}/{blob_path}"
        )

    def test_parse_gcs_uri(self, mock_settings_gcs, mock_gcs_client):
        """Test parsing a GCS URI."""
        service = FileStorageService(mock_settings_gcs)

        # Valid URI
        bucket_name, blob_name = service._parse_gcs_uri(
            "gs://test-bucket/path/to/file.txt"
        )
        assert bucket_name == "test-bucket"
        assert blob_name == "path/to/file.txt"

        # Invalid URI (no gs:// prefix)
        with pytest.raises(ValueError) as excinfo:
            service._parse_gcs_uri("invalid-uri")
        assert "Invalid GCS URI" in str(excinfo.value)

        # Invalid URI (no blob name)
        with pytest.raises(ValueError) as excinfo:
            service._parse_gcs_uri("gs://test-bucket")
        assert "Invalid GCS URI format" in str(excinfo.value)

    def test_upload_from_string_local(self, mock_settings_local):
        """Test uploading a string to local storage."""
        service = FileStorageService(mock_settings_local)

        # Test content
        test_content = "This is string content"
        storage_path = "test_folder/string_file.txt"

        # Upload the string
        service.upload_from_string(test_content, storage_path)

        # Verify the file was created
        full_path = os.path.join(mock_settings_local.LOCAL_STORAGE_PATH, storage_path)
        assert os.path.exists(full_path)

        # Verify the content
        with open(full_path, "r", encoding="utf-8") as f:
            saved_content = f.read()
        assert saved_content == test_content

    def test_upload_from_string_gcs(self, mock_settings_gcs, mock_gcs_client):
        """Test uploading a string to GCS."""
        service = FileStorageService(mock_settings_gcs)

        # Test content
        test_content = "This is string content"
        storage_path = "test_folder/string_file.txt"
        content_type = "text/plain"

        # Upload the string
        service.upload_from_string(test_content, storage_path, content_type)

        # Verify upload_from_string was called on the blob
        mock_bucket = mock_gcs_client.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.upload_from_string.assert_called_once_with(
            test_content, content_type=content_type
        )
