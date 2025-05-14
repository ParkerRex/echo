"""
Storage adapters package.

Contains implementations of the StorageInterface for different storage providers.
"""

from video_processor.adapters.storage.gcs import GCSStorageAdapter
from video_processor.adapters.storage.local import LocalStorageAdapter

__all__ = [
    "GCSStorageAdapter",
    "LocalStorageAdapter",
]
