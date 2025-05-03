"""
Mock storage adapter for testing.
"""

import shutil
from pathlib import Path
from typing import Dict

from video_processor.application.interfaces.storage import StorageInterface
from video_processor.domain.exceptions import StorageError


class MockStorageAdapter(StorageInterface):
    """
    Mock implementation of StorageInterface for testing.
    Simulates storage operations using a local temporary directory.
    """

    def __init__(self, base_path: str = "/tmp/mock_storage"):
        """
        Initialize the mock storage adapter.

        Args:
            base_path: Base directory for mock storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True, parents=True)

        # In-memory storage to simulate file contents
        self._files: Dict[str, bytes] = {}
        self._urls: Dict[str, str] = {}

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """
        Simulate uploading a file to storage.

        Args:
            file_path: Local path to file
            destination_path: Destination path in storage

        Returns:
            Storage path of uploaded file

        Raises:
            StorageError: If file doesn't exist or upload fails
        """
        try:
            source_path = Path(file_path)

            if not source_path.exists():
                raise StorageError(f"File not found: {file_path}")

            # Store file content in memory
            with open(source_path, "rb") as f:
                self._files[destination_path] = f.read()

            # Generate a mock URL
            self._urls[destination_path] = (
                f"https://storage.example.com/{destination_path}"
            )

            return destination_path
        except Exception as e:
            if not isinstance(e, StorageError):
                raise StorageError(f"Failed to upload file: {str(e)}")
            raise

    def download_file(self, source_path: str, destination_path: str) -> str:
        """
        Simulate downloading a file from storage.

        Args:
            source_path: Path in storage
            destination_path: Local destination path

        Returns:
            Local path of downloaded file

        Raises:
            StorageError: If download fails
        """
        try:
            if source_path not in self._files:
                raise StorageError(f"File not found in storage: {source_path}")

            dest_path = Path(destination_path)
            dest_path.parent.mkdir(exist_ok=True, parents=True)

            # Write from in-memory storage to destination
            with open(dest_path, "wb") as f:
                f.write(self._files[source_path])

            return destination_path
        except Exception as e:
            if not isinstance(e, StorageError):
                raise StorageError(f"Failed to download file: {str(e)}")
            raise

    def delete_file(self, path: str) -> bool:
        """
        Simulate deleting a file from storage.

        Args:
            path: Path in storage

        Returns:
            True if deletion succeeded, False otherwise

        Raises:
            StorageError: If deletion fails
        """
        try:
            if path in self._files:
                del self._files[path]
                if path in self._urls:
                    del self._urls[path]
                return True
            return False
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}")

    def get_public_url(self, path: str) -> str:
        """
        Generate a public URL for a file.

        Args:
            path: Path in storage

        Returns:
            Public URL

        Raises:
            StorageError: If file doesn't exist
        """
        if path not in self._files:
            raise StorageError(f"File not found in storage: {path}")

        return f"https://storage.example.com/public/{path}"

    def get_signed_url(self, path: str, expiration_seconds: int = 3600) -> str:
        """
        Generate a signed URL for a file.

        Args:
            path: Path in storage
            expiration_seconds: URL expiration time in seconds

        Returns:
            Signed URL

        Raises:
            StorageError: If file doesn't exist
        """
        if path not in self._files:
            raise StorageError(f"File not found in storage: {path}")

        return f"https://storage.example.com/signed/{path}?exp={expiration_seconds}"

    def cleanup(self):
        """
        Clean up the mock storage.
        """
        self._files.clear()
        self._urls.clear()
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
