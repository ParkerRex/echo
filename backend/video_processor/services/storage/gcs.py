"""
Google Cloud Storage implementation of the storage service.
"""
import os
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union, BinaryIO

from google.cloud import storage
from google.cloud.exceptions import NotFound

from ...utils.error_handling import StorageError, retry
from ...utils.logging import get_logger
from .base import FileContent, StorageService

logger = get_logger(__name__)


class GCSStorageService(StorageService):
    """
    Google Cloud Storage implementation of the storage service.
    """
    
    def __init__(self, client: Optional[storage.Client] = None):
        """
        Initialize the GCS storage service.
        
        Args:
            client: Optional storage client (if None, creates a new client)
        """
        self.client = client if client is not None else storage.Client()
    
    @retry(max_attempts=3)
    def download_file(self, bucket: str, source_path: str, destination_path: str) -> str:
        """
        Download a file from GCS.
        
        Args:
            bucket: GCS bucket name
            source_path: Path to the file in GCS
            destination_path: Local path to save the file
            
        Returns:
            Local path to the downloaded file
            
        Raises:
            StorageError: If the download fails
        """
        try:
            logger.info(f"Downloading gs://{bucket}/{source_path} to {destination_path}")
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(source_path)
            
            # Check if the blob exists
            if not blob.exists():
                raise StorageError(f"File gs://{bucket}/{source_path} does not exist")
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Download the file
            blob.download_to_filename(destination_path)
            logger.info(f"Download complete: gs://{bucket}/{source_path}")
            return destination_path
        except Exception as e:
            logger.error(f"Failed to download gs://{bucket}/{source_path}: {e}")
            raise StorageError(f"Failed to download file: {e}")
    
    @retry(max_attempts=3)
    def upload_file(self, bucket: str, source_path: str, destination_path: str) -> str:
        """
        Upload a file to GCS.
        
        Args:
            bucket: GCS bucket name
            source_path: Local path to the file
            destination_path: Path to save the file in GCS
            
        Returns:
            GCS path to the uploaded file
            
        Raises:
            StorageError: If the upload fails
        """
        try:
            logger.info(f"Uploading {source_path} to gs://{bucket}/{destination_path}")
            
            # Check if source file exists
            if not os.path.exists(source_path):
                raise StorageError(f"Source file {source_path} does not exist")
            
            # Upload to GCS
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(destination_path)
            blob.upload_from_filename(source_path)
            
            logger.info(f"Upload complete: gs://{bucket}/{destination_path}")
            return destination_path
        except Exception as e:
            logger.error(f"Failed to upload {source_path} to gs://{bucket}/{destination_path}: {e}")
            raise StorageError(f"Failed to upload file: {e}")
    
    @retry(max_attempts=3)
    def upload_from_string(self, bucket: str, content: FileContent, destination_path: str) -> str:
        """
        Upload content directly to GCS.
        
        Args:
            bucket: GCS bucket name
            content: Content to upload (string, bytes, or file-like object)
            destination_path: Path to save the file in GCS
            
        Returns:
            GCS path to the uploaded file
            
        Raises:
            StorageError: If the upload fails
        """
        try:
            logger.info(f"Uploading content to gs://{bucket}/{destination_path}")
            
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(destination_path)
            
            # Handle different content types
            if isinstance(content, str):
                blob.upload_from_string(content)
            elif isinstance(content, bytes):
                blob.upload_from_string(content)
            elif hasattr(content, 'read'):  # File-like object
                blob.upload_from_file(content)
            else:
                raise StorageError(f"Unsupported content type: {type(content)}")
            
            logger.info(f"Upload complete: gs://{bucket}/{destination_path}")
            return destination_path
        except Exception as e:
            logger.error(f"Failed to upload content to gs://{bucket}/{destination_path}: {e}")
            raise StorageError(f"Failed to upload content: {e}")
    
    @retry(max_attempts=3)
    def read_file(self, bucket: str, path: str) -> bytes:
        """
        Read a file from GCS as bytes.
        
        Args:
            bucket: GCS bucket name
            path: Path to the file in GCS
            
        Returns:
            File content as bytes
            
        Raises:
            StorageError: If the read fails
        """
        try:
            logger.info(f"Reading gs://{bucket}/{path}")
            
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            
            # Check if the blob exists
            if not blob.exists():
                raise StorageError(f"File gs://{bucket}/{path} does not exist")
            
            # Download as bytes
            content = blob.download_as_bytes()
            logger.info(f"Read {len(content)} bytes from gs://{bucket}/{path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read gs://{bucket}/{path}: {e}")
            raise StorageError(f"Failed to read file: {e}")
    
    @retry(max_attempts=3)
    def read_text(self, bucket: str, path: str, encoding: str = "utf-8") -> str:
        """
        Read a file from GCS as text.
        
        Args:
            bucket: GCS bucket name
            path: Path to the file in GCS
            encoding: Text encoding to use
            
        Returns:
            File content as text
            
        Raises:
            StorageError: If the read fails
        """
        try:
            logger.info(f"Reading text from gs://{bucket}/{path}")
            
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            
            # Check if the blob exists
            if not blob.exists():
                raise StorageError(f"File gs://{bucket}/{path} does not exist")
                
            # Download as text
            content = blob.download_as_text(encoding=encoding)
            logger.info(f"Read {len(content)} characters from gs://{bucket}/{path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read text from gs://{bucket}/{path}: {e}")
            raise StorageError(f"Failed to read file as text: {e}")
    
    def list_files(self, bucket: str, prefix: Optional[str] = None) -> List[str]:
        """
        List files in a GCS bucket with optional prefix.
        
        Args:
            bucket: GCS bucket name
            prefix: Optional prefix to filter files
            
        Returns:
            List of file paths
            
        Raises:
            StorageError: If the listing fails
        """
        try:
            logger.info(f"Listing files in gs://{bucket}/{prefix or ''}")
            
            bucket_obj = self.client.bucket(bucket)
            blobs = bucket_obj.list_blobs(prefix=prefix)
            
            # Extract paths
            paths = [blob.name for blob in blobs]
            logger.info(f"Found {len(paths)} files in gs://{bucket}/{prefix or ''}")
            return paths
        except Exception as e:
            logger.error(f"Failed to list files in gs://{bucket}/{prefix or ''}: {e}")
            raise StorageError(f"Failed to list files: {e}")
    
    def file_exists(self, bucket: str, path: str) -> bool:
        """
        Check if a file exists in GCS.
        
        Args:
            bucket: GCS bucket name
            path: Path to the file in GCS
            
        Returns:
            True if the file exists, False otherwise
        """
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            return blob.exists()
        except Exception as e:
            logger.error(f"Error checking if gs://{bucket}/{path} exists: {e}")
            return False
    
    @retry(max_attempts=3)
    def delete_file(self, bucket: str, path: str) -> bool:
        """
        Delete a file from GCS.
        
        Args:
            bucket: GCS bucket name
            path: Path to the file in GCS
            
        Returns:
            True if the file was deleted, False otherwise
        """
        try:
            logger.info(f"Deleting gs://{bucket}/{path}")
            
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            
            # Check if the blob exists
            if not blob.exists():
                logger.warning(f"File gs://{bucket}/{path} does not exist, nothing to delete")
                return False
                
            # Delete the blob
            blob.delete()
            logger.info(f"Deleted gs://{bucket}/{path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete gs://{bucket}/{path}: {e}")
            return False
    
    @retry(max_attempts=3)
    def move_file(self, bucket: str, source_path: str, destination_path: str) -> bool:
        """
        Move a file within a GCS bucket.
        
        Args:
            bucket: GCS bucket name
            source_path: Original path to the file
            destination_path: New path for the file
            
        Returns:
            True if the file was moved, False otherwise
        """
        try:
            logger.info(f"Moving gs://{bucket}/{source_path} to gs://{bucket}/{destination_path}")
            
            bucket_obj = self.client.bucket(bucket)
            source_blob = bucket_obj.blob(source_path)
            
            # Check if the source blob exists
            if not source_blob.exists():
                logger.warning(f"Source file gs://{bucket}/{source_path} does not exist")
                return False
                
            # Copy to destination
            destination_blob = bucket_obj.copy_blob(
                source_blob, bucket_obj, destination_path
            )
            
            # Delete the source blob
            source_blob.delete()
            
            logger.info(f"Moved gs://{bucket}/{source_path} to gs://{bucket}/{destination_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to move gs://{bucket}/{source_path}: {e}")
            return False
    
    def get_signed_url(
        self, 
        bucket: str, 
        path: str, 
        expiration_minutes: int = 15,
        http_method: str = "GET",
        content_type: Optional[str] = None,
    ) -> str:
        """
        Generate a signed URL for a file in GCS.
        
        Args:
            bucket: GCS bucket name
            path: Path to the file in GCS
            expiration_minutes: URL expiration time in minutes
            http_method: HTTP method for the URL (GET, PUT, etc.)
            content_type: Content type for uploads
            
        Returns:
            Signed URL
            
        Raises:
            StorageError: If URL generation fails
        """
        try:
            logger.info(f"Generating signed {http_method} URL for gs://{bucket}/{path}")
            
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            
            # Set up arguments for signed URL
            expiration = timedelta(minutes=expiration_minutes)
            kwargs = {
                "version": "v4",
                "expiration": expiration,
                "method": http_method,
            }
            
            # Add content type for PUT requests
            if http_method.upper() == "PUT" and content_type:
                kwargs["content_type"] = content_type
                
            # Generate the URL
            url = blob.generate_signed_url(**kwargs)
            
            logger.info(f"Generated signed URL for gs://{bucket}/{path}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL for gs://{bucket}/{path}: {e}")
            raise StorageError(f"Failed to generate signed URL: {e}")
    
    def get_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """
        Get metadata for a file in GCS.
        
        Args:
            bucket: GCS bucket name
            path: Path to the file in GCS
            
        Returns:
            File metadata as a dictionary
            
        Raises:
            StorageError: If metadata retrieval fails
        """
        try:
            logger.info(f"Getting metadata for gs://{bucket}/{path}")
            
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            
            # Check if the blob exists
            if not blob.exists():
                raise StorageError(f"File gs://{bucket}/{path} does not exist")
                
            # Get metadata
            blob.reload()  # Ensure we have the latest metadata
            
            # Create a dictionary of relevant metadata
            metadata = {
                "name": blob.name,
                "bucket": blob.bucket.name,
                "size": blob.size,
                "updated": blob.updated,
                "content_type": blob.content_type,
                "etag": blob.etag,
                "generation": blob.generation,
                "metageneration": blob.metageneration,
                "md5_hash": blob.md5_hash,
                "storage_class": blob.storage_class,
                "time_created": blob.time_created,
                # Include any custom metadata
                "metadata": blob.metadata or {},
            }
            
            logger.info(f"Got metadata for gs://{bucket}/{path}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for gs://{bucket}/{path}: {e}")
            raise StorageError(f"Failed to get file metadata: {e}")