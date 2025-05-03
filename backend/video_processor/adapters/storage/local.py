"""
Local filesystem storage adapter implementation.

This module provides a concrete implementation of the StorageInterface
for local filesystem storage. It's used primarily for development and testing.
"""

import os
import shutil
from typing import List, Optional, Union
from urllib.parse import quote

from video_processor.application.interfaces.storage import StorageInterface
from video_processor.domain.exceptions import StorageError


class LocalStorageAdapter(StorageInterface):
    """
    Local filesystem implementation of StorageInterface.

    This adapter implements storage operations using the local filesystem,
    which is useful for development and testing environments.
    """

    def __init__(self, base_dir: str = "storage"):
        """
        Initialize the Local Storage Adapter.

        Args:
            base_dir: Base directory for storage (relative to current directory)
        """
        self.base_dir = os.path.abspath(base_dir)
        # Create the base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """
        Upload (copy) a file to local storage.

        Args:
            file_path: Local path to the file to upload
            destination_path: Path in storage where the file should be saved

        Returns:
            The local path to the uploaded file

        Raises:
            StorageError: If the upload fails
        """
        try:
            if not os.path.exists(file_path):
                raise StorageError(f"Source file not found: {file_path}")

            dest_full_path = os.path.join(self.base_dir, destination_path)

            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)

            # Copy the file
            shutil.copy2(file_path, dest_full_path)

            return dest_full_path

        except Exception as e:
            raise StorageError(f"Failed to upload file: {str(e)}")

    def upload_from_string(
        self,
        content: Union[str, bytes],
        destination_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload string content to local storage.

        Args:
            content: String or bytes content to upload
            destination_path: Path in storage where the content should be saved
            content_type: Optional MIME type of the content (ignored in local implementation)

        Returns:
            The local path to the uploaded content

        Raises:
            StorageError: If the upload fails
        """
        try:
            dest_full_path = os.path.join(self.base_dir, destination_path)

            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)

            # Write the content to the file
            mode = "wb" if isinstance(content, bytes) else "w"
            with open(dest_full_path, mode) as f:
                f.write(content)

            return dest_full_path

        except Exception as e:
            raise StorageError(f"Failed to upload content: {str(e)}")

    def download_file(self, source_path: str, destination_path: str) -> str:
        """
        Download (copy) a file from local storage.

        Args:
            source_path: Path in storage to the file to download
            destination_path: Local path where the file should be saved

        Returns:
            The local path to the downloaded file

        Raises:
            StorageError: If the download fails
        """
        try:
            source_full_path = os.path.join(self.base_dir, source_path)

            if not os.path.exists(source_full_path):
                raise StorageError(f"File not found in storage: {source_path}")

            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            # Copy the file
            shutil.copy2(source_full_path, destination_path)

            return destination_path

        except Exception as e:
            raise StorageError(f"Failed to download file: {str(e)}")

    def delete_file(self, path: str) -> bool:
        """
        Delete a file from local storage.

        Args:
            path: Path in storage to the file to delete

        Returns:
            True if the file was deleted, False if the file didn't exist

        Raises:
            StorageError: If the deletion fails
        """
        try:
            full_path = os.path.join(self.base_dir, path)

            if not os.path.exists(full_path):
                return False

            os.remove(full_path)
            return True

        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}")

    def get_public_url(self, path: str) -> str:
        """
        Get a public URL for a file in local storage.

        In local storage, this returns a file:// URL.

        Args:
            path: Path in storage to the file

        Returns:
            A file:// URL for the file
        """
        full_path = os.path.join(self.base_dir, path)
        full_path = os.path.abspath(full_path)
        return f"file://{quote(full_path)}"

    def get_signed_url(self, path: str, expiration_seconds: int = 3600) -> str:
        """
        Get a signed URL for a file in local storage.

        In local storage, this simply returns a file:// URL since
        we can't create an actual signed URL for local files.

        Args:
            path: Path in storage to the file
            expiration_seconds: Number of seconds until the URL expires

        Returns:
            A file:// URL for the file

        Raises:
            StorageError: If the file doesn't exist
        """
        full_path = os.path.join(self.base_dir, path)

        if not os.path.exists(full_path):
            raise StorageError(f"File not found in storage: {path}")

        full_path = os.path.abspath(full_path)
        return f"file://{quote(full_path)}"

    def list_files(
        self, directory_path: str, filter_prefix: Optional[str] = None
    ) -> List[str]:
        """
        List files in a directory in local storage.

        Args:
            directory_path: Path in storage to the directory to list
            filter_prefix: Optional prefix to filter the files

        Returns:
            A list of file paths in the directory

        Raises:
            StorageError: If the listing fails
        """
        try:
            dir_path = os.path.join(self.base_dir, directory_path)

            if not os.path.exists(dir_path):
                return []

            result = []
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if filter_prefix and not file.startswith(filter_prefix):
                        continue

                    # Get the relative path from the base directory
                    rel_path = os.path.relpath(os.path.join(root, file), self.base_dir)
                    result.append(rel_path)

            return result

        except Exception as e:
            raise StorageError(f"Failed to list files: {str(e)}")

    def copy_file(self, source_path: str, destination_path: str) -> str:
        """
        Copy a file within local storage.

        Args:
            source_path: Path in storage to the file to copy
            destination_path: Path in storage where the file should be copied

        Returns:
            The path to the copied file

        Raises:
            StorageError: If the copy fails
        """
        try:
            source_full_path = os.path.join(self.base_dir, source_path)
            dest_full_path = os.path.join(self.base_dir, destination_path)

            if not os.path.exists(source_full_path):
                raise StorageError(f"Source file not found: {source_path}")

            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)

            # Copy the file
            shutil.copy2(source_full_path, dest_full_path)

            return destination_path

        except Exception as e:
            raise StorageError(f"Failed to copy file: {str(e)}")

    def move_file(self, source_path: str, destination_path: str) -> str:
        """
        Move a file within local storage.

        Args:
            source_path: Path in storage to the file to move
            destination_path: Path in storage where the file should be moved

        Returns:
            The path to the moved file

        Raises:
            StorageError: If the move fails
        """
        try:
            source_full_path = os.path.join(self.base_dir, source_path)
            dest_full_path = os.path.join(self.base_dir, destination_path)

            if not os.path.exists(source_full_path):
                raise StorageError(f"Source file not found: {source_path}")

            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)

            # Move the file
            shutil.move(source_full_path, dest_full_path)

            return destination_path

        except Exception as e:
            raise StorageError(f"Failed to move file: {str(e)}")

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in local storage.

        Args:
            path: Path in storage to the file to check

        Returns:
            True if the file exists, False otherwise
        """
        full_path = os.path.join(self.base_dir, path)
        return os.path.exists(full_path) and os.path.isfile(full_path)
