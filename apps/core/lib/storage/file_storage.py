import asyncio
import os
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, BinaryIO, List, Optional, Tuple, Union

from fastapi import UploadFile

# Import Google Cloud Storage dependencies with error handling
# to allow the module to load even if these aren't installed
try:
    from google.cloud import storage as gcs_storage
    from google.oauth2 import service_account as gcs_service_account

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    gcs_storage = None  # type: ignore
    gcs_service_account = None  # type: ignore


from core.config import settings


class FileStorageService:
    """
    A service for handling file storage operations with support for both local filesystem
    and Google Cloud Storage (GCS).
    """

    def upload_from_string(
        self,
        content: str,
        storage_path: str,
        content_type: str = "application/octet-stream",
    ) -> None:
        """
        Upload a string as a file to the configured storage backend.

        Args:
            content: The string content to upload
            storage_path: The path (relative or absolute) where the file should be stored
            content_type: The MIME type of the content (default: application/octet-stream)
        """
        if self.settings.STORAGE_BACKEND == "local":
            # Save to local filesystem
            full_path = self.local_storage_path / storage_path
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif self.settings.STORAGE_BACKEND == "gcs":
            if self.gcs_client is None:
                raise RuntimeError("GCS client not initialized")
            bucket = self.gcs_client.bucket(self.settings.GCS_BUCKET_NAME)
            blob = bucket.blob(storage_path)
            blob.upload_from_string(content, content_type=content_type)
        else:
            raise ValueError(
                f"Unsupported storage backend: {self.settings.STORAGE_BACKEND}"
            )

    def __init__(self, settings_instance=None):
        """
        Initialize the storage service based on configuration.

        Args:
            settings_instance: An optional Settings instance. If not provided, uses the global settings.
        """
        self.settings = settings_instance or settings

        # Set up local storage configuration
        self.local_storage_path = (
            Path(self.settings.BASE_DIR) / self.settings.LOCAL_STORAGE_PATH
        )
        os.makedirs(self.local_storage_path, exist_ok=True)

        # Set up GCS client if needed
        self.gcs_client = None
        if self.settings.STORAGE_BACKEND == "gcs":
            if not GCS_AVAILABLE:
                raise ImportError(
                    "Google Cloud Storage dependencies are not installed. "
                    "Please install with: pip install google-cloud-storage"
                )

            if self.settings.GOOGLE_APPLICATION_CREDENTIALS_PATH:
                credentials = gcs_service_account.Credentials.from_service_account_file(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS_PATH
                )
                self.gcs_client = gcs_storage.Client(
                    credentials=credentials, project=credentials.project_id
                )
            else:
                # Use default credentials from environment
                self.gcs_client = gcs_storage.Client()

            # Verify bucket exists
            if not self.settings.GCS_BUCKET_NAME:
                raise ValueError(
                    "GCS_BUCKET_NAME must be set when using GCS storage backend"
                )

    async def save_file(
        self, file_content: bytes, filename: str, subdir: Optional[str] = "uploads"
    ) -> str:
        """
        Save a file to the configured storage backend.

        Args:
            file_content: The binary content of the file
            filename: The name of the file
            subdir: Optional subdirectory for organizing storage

        Returns:
            A string representing the storage path of the saved file
        """
        # Generate a unique filename to prevent collisions
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Define the full path including subdirectory
        relative_path = f"{subdir}/{unique_filename}" if subdir else unique_filename

        if self.settings.STORAGE_BACKEND == "local":
            # Ensure subdirectory exists
            if subdir:
                target_dir = self.local_storage_path / subdir
                os.makedirs(target_dir, exist_ok=True)

            # Save to local filesystem
            file_path = self.local_storage_path / relative_path

            # Use async to avoid blocking on file I/O
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(
                    pool, lambda: self._save_local_file(file_path, file_content)
                )

            return relative_path

        elif self.settings.STORAGE_BACKEND == "gcs":
            # Upload to GCS using a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(
                    pool, lambda: self._upload_to_gcs(relative_path, file_content)
                )

            return f"gs://{self.settings.GCS_BUCKET_NAME}/{relative_path}"

        else:
            raise ValueError(
                f"Unsupported storage backend: {self.settings.STORAGE_BACKEND}"
            )

    async def download_file(
        self, storage_path: str, destination_local_path: str
    ) -> str:
        """
        Download a file from storage to a local path.

        Args:
            storage_path: The path where the file is stored
            destination_local_path: The local path where the file should be saved

        Returns:
            The local path where the file is downloaded
        """
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(destination_local_path), exist_ok=True)

        if self.settings.STORAGE_BACKEND == "local":
            # For local storage, just copy the file
            source_path = self._get_local_path(storage_path)

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(
                    pool, lambda: shutil.copy2(source_path, destination_local_path)
                )

        elif self.settings.STORAGE_BACKEND == "gcs":
            # Handle GCS URI format (gs://bucket-name/path/to/file)
            bucket_name: str
            blob_name: str

            if storage_path.startswith("gs://"):
                parts = self._parse_gcs_uri(storage_path)
                bucket_name, blob_name = parts
            else:
                # Assume it's just the blob name
                bucket_name = self.settings.GCS_BUCKET_NAME or ""
                blob_name = storage_path

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(
                    pool,
                    lambda: self._download_from_gcs(
                        bucket_name, blob_name, destination_local_path
                    ),
                )

        else:
            raise ValueError(
                f"Unsupported storage backend: {self.settings.STORAGE_BACKEND}"
            )

        return destination_local_path

    async def get_public_url(self, storage_path: str) -> Optional[str]:
        """
        Get a public URL for accessing the file.

        Args:
            storage_path: The path where the file is stored

        Returns:
            A public URL string or None if not available
        """
        if self.settings.STORAGE_BACKEND == "local":
            # For local files, we typically don't have a public URL
            # Return a placeholder or None
            return None

        elif self.settings.STORAGE_BACKEND == "gcs":
            # Handle GCS URI format
            bucket_name: str
            blob_name: str

            if storage_path.startswith("gs://"):
                parts = self._parse_gcs_uri(storage_path)
                bucket_name, blob_name = parts
            else:
                # Assume it's just the blob name
                bucket_name = self.settings.GCS_BUCKET_NAME or ""
                blob_name = storage_path

            # Generate a public URL for GCS objects
            return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

        else:
            raise ValueError(
                f"Unsupported storage backend: {self.settings.STORAGE_BACKEND}"
            )

    def _save_local_file(self, file_path: Path, content: bytes) -> None:
        """Helper method to save content to a local file"""
        with open(file_path, "wb") as f:
            f.write(content)

    def _upload_to_gcs(self, blob_name: str, content: bytes) -> None:
        """Helper method to upload content to GCS"""
        if self.gcs_client is None:
            raise RuntimeError("GCS client not initialized")

        bucket = self.gcs_client.bucket(self.settings.GCS_BUCKET_NAME)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(content)

    def _download_from_gcs(
        self, bucket_name: str, blob_name: str, destination_path: str
    ) -> None:
        """Helper method to download a file from GCS"""
        if self.gcs_client is None:
            raise RuntimeError("GCS client not initialized")

        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_path)

    def _get_local_path(self, relative_path: str) -> Path:
        """Convert a relative storage path to a full local path"""
        # Handle absolute paths that might have been stored
        if os.path.isabs(relative_path):
            absolute_path: Path = Path(relative_path)
            return absolute_path
        combined_path: Path = self.local_storage_path / relative_path
        return combined_path

    def _parse_gcs_uri(self, gcs_uri: str) -> Tuple[str, str]:
        """Parse a GCS URI (gs://bucket-name/path/to/file) into bucket and blob names"""
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")

        # Remove 'gs://' prefix
        path = gcs_uri[5:]

        # Split into bucket and blob name
        parts = path.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid GCS URI format: {gcs_uri}")

        bucket_name, blob_name = parts
        return bucket_name, blob_name


# Singleton factory
_file_storage_service = None


def get_file_storage_service() -> FileStorageService:
    """Factory function to get the FileStorageService singleton instance"""
    global _file_storage_service
    if _file_storage_service is None:
        _file_storage_service = FileStorageService()
    return _file_storage_service
