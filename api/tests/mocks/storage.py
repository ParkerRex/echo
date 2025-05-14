"""
Mock implementation of the storage interface for testing.
"""

import os
import shutil
from typing import Dict

from video_processor.application.interfaces.storage import StorageInterface


class MockStorageAdapter(StorageInterface):
    """
    Mock implementation of StorageInterface for testing.

    This adapter simulates storage operations in memory without accessing
    any real storage system.
    """

    def __init__(self, base_url: str = "https://mock-storage.example.com"):
        """Initialize the mock storage adapter."""
        self.base_url = base_url
        self.files: Dict[str, bytes] = {}  # In-memory storage
        self.temp_dir = "/tmp/mock_storage"
        os.makedirs(self.temp_dir, exist_ok=True)

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """
        Mock uploading a file to storage.

        Args:
            file_path: Local path to the file
            destination_path: Destination path in storage

        Returns:
            Full path of the uploaded file in storage
        """
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                content = f.read()
                self.files[destination_path] = content
        else:
            # For testing, create some mock content if file doesn't exist
            self.files[destination_path] = b"Mock file content"

        return f"gs://mock-bucket/{destination_path}"

    def download_file(self, source_path: str, destination_path: str) -> str:
        """
        Mock downloading a file from storage.

        Args:
            source_path: Storage path of the file
            destination_path: Local destination path

        Returns:
            Local path of the downloaded file
        """
        # Create the directory structure if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Write mock content to the destination file
        if source_path in self.files:
            content = self.files[source_path]
        else:
            content = b"Mock downloaded content"

        with open(destination_path, "wb") as f:
            f.write(content)

        return destination_path

    def delete_file(self, path: str) -> bool:
        """
        Mock deleting a file from storage.

        Args:
            path: Storage path of the file to delete

        Returns:
            True if successful, False otherwise
        """
        if path in self.files:
            del self.files[path]
            return True
        return False

    def get_public_url(self, path: str) -> str:
        """
        Get a public URL for a file.

        Args:
            path: Storage path of the file

        Returns:
            Public URL for the file
        """
        return f"{self.base_url}/{path}"

    def get_signed_url(self, path: str, expiration_seconds: int = 3600) -> str:
        """
        Get a signed URL for a file with expiration.

        Args:
            path: Storage path of the file
            expiration_seconds: Seconds until the URL expires

        Returns:
            Signed URL for the file
        """
        return (
            f"{self.base_url}/{path}?token=mock-signature&expires={expiration_seconds}"
        )

    def list_files(self, prefix: str) -> list:
        """
        List files with a given prefix.

        Args:
            prefix: Prefix to filter files by

        Returns:
            List of file paths matching the prefix
        """
        return [path for path in self.files.keys() if path.startswith(prefix)]

    def clear(self) -> None:
        """Clear all mock storage data."""
        self.files.clear()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)
