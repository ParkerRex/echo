"""
Google Cloud Storage adapter implementation.

This module provides a concrete implementation of the StorageInterface
for Google Cloud Storage. It handles file operations using GCS.
"""

import os
import time
from typing import List, Optional, Union

from google.cloud import storage
from google.cloud.exceptions import Forbidden, NotFound

from video_processor.application.interfaces.storage import StorageInterface
from video_processor.domain.exceptions import StorageError


class GCSStorageAdapter(StorageInterface):
    """
    Google Cloud Storage implementation of StorageInterface.

    This adapter implements storage operations using the Google Cloud Storage client.
    """

    def __init__(self, client: Optional[storage.Client] = None):
        """
        Initialize the GCS Storage Adapter.

        Args:
            client: Optional pre-configured storage client
        """
        self._client = client or storage.Client()

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """
        Upload a file to GCS storage.

        Args:
            file_path: Local path to the file to upload
            destination_path: Path in storage where the file should be saved

        Returns:
            The GCS path to the uploaded file

        Raises:
            StorageError: If the upload fails
        """
        try:
            if not os.path.exists(file_path):
                raise StorageError(f"Source file not found: {file_path}")

            bucket_name, blob_name = self._parse_gcs_path(destination_path)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Upload with retry logic
            max_retries = 3
            backoff = 1  # Initial backoff in seconds

            for attempt in range(max_retries):
                try:
                    blob.upload_from_filename(file_path)
                    return f"gs://{bucket_name}/{blob_name}"
                except Exception:
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise exception
                        raise
                    # Exponential backoff
                    time.sleep(backoff)
                    backoff *= 2

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StorageError(f"Permission denied uploading to {destination_path}")
        except Exception as e:
            raise StorageError(f"Failed to upload file: {str(e)}")

    def upload_from_string(
        self,
        content: Union[str, bytes],
        destination_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload string content to GCS storage.

        Args:
            content: String or bytes content to upload
            destination_path: Path in storage where the content should be saved
            content_type: Optional MIME type of the content

        Returns:
            The GCS path to the uploaded content

        Raises:
            StorageError: If the upload fails
        """
        try:
            bucket_name, blob_name = self._parse_gcs_path(destination_path)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Upload with retry logic
            max_retries = 3
            backoff = 1  # Initial backoff in seconds

            for attempt in range(max_retries):
                try:
                    if content_type:
                        blob.upload_from_string(content, content_type=content_type)
                    else:
                        blob.upload_from_string(content)
                    return f"gs://{bucket_name}/{blob_name}"
                except Exception:
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise exception
                        raise
                    # Exponential backoff
                    time.sleep(backoff)
                    backoff *= 2

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StorageError(f"Permission denied uploading to {destination_path}")
        except Exception as e:
            raise StorageError(f"Failed to upload content: {str(e)}")

    def download_file(self, source_path: str, destination_path: str) -> str:
        """
        Download a file from GCS storage.

        Args:
            source_path: Path in storage to the file to download
            destination_path: Local path where the file should be saved

        Returns:
            The local path to the downloaded file

        Raises:
            StorageError: If the download fails
        """
        try:
            bucket_name, blob_name = self._parse_gcs_path(source_path)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            if not blob.exists():
                raise StorageError(f"File not found in storage: {source_path}")

            # Download with retry logic
            max_retries = 3
            backoff = 1  # Initial backoff in seconds

            for attempt in range(max_retries):
                try:
                    blob.download_to_filename(destination_path)
                    return destination_path
                except Exception:
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise exception
                        raise
                    # Exponential backoff
                    time.sleep(backoff)
                    backoff *= 2

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StorageError(f"Permission denied downloading from {source_path}")
        except Exception as e:
            raise StorageError(f"Failed to download file: {str(e)}")

    def delete_file(self, path: str) -> bool:
        """
        Delete a file from GCS storage.

        Args:
            path: Path in storage to the file to delete

        Returns:
            True if the file was deleted, False if the file didn't exist

        Raises:
            StorageError: If the deletion fails
        """
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                return False

            blob.delete()
            return True

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Forbidden:
            raise StorageError(f"Permission denied deleting {path}")
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}")

    def get_public_url(self, path: str) -> str:
        """
        Get a public URL for a file in GCS storage.

        Args:
            path: Path in storage to the file

        Returns:
            A public URL for the file
        """
        bucket_name, blob_name = self._parse_gcs_path(path)
        return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

    def get_signed_url(self, path: str, expiration_seconds: int = 3600) -> str:
        """
        Get a signed URL for a file in GCS storage.

        Args:
            path: Path in storage to the file
            expiration_seconds: Number of seconds until the URL expires

        Returns:
            A signed URL for the file

        Raises:
            StorageError: If the URL generation fails
        """
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                raise StorageError(f"File not found in storage: {path}")

            url = blob.generate_signed_url(
                version="v4", expiration=expiration_seconds, method="GET"
            )
            return url

        except Exception as e:
            raise StorageError(f"Failed to generate signed URL: {str(e)}")

    def get_upload_signed_url(
        self,
        path: str,
        expiration_seconds: int = 3600,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Get a signed URL for uploading a file to GCS storage (method=PUT).

        Args:
            path: Path in storage where the file will be uploaded
            expiration_seconds: Number of seconds until the URL expires
            content_type: Optional MIME type to restrict uploads

        Returns:
            A signed URL for uploading the file

        Raises:
            StorageError: If the URL generation fails
        """
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            response_headers = {}
            if content_type:
                response_headers["content-type"] = content_type

            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration_seconds,
                method="PUT",
                content_type=content_type,
                response_headers=response_headers if response_headers else None,
            )
            return url

        except Exception as e:
            raise StorageError(f"Failed to generate upload signed URL: {str(e)}")

    def list_files(
        self, directory_path: str, filter_prefix: Optional[str] = None
    ) -> List[str]:
        """
        List files in a directory in GCS storage.

        Args:
            directory_path: Path in storage to the directory to list
            filter_prefix: Optional prefix to filter the files

        Returns:
            A list of file paths in the directory

        Raises:
            StorageError: If the listing fails
        """
        try:
            bucket_name, prefix = self._parse_gcs_path(directory_path)
            bucket = self._client.bucket(bucket_name)

            # Ensure prefix ends with a slash to represent a directory
            if prefix and not prefix.endswith("/"):
                prefix += "/"

            # Add filter prefix if provided
            if filter_prefix:
                prefix = prefix + filter_prefix

            blobs = bucket.list_blobs(prefix=prefix)
            return [f"gs://{bucket_name}/{blob.name}" for blob in blobs]

        except NotFound:
            raise StorageError(f"Bucket not found: {bucket_name}")
        except Exception as e:
            raise StorageError(f"Failed to list files: {str(e)}")

    def copy_file(self, source_path: str, destination_path: str) -> str:
        """
        Copy a file within GCS storage.

        Args:
            source_path: Path in storage to the file to copy
            destination_path: Path in storage where the file should be copied

        Returns:
            The path to the copied file

        Raises:
            StorageError: If the copy fails
        """
        try:
            src_bucket_name, src_blob_name = self._parse_gcs_path(source_path)
            dst_bucket_name, dst_blob_name = self._parse_gcs_path(destination_path)

            source_bucket = self._client.bucket(src_bucket_name)
            source_blob = source_bucket.blob(src_blob_name)

            if not source_blob.exists():
                raise StorageError(f"Source file not found: {source_path}")

            destination_bucket = self._client.bucket(dst_bucket_name)
            destination_blob = destination_bucket.blob(dst_blob_name)

            # Copy the blob
            source_bucket.copy_blob(source_blob, destination_bucket, dst_blob_name)

            return f"gs://{dst_bucket_name}/{dst_blob_name}"

        except NotFound:
            raise StorageError("Bucket not found")
        except Forbidden:
            raise StorageError("Permission denied copying file")
        except Exception as e:
            raise StorageError(f"Failed to copy file: {str(e)}")

    def move_file(self, source_path: str, destination_path: str) -> str:
        """
        Move a file within GCS storage.

        Args:
            source_path: Path in storage to the file to move
            destination_path: Path in storage where the file should be moved

        Returns:
            The path to the moved file

        Raises:
            StorageError: If the move fails
        """
        try:
            # Copy the file
            self.copy_file(source_path, destination_path)

            # Delete the source file
            self.delete_file(source_path)

            return destination_path

        except Exception as e:
            raise StorageError(f"Failed to move file: {str(e)}")

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in GCS storage.

        Args:
            path: Path in storage to the file to check

        Returns:
            True if the file exists, False otherwise
        """
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = self._client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            return blob.exists()

        except Exception:
            return False

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
