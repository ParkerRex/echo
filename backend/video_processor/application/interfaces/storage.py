"""
Storage interface for the video processing application.

Defines the contract for storage operations independent of any specific
storage implementation (GCS, local filesystem, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union


class StorageInterface(ABC):
    """
    Interface for storage operations.

    This interface defines the contract for all storage adapter implementations,
    ensuring they provide the necessary methods for file operations.
    """

    @abstractmethod
    def upload_file(self, file_path: str, destination_path: str) -> str:
        """
        Upload a file to storage.

        Args:
            file_path: Local path to the file to upload
            destination_path: Path in storage where the file should be saved

        Returns:
            The public URL or path to the uploaded file

        Raises:
            StorageError: If the upload fails
        """
        pass

    @abstractmethod
    def upload_from_string(
        self,
        content: Union[str, bytes],
        destination_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload string content to storage.

        Args:
            content: String or bytes content to upload
            destination_path: Path in storage where the content should be saved
            content_type: Optional MIME type of the content

        Returns:
            The path or URL to the uploaded content

        Raises:
            StorageError: If the upload fails
        """
        pass

    @abstractmethod
    def download_file(self, source_path: str, destination_path: str) -> str:
        """
        Download a file from storage.

        Args:
            source_path: Path in storage to the file to download
            destination_path: Local path where the file should be saved

        Returns:
            The local path to the downloaded file

        Raises:
            StorageError: If the download fails
        """
        pass

    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            path: Path in storage to the file to delete

        Returns:
            True if the file was deleted, False otherwise

        Raises:
            StorageError: If the deletion fails
        """
        pass

    @abstractmethod
    def get_public_url(self, path: str) -> str:
        """
        Get a public URL for a file in storage.

        Args:
            path: Path in storage to the file

        Returns:
            A public URL for the file that can be accessed without authentication
        """
        pass

    @abstractmethod
    def get_signed_url(self, path: str, expiration_seconds: int = 3600) -> str:
        """
        Get a signed URL for a file in storage.

        Args:
            path: Path in storage to the file
            expiration_seconds: Number of seconds until the URL expires

        Returns:
            A signed URL for the file that expires after the specified time
        """
        pass

    @abstractmethod
    def list_files(
        self, directory_path: str, filter_prefix: Optional[str] = None
    ) -> List[str]:
        """
        List files in a directory in storage.

        Args:
            directory_path: Path in storage to the directory to list
            filter_prefix: Optional prefix to filter the files

        Returns:
            A list of file paths in the directory
        """
        pass

    @abstractmethod
    def copy_file(self, source_path: str, destination_path: str) -> str:
        """
        Copy a file within storage.

        Args:
            source_path: Path in storage to the file to copy
            destination_path: Path in storage where the file should be copied

        Returns:
            The path to the copied file

        Raises:
            StorageError: If the copy fails
        """
        pass

    @abstractmethod
    def move_file(self, source_path: str, destination_path: str) -> str:
        """
        Move a file within storage.

        Args:
            source_path: Path in storage to the file to move
            destination_path: Path in storage where the file should be moved

        Returns:
            The path to the moved file

        Raises:
            StorageError: If the move fails
        """
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            path: Path in storage to the file to check

        Returns:
            True if the file exists, False otherwise
        """
        pass
