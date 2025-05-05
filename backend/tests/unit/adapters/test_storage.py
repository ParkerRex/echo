"""
Unit tests for the storage adapter implementations.
"""

import os
import tempfile

from tests.mocks.storage import MockStorageAdapter


def test_mock_storage_adapter_upload():
    """Test the mock storage adapter's upload functionality."""
    adapter = MockStorageAdapter()

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b"Test content")
        temp_path = temp.name

    try:
        # Test uploading the file
        result = adapter.upload_file(temp_path, "test/path.txt")

        assert result == "gs://mock-bucket/test/path.txt"
        assert "test/path.txt" in adapter.files
        assert adapter.files["test/path.txt"] == b"Test content"
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_mock_storage_adapter_download():
    """Test the mock storage adapter's download functionality."""
    adapter = MockStorageAdapter()

    # Add a file to the mock storage
    adapter.files["test/download.txt"] = b"Downloaded content"

    with tempfile.TemporaryDirectory() as temp_dir:
        dest_path = os.path.join(temp_dir, "downloaded.txt")

        # Test downloading the file
        result = adapter.download_file("test/download.txt", dest_path)

        assert result == dest_path
        assert os.path.exists(dest_path)

        # Verify the content
        with open(dest_path, "rb") as f:
            content = f.read()
            assert content == b"Downloaded content"


def test_mock_storage_adapter_delete():
    """Test the mock storage adapter's delete functionality."""
    adapter = MockStorageAdapter()

    # Add a file to the mock storage
    adapter.files["test/delete.txt"] = b"Content to delete"

    # Test deleting existing file
    result = adapter.delete_file("test/delete.txt")
    assert result is True
    assert "test/delete.txt" not in adapter.files

    # Test deleting non-existent file
    result = adapter.delete_file("nonexistent.txt")
    assert result is False


def test_mock_storage_adapter_urls():
    """Test the mock storage adapter's URL generation functionality."""
    adapter = MockStorageAdapter(base_url="https://test-storage.example.org")

    # Test public URL
    public_url = adapter.get_public_url("test/file.txt")
    assert public_url == "https://test-storage.example.org/test/file.txt"

    # Test signed URL
    signed_url = adapter.get_signed_url("test/file.txt", 7200)
    assert "https://test-storage.example.org/test/file.txt" in signed_url
    assert "token=mock-signature" in signed_url
    assert "expires=7200" in signed_url


def test_mock_storage_adapter_list_files():
    """Test the mock storage adapter's file listing functionality."""
    adapter = MockStorageAdapter()

    # Add some files with different prefixes
    adapter.files["test/file1.txt"] = b"Content 1"
    adapter.files["test/file2.txt"] = b"Content 2"
    adapter.files["other/file3.txt"] = b"Content 3"

    # Test listing with prefix
    test_files = adapter.list_files("test/")
    assert len(test_files) == 2
    assert "test/file1.txt" in test_files
    assert "test/file2.txt" in test_files
    assert "other/file3.txt" not in test_files

    # Test listing with different prefix
    other_files = adapter.list_files("other/")
    assert len(other_files) == 1
    assert "other/file3.txt" in other_files


def test_mock_storage_adapter_clear():
    """Test the mock storage adapter's clearing functionality."""
    adapter = MockStorageAdapter()

    # Add some files
    adapter.files["test/file1.txt"] = b"Content 1"
    adapter.files["test/file2.txt"] = b"Content 2"

    assert len(adapter.files) == 2

    # Clear the adapter
    adapter.clear()

    assert len(adapter.files) == 0
