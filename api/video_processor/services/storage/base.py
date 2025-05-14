"""
Base storage service interface.
"""

from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Dict, List, Optional, Union

# Type alias for file-like objects
FileContent = Union[str, bytes, BinaryIO]


class StorageService(ABC):
    """
    Abstract base class for storage services.

    This interface defines the methods that all storage services must implement,
    providing a consistent API regardless of the underlying storage system.
    """

    @abstractmethod
    def download_file(
        self, bucket: str, source_path: str, destination_path: str
    ) -> str:
        """
        Download a file from storage.

        Args:
            bucket: Storage bucket name
            source_path: Path to the file in storage
            destination_path: Local path to save the file

        Returns:
            Local path to the downloaded file

        Raises:
            StorageError: If the download fails
        """
        pass

    @abstractmethod
    def upload_file(self, bucket: str, source_path: str, destination_path: str) -> str:
        """
        Upload a file to storage.

        Args:
            bucket: Storage bucket name
            source_path: Local path to the file
            destination_path: Path to save the file in storage

        Returns:
            Storage path to the uploaded file

        Raises:
            StorageError: If the upload fails
        """
        pass

    @abstractmethod
    def upload_from_string(
        self, bucket: str, content: FileContent, destination_path: str
    ) -> str:
        """
        Upload content directly to storage.

        Args:
            bucket: Storage bucket name
            content: Content to upload (string, bytes, or file-like object)
            destination_path: Path to save the file in storage

        Returns:
            Storage path to the uploaded file

        Raises:
            StorageError: If the upload fails
        """
        pass

    @abstractmethod
    def read_file(self, bucket: str, path: str) -> bytes:
        """
        Read a file from storage as bytes.

        Args:
            bucket: Storage bucket name
            path: Path to the file in storage

        Returns:
            File content as bytes

        Raises:
            StorageError: If the read fails
        """
        pass

    @abstractmethod
    def read_text(self, bucket: str, path: str, encoding: str = "utf-8") -> str:
        """
        Read a file from storage as text.

        Args:
            bucket: Storage bucket name
            path: Path to the file in storage
            encoding: Text encoding to use

        Returns:
            File content as text

        Raises:
            StorageError: If the read fails
        """
        pass

    @abstractmethod
    def list_files(self, bucket: str, prefix: Optional[str] = None) -> List[str]:
        """
        List files in a bucket with optional prefix.

        Args:
            bucket: Storage bucket name
            prefix: Optional prefix to filter files

        Returns:
            List of file paths

        Raises:
            StorageError: If the listing fails
        """
        pass

    @abstractmethod
    def file_exists(self, bucket: str, path: str) -> bool:
        """
        Check if a file exists.

        Args:
            bucket: Storage bucket name
            path: Path to the file in storage

        Returns:
            True if the file exists, False otherwise
        """
        pass

    @abstractmethod
    def delete_file(self, bucket: str, path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            bucket: Storage bucket name
            path: Path to the file in storage

        Returns:
            True if the file was deleted, False otherwise
        """
        pass

    @abstractmethod
    def move_file(self, bucket: str, source_path: str, destination_path: str) -> bool:
        """
        Move a file within a bucket.

        Args:
            bucket: Storage bucket name
            source_path: Original path to the file
            destination_path: New path for the file

        Returns:
            True if the file was moved, False otherwise
        """
        pass

    @abstractmethod
    def get_signed_url(
        self,
        bucket: str,
        path: str,
        expiration_minutes: int = 15,
        http_method: str = "GET",
        content_type: Optional[str] = None,
    ) -> str:
        """
        Generate a signed URL for a file.

        Args:
            bucket: Storage bucket name
            path: Path to the file in storage
            expiration_minutes: URL expiration time in minutes
            http_method: HTTP method for the URL (GET, PUT, etc.)
            content_type: Content type for uploads

        Returns:
            Signed URL

        Raises:
            StorageError: If URL generation fails
        """
        pass

    @abstractmethod
    def get_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """
        Get metadata for a file.

        Args:
            bucket: Storage bucket name
            path: Path to the file in storage

        Returns:
            File metadata as a dictionary

        Raises:
            StorageError: If metadata retrieval fails
        """
        pass
