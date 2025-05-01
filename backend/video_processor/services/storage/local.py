"""
Local filesystem implementation of the storage service.
"""
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, BinaryIO

from ...utils.error_handling import StorageError
from ...utils.logging import get_logger
from ...utils.file_handling import ensure_directory_exists
from .base import FileContent, StorageService

logger = get_logger(__name__)


class LocalStorageService(StorageService):
    """
    Local filesystem implementation of the storage service.
    
    This is useful for local development and testing without connecting to cloud storage.
    """
    
    def __init__(self, base_path: str = "test_data"):
        """
        Initialize the local storage service.
        
        Args:
            base_path: Base directory to use for storage
        """
        self.base_path = base_path
        ensure_directory_exists(base_path)
    
    def _get_bucket_path(self, bucket: str) -> str:
        """Get the full path for a bucket."""
        return os.path.join(self.base_path, bucket)
    
    def _get_file_path(self, bucket: str, path: str) -> str:
        """Get the full local path for a file."""
        return os.path.join(self._get_bucket_path(bucket), path)
    
    def download_file(self, bucket: str, source_path: str, destination_path: str) -> str:
        """
        Copy a file from the local storage.
        
        Args:
            bucket: Directory name within base_path
            source_path: Path to the file in local storage
            destination_path: Local path to save the file
            
        Returns:
            Local path to the downloaded file
            
        Raises:
            StorageError: If the copy fails
        """
        try:
            source_file = self._get_file_path(bucket, source_path)
            logger.info(f"Copying {source_file} to {destination_path}")
            
            if not os.path.exists(source_file):
                raise StorageError(f"Source file {source_file} does not exist")
                
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_file, destination_path)
            
            logger.info(f"Copy complete: {destination_path}")
            return destination_path
        except Exception as e:
            logger.error(f"Failed to copy {source_path}: {e}")
            raise StorageError(f"Failed to copy file: {e}")
    
    def upload_file(self, bucket: str, source_path: str, destination_path: str) -> str:
        """
        Copy a file to the local storage.
        
        Args:
            bucket: Directory name within base_path
            source_path: Local path to the file
            destination_path: Path to save the file in local storage
            
        Returns:
            Storage path to the uploaded file
            
        Raises:
            StorageError: If the copy fails
        """
        try:
            if not os.path.exists(source_path):
                raise StorageError(f"Source file {source_path} does not exist")
                
            destination_file = self._get_file_path(bucket, destination_path)
            logger.info(f"Copying {source_path} to {destination_file}")
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, destination_file)
            
            logger.info(f"Copy complete: {destination_file}")
            return destination_path
        except Exception as e:
            logger.error(f"Failed to copy {source_path}: {e}")
            raise StorageError(f"Failed to copy file: {e}")
    
    def upload_from_string(self, bucket: str, content: FileContent, destination_path: str) -> str:
        """
        Write content directly to local storage.
        
        Args:
            bucket: Directory name within base_path
            content: Content to write (string, bytes, or file-like object)
            destination_path: Path to save the file in local storage
            
        Returns:
            Storage path to the written file
            
        Raises:
            StorageError: If the write fails
        """
        try:
            destination_file = self._get_file_path(bucket, destination_path)
            logger.info(f"Writing content to {destination_file}")
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)
            
            # Write the content based on its type
            if isinstance(content, str):
                with open(destination_file, 'w') as f:
                    f.write(content)
            elif isinstance(content, bytes):
                with open(destination_file, 'wb') as f:
                    f.write(content)
            elif hasattr(content, 'read'):  # File-like object
                with open(destination_file, 'wb') as f:
                    shutil.copyfileobj(content, f)
            else:
                raise StorageError(f"Unsupported content type: {type(content)}")
            
            logger.info(f"Write complete: {destination_file}")
            return destination_path
        except Exception as e:
            logger.error(f"Failed to write content to {destination_path}: {e}")
            raise StorageError(f"Failed to write content: {e}")
    
    def read_file(self, bucket: str, path: str) -> bytes:
        """
        Read a file from local storage as bytes.
        
        Args:
            bucket: Directory name within base_path
            path: Path to the file in local storage
            
        Returns:
            File content as bytes
            
        Raises:
            StorageError: If the read fails
        """
        try:
            file_path = self._get_file_path(bucket, path)
            logger.info(f"Reading {file_path}")
            
            if not os.path.exists(file_path):
                raise StorageError(f"File {file_path} does not exist")
                
            # Read the file
            with open(file_path, 'rb') as f:
                content = f.read()
                
            logger.info(f"Read {len(content)} bytes from {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read {path}: {e}")
            raise StorageError(f"Failed to read file: {e}")
    
    def read_text(self, bucket: str, path: str, encoding: str = "utf-8") -> str:
        """
        Read a file from local storage as text.
        
        Args:
            bucket: Directory name within base_path
            path: Path to the file in local storage
            encoding: Text encoding to use
            
        Returns:
            File content as text
            
        Raises:
            StorageError: If the read fails
        """
        try:
            file_path = self._get_file_path(bucket, path)
            logger.info(f"Reading text from {file_path}")
            
            if not os.path.exists(file_path):
                raise StorageError(f"File {file_path} does not exist")
                
            # Read the file
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            logger.info(f"Read {len(content)} characters from {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read text from {path}: {e}")
            raise StorageError(f"Failed to read file as text: {e}")
    
    def list_files(self, bucket: str, prefix: Optional[str] = None) -> List[str]:
        """
        List files in local storage with optional prefix.
        
        Args:
            bucket: Directory name within base_path
            prefix: Optional prefix to filter files
            
        Returns:
            List of file paths
            
        Raises:
            StorageError: If the listing fails
        """
        try:
            bucket_path = self._get_bucket_path(bucket)
            logger.info(f"Listing files in {bucket_path}/{prefix or ''}")
            
            if not os.path.exists(bucket_path):
                logger.warning(f"Bucket {bucket} does not exist, returning empty list")
                return []
                
            # Get list of all files
            all_files = []
            prefix_path = os.path.join(bucket_path, prefix or "")
            prefix_dir = os.path.dirname(prefix_path) if prefix else bucket_path
            
            for root, _, files in os.walk(prefix_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    # Convert to bucket-relative path
                    rel_path = os.path.relpath(full_path, bucket_path)
                    
                    # Filter by prefix if provided
                    if prefix and not rel_path.startswith(prefix):
                        continue
                        
                    all_files.append(rel_path)
            
            logger.info(f"Found {len(all_files)} files in {bucket_path}/{prefix or ''}")
            return all_files
        except Exception as e:
            logger.error(f"Failed to list files in {bucket}/{prefix or ''}: {e}")
            raise StorageError(f"Failed to list files: {e}")
    
    def file_exists(self, bucket: str, path: str) -> bool:
        """
        Check if a file exists in local storage.
        
        Args:
            bucket: Directory name within base_path
            path: Path to the file in local storage
            
        Returns:
            True if the file exists, False otherwise
        """
        file_path = self._get_file_path(bucket, path)
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    def delete_file(self, bucket: str, path: str) -> bool:
        """
        Delete a file from local storage.
        
        Args:
            bucket: Directory name within base_path
            path: Path to the file in local storage
            
        Returns:
            True if the file was deleted, False otherwise
        """
        try:
            file_path = self._get_file_path(bucket, path)
            logger.info(f"Deleting {file_path}")
            
            if not os.path.exists(file_path):
                logger.warning(f"File {file_path} does not exist, nothing to delete")
                return False
                
            # Delete the file
            os.remove(file_path)
            
            logger.info(f"Deleted {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {path}: {e}")
            return False
    
    def move_file(self, bucket: str, source_path: str, destination_path: str) -> bool:
        """
        Move a file within local storage.
        
        Args:
            bucket: Directory name within base_path
            source_path: Original path to the file
            destination_path: New path for the file
            
        Returns:
            True if the file was moved, False otherwise
        """
        try:
            source_file = self._get_file_path(bucket, source_path)
            destination_file = self._get_file_path(bucket, destination_path)
            
            logger.info(f"Moving {source_file} to {destination_file}")
            
            if not os.path.exists(source_file):
                logger.warning(f"Source file {source_file} does not exist")
                return False
                
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)
            
            # Move the file
            shutil.move(source_file, destination_file)
            
            logger.info(f"Moved {source_file} to {destination_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to move {source_path}: {e}")
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
        Generate a fake signed URL for local development.
        
        Args:
            bucket: Directory name within base_path
            path: Path to the file in local storage
            expiration_minutes: URL expiration time in minutes
            http_method: HTTP method for the URL (GET, PUT, etc.)
            content_type: Content type for uploads
            
        Returns:
            Local file URL
            
        Raises:
            StorageError: If URL generation fails
        """
        # For local development, just return a direct file path
        file_path = self._get_file_path(bucket, path)
        return f"file://{os.path.abspath(file_path)}"
    
    def get_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """
        Get metadata for a file in local storage.
        
        Args:
            bucket: Directory name within base_path
            path: Path to the file in local storage
            
        Returns:
            File metadata as a dictionary
            
        Raises:
            StorageError: If metadata retrieval fails
        """
        try:
            file_path = self._get_file_path(bucket, path)
            logger.info(f"Getting metadata for {file_path}")
            
            if not os.path.exists(file_path):
                raise StorageError(f"File {file_path} does not exist")
                
            # Get file stats
            stats = os.stat(file_path)
            
            # Create metadata dictionary
            metadata = {
                "name": path,
                "bucket": bucket,
                "size": stats.st_size,
                "updated": datetime.fromtimestamp(stats.st_mtime),
                "time_created": datetime.fromtimestamp(stats.st_ctime),
                "content_type": self._guess_content_type(file_path),
                # Add other metadata similar to GCS for compatibility
                "etag": None,
                "generation": None,
                "metageneration": None,
                "md5_hash": None,
                "storage_class": "STANDARD",
                "metadata": {},
            }
            
            logger.info(f"Got metadata for {file_path}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for {path}: {e}")
            raise StorageError(f"Failed to get file metadata: {e}")
    
    def _guess_content_type(self, file_path: str) -> str:
        """Guess the content type of a file based on its extension."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        content_types = {
            ".txt": "text/plain",
            ".html": "text/html",
            ".htm": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".xml": "application/xml",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".zip": "application/zip",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",
        }
        
        return content_types.get(ext, "application/octet-stream")