"""
Storage interface for the video processing pipeline.

This module defines the abstract interface for storage operations required by the
application. It follows the dependency inversion principle by having core business
logic depend on abstractions rather than concrete implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union


class StorageError(Exception):
    """Base exception for storage-related errors."""

    pass


class FileNotFoundError(StorageError):
    """Raised when a file cannot be found in storage."""

    pass


class StoragePermissionError(StorageError):
    """Raised when there's a permission issue with storage operations."""

    pass


class StorageInterface(ABC):
    """
    Abstract interface for storage operations.

    This interface defines the contract that any storage implementation
    must fulfill, regardless of whether it's cloud storage, local filesystem,
    or another storage mechanism.
    """

    @abstractmethod
    async def upload_file(
        self,
        source_path: Union[str, Path],
        destination_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a file from local filesystem to storage.

        Args:
            source_path: Local path to file to upload
            destination_path: Path in storage where file should be saved
            content_type: Optional MIME type of the file

        Returns:
            The URL or path to the uploaded file

        Raises:
            StorageError: If upload fails
        """
        pass

    @abstractmethod
    async def upload_from_string(
        self, content: str, destination_path: str, content_type: Optional[str] = None
    ) -> str:
        """
        Upload string content to storage.

        Args:
            content: String content to upload
            destination_path: Path in storage where content should be saved
            content_type: Optional MIME type of the content

        Returns:
            The URL or path to the uploaded content

        Raises:
            StorageError: If upload fails
        """
        pass

    @abstractmethod
    async def download_to_file(
        self, source_path: str, destination_path: Union[str, Path]
    ) -> Path:
        """
        Download a file from storage to local filesystem.

        Args:
            source_path: Path in storage to the file to download
            destination_path: Local path where file should be saved

        Returns:
            Path object pointing to the downloaded file

        Raises:
            FileNotFoundError: If source file doesn't exist
            StorageError: If download fails
        """
        pass

    @abstractmethod
    async def download_as_string(self, source_path: str) -> str:
        """
        Download a file from storage as a string.

        Args:
            source_path: Path in storage to the file to download

        Returns:
            Content of the file as a string

        Raises:
            FileNotFoundError: If source file doesn't exist
            StorageError: If download fails
        """
        pass

    @abstractmethod
    async def download_as_bytes(self, source_path: str) -> bytes:
        """
        Download a file from storage as bytes.

        Args:
            source_path: Path in storage to the file to download

        Returns:
            Content of the file as bytes

        Raises:
            FileNotFoundError: If source file doesn't exist
            StorageError: If download fails
        """
        pass

    @abstractmethod
    async def get_signed_url(
        self, path: str, expires_after_seconds: int = 3600, method: str = "GET"
    ) -> str:
        """
        Generate a signed URL for a file in storage.

        Args:
            path: Path in storage to the file
            expires_after_seconds: Number of seconds until URL expires
            method: HTTP method the URL should support (GET, PUT, etc.)

        Returns:
            A signed URL that can be used to access the file

        Raises:
            FileNotFoundError: If file doesn't exist
            StorageError: If URL generation fails
        """
        pass

    @abstractmethod
    async def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            path: Path in storage to check

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            path: Path in storage to the file to delete

        Returns:
            True if file was deleted, False if file didn't exist

        Raises:
            StoragePermissionError: If deletion fails due to permissions
            StorageError: If deletion fails for other reasons
        """
        pass

    @abstractmethod
    async def move_file(self, source_path: str, destination_path: str) -> str:
        """
        Move a file within storage.

        Args:
            source_path: Current path of the file in storage
            destination_path: New path for the file in storage

        Returns:
            The new path or URL to the moved file

        Raises:
            FileNotFoundError: If source file doesn't exist
            StorageError: If move fails
        """
        pass

    @abstractmethod
    async def copy_file(self, source_path: str, destination_path: str) -> str:
        """
        Copy a file within storage.

        Args:
            source_path: Path of the file to copy
            destination_path: Path where the copy should be saved

        Returns:
            The path or URL to the copied file

        Raises:
            FileNotFoundError: If source file doesn't exist
            StorageError: If copy fails
        """
        pass

    @abstractmethod
    async def list_files(self, prefix: str) -> list[str]:
        """
        List files in storage with a given prefix.

        Args:
            prefix: Prefix to filter files by

        Returns:
            List of paths matching the prefix
        """
        pass
