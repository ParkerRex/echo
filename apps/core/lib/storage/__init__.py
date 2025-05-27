from apps.core.lib.storage.file_storage import (
    FileStorageService,
    get_file_storage_service,
)


# Temporary stub for legacy imports
class FileStorage:
    pass


# Temporary alias for legacy import
get_file_storage = get_file_storage_service

__all__ = [
    "FileStorageService",
    "get_file_storage_service",
    "FileStorage",
    "get_file_storage",
]
