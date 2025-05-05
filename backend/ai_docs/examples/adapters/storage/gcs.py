"""
Google Cloud Storage adapter implementation.

This module provides a concrete implementation of the StorageInterface
for Google Cloud Storage. It handles the specific details of interacting
with GCS while conforming to the interface expected by the application.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Union

from google.cloud import storage
from google.cloud.exceptions import Forbidden, NotFound

from video_processor.application.interfaces.storage import (
    FileNotFoundError,
    StorageError,
    StorageInterface,
    StoragePermissionError,
)


class GCSStorageAdapter(StorageInterface):
    """
    Google Cloud Storage implementation of the storage interface.

    This adapter implements the StorageInterface abstract methods using
    the Google Cloud Storage client library.
    """

    def __init__(
        self,
        client: Optional[storage.Client] = None,
        executor: Optional[ThreadPoolExecutor] = None,
    ):
        """
        Initialize the GCS storage adapter.

        Args:
            client: Optional pre-configured storage client
            executor: Optional thread pool executor for async operations
        """
        self._client = client or storage.Client()
        self._executor = executor or ThreadPoolExecutor(max_workers=10)

    def _get_bucket(self, bucket_name: str) -> storage.Bucket:
        """Get a bucket by name."""
        return self._client.bucket(bucket_name)

    def _parse_gcs_path(self, path: str) -> tuple[str, str]:
        """
        Parse a GCS path into bucket name and blob name.

        Args:
            path: GCS path in format 'bucket_name/path/to/file'
                or 'gs://bucket_name/path/to/file'

        Returns:
            Tuple of (bucket_name, blob_name)

        Raises:
            ValueError: If path format is invalid
        """
        if path.startswith("gs://"):
            path = path[5:]

        parts = path.split("/", 1)
        if len(parts) < 2:
            raise ValueError(
                f"Invalid GCS path: {path}. Must be in format 'bucket_name/blob_name'"
            )

        bucket_name, blob_name = parts
        return bucket_name, blob_name

    async def upload_file(
        self,
        source_path: Union[str, Path],
        destination_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """Upload a file to GCS."""
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")

            bucket_name, blob_name = self._parse_gcs_path(destination_path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if content_type:
                blob.content_type = content_type

            # Run in thread pool to avoid blocking
            def _upload():
                blob.upload_from_filename(str(source_path))
                return f"gs://{bucket_name}/{blob_name}"

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _upload
            )

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied uploading to {destination_path}"
            )
        except Exception as e:
            raise StorageError(f"Failed to upload file: {str(e)}")

    async def upload_from_string(
        self, content: str, destination_path: str, content_type: Optional[str] = None
    ) -> str:
        """Upload string content to GCS."""
        try:
            bucket_name, blob_name = self._parse_gcs_path(destination_path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if content_type:
                blob.content_type = content_type

            # Run in thread pool to avoid blocking
            def _upload():
                blob.upload_from_string(content)
                return f"gs://{bucket_name}/{blob_name}"

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _upload
            )

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied uploading to {destination_path}"
            )
        except Exception as e:
            raise StorageError(f"Failed to upload content: {str(e)}")

    async def download_to_file(
        self, source_path: str, destination_path: Union[str, Path]
    ) -> Path:
        """Download a file from GCS to local filesystem."""
        try:
            bucket_name, blob_name = self._parse_gcs_path(source_path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            destination_path = Path(destination_path)

            # Ensure destination directory exists
            destination_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if blob exists
            def _exists():
                return blob.exists()

            exists = await asyncio.get_event_loop().run_in_executor(
                self._executor, _exists
            )

            if not exists:
                raise FileNotFoundError(f"File not found in storage: {source_path}")

            # Download the file
            def _download():
                blob.download_to_filename(str(destination_path))
                return destination_path

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _download
            )

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied downloading from {source_path}"
            )
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise StorageError(f"Failed to download file: {str(e)}")

    async def download_as_string(self, source_path: str) -> str:
        """Download a file from GCS as a string."""
        try:
            bucket_name, blob_name = self._parse_gcs_path(source_path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Check if blob exists
            def _exists():
                return blob.exists()

            exists = await asyncio.get_event_loop().run_in_executor(
                self._executor, _exists
            )

            if not exists:
                raise FileNotFoundError(f"File not found in storage: {source_path}")

            # Download the file as string
            def _download():
                return blob.download_as_text()

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _download
            )

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied downloading from {source_path}"
            )
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise StorageError(f"Failed to download file as string: {str(e)}")

    async def download_as_bytes(self, source_path: str) -> bytes:
        """Download a file from GCS as bytes."""
        try:
            bucket_name, blob_name = self._parse_gcs_path(source_path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Check if blob exists
            def _exists():
                return blob.exists()

            exists = await asyncio.get_event_loop().run_in_executor(
                self._executor, _exists
            )

            if not exists:
                raise FileNotFoundError(f"File not found in storage: {source_path}")

            # Download the file as bytes
            def _download():
                return blob.download_as_bytes()

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _download
            )

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied downloading from {source_path}"
            )
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise StorageError(f"Failed to download file as bytes: {str(e)}")

    async def get_signed_url(
        self, path: str, expires_after_seconds: int = 3600, method: str = "GET"
    ) -> str:
        """Generate a signed URL for a GCS file."""
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Check if blob exists for GET requests
            if method.upper() == "GET":

                def _exists():
                    return blob.exists()

                exists = await asyncio.get_event_loop().run_in_executor(
                    self._executor, _exists
                )

                if not exists:
                    raise FileNotFoundError(f"File not found in storage: {path}")

            # Generate signed URL
            def _generate_url():
                return blob.generate_signed_url(
                    expiration=expires_after_seconds, method=method, version="v4"
                )

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _generate_url
            )

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied generating signed URL for {path}"
            )
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise StorageError(f"Failed to generate signed URL: {str(e)}")

    async def file_exists(self, path: str) -> bool:
        """Check if a file exists in GCS."""
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            def _exists():
                return blob.exists()

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _exists
            )

        except Exception:
            # Don't raise exceptions for existence checks
            return False

    async def delete_file(self, path: str) -> bool:
        """Delete a file from GCS."""
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Check if blob exists
            def _exists():
                return blob.exists()

            exists = await asyncio.get_event_loop().run_in_executor(
                self._executor, _exists
            )

            if not exists:
                return False

            # Delete the blob
            def _delete():
                blob.delete()
                return True

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _delete
            )

        except NotFound:
            return False
        except Forbidden:
            raise StoragePermissionError(f"Permission denied deleting {path}")
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}")

    async def move_file(self, source_path: str, destination_path: str) -> str:
        """Move a file within GCS (copy and delete)."""
        # First copy the file
        destination_url = await self.copy_file(source_path, destination_path)

        # Then delete the original
        await self.delete_file(source_path)

        return destination_url

    async def copy_file(self, source_path: str, destination_path: str) -> str:
        """Copy a file within GCS."""
        try:
            source_bucket_name, source_blob_name = self._parse_gcs_path(source_path)
            dest_bucket_name, dest_blob_name = self._parse_gcs_path(destination_path)

            source_bucket = self._get_bucket(source_bucket_name)
            source_blob = source_bucket.blob(source_blob_name)

            # Check if source blob exists
            def _exists():
                return source_blob.exists()

            exists = await asyncio.get_event_loop().run_in_executor(
                self._executor, _exists
            )

            if not exists:
                raise FileNotFoundError(f"Source file not found: {source_path}")

            dest_bucket = self._get_bucket(dest_bucket_name)

            # Copy the blob
            def _copy():
                destination_blob = source_bucket.copy_blob(
                    source_blob, dest_bucket, dest_blob_name
                )
                return f"gs://{dest_bucket_name}/{dest_blob_name}"

            return await asyncio.get_event_loop().run_in_executor(self._executor, _copy)

        except NotFound:
            raise StorageError(
                f"Bucket not found: {source_bucket_name} or {dest_bucket_name}"
            )
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied copying {source_path} to {destination_path}"
            )
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise StorageError(f"Failed to copy file: {str(e)}")

    async def list_files(self, prefix: str) -> list[str]:
        """List files in GCS with a given prefix."""
        try:
            bucket_name, prefix_path = self._parse_gcs_path(prefix)
            bucket = self._get_bucket(bucket_name)

            # List blobs with prefix
            def _list():
                blobs = bucket.list_blobs(prefix=prefix_path)
                return [f"gs://{bucket_name}/{blob.name}" for blob in blobs]

            return await asyncio.get_event_loop().run_in_executor(self._executor, _list)

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StoragePermissionError(
                f"Permission denied listing files with prefix {prefix}"
            )
        except Exception as e:
            raise StorageError(f"Failed to list files: {str(e)}")
