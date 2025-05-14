"""Integration tests for GCS storage adapter."""
import os
import pytest
import tempfile
import uuid
from pathlib import Path

from video_processor.adapters.storage.gcs import GCSStorageAdapter
from video_processor.domain.exceptions import StorageError


@pytest.fixture
def test_bucket_name():
    """Get test bucket name from environment or use a default for local testing."""
    return os.environ.get("TEST_GCS_BUCKET", "test-video-processor-bucket")


@pytest.fixture
def test_file_content():
    """Provide sample file content for testing."""
    return b"Test file content for GCS storage adapter integration test."


@pytest.fixture
def test_file_path():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    
    # Cleanup after test
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


@pytest.fixture
def gcs_adapter(test_bucket_name):
    """Create a GCS adapter for testing."""
    return GCSStorageAdapter(bucket_name=test_bucket_name)


@pytest.mark.integration
class TestGCSStorageAdapter:
    """Integration tests for GCS storage adapter."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_files = []
    
    def teardown_method(self):
        """Clean up any test files created during tests."""
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception:
                pass
                
    def test_upload_and_download(self, gcs_adapter, test_file_path, test_file_content):
        """Test uploading and downloading a file."""
        # Prepare test file
        with open(test_file_path, "wb") as f:
            f.write(test_file_content)
        
        # Generate unique destination path
        test_id = str(uuid.uuid4())
        destination_path = f"test/integration/{test_id}/test_file.txt"
        
        # Upload the file
        uploaded_path = gcs_adapter.upload_file(
            file_path=test_file_path,
            destination_path=destination_path
        )
        
        assert uploaded_path == destination_path
        
        # Download the file to a new location
        download_path = f"{test_file_path}_downloaded"
        self.test_files.append(download_path)
        
        downloaded_path = gcs_adapter.download_file(
            source_path=destination_path,
            destination_path=download_path
        )
        
        assert downloaded_path == download_path
        assert os.path.exists(download_path)
        
        # Verify content
        with open(download_path, "rb") as f:
            downloaded_content = f.read()
        
        assert downloaded_content == test_file_content
        
        # Clean up the remote file
        assert gcs_adapter.delete_file(destination_path)
    
    def test_get_public_url(self, gcs_adapter, test_bucket_name):
        """Test getting a public URL for a file."""
        test_path = "test/public/test_file.txt"
        url = gcs_adapter.get_public_url(test_path)
        
        assert url.startswith("https://storage.googleapis.com/")
        assert test_bucket_name in url
        assert test_path in url
    
    def test_get_signed_url(self, gcs_adapter, test_bucket_name):
        """Test getting a signed URL for a file."""
        test_path = "test/signed/test_file.txt"
        expiration = 3600  # 1 hour
        
        url = gcs_adapter.get_signed_url(test_path, expiration_seconds=expiration)
        
        assert url.startswith("https://storage.googleapis.com/")
        assert test_bucket_name in url
        assert test_path in url
        assert "Signature=" in url
        assert "Expires=" in url
    
    def test_upload_nonexistent_file(self, gcs_adapter):
        """Test uploading a non-existent file raises appropriate error."""
        with pytest.raises(StorageError):
            gcs_adapter.upload_file(
                file_path="/nonexistent/file.txt",
                destination_path="test/error/file.txt"
            )
    
    def test_download_nonexistent_file(self, gcs_adapter, test_file_path):
        """Test downloading a non-existent file raises appropriate error."""
        with pytest.raises(StorageError):
            gcs_adapter.download_file(
                source_path="test/nonexistent/file.txt",
                destination_path=f"{test_file_path}_nonexistent"
            ) 