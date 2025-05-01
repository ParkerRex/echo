"""
Factory for creating storage service instances.
"""
from typing import Optional

from ...config import get_settings
from ...utils.logging import get_logger
from .base import StorageService
from .gcs import GCSStorageService
from .local import LocalStorageService

logger = get_logger(__name__)


def get_storage_service(
    testing_mode: Optional[bool] = None,
    local_output: Optional[bool] = None,
) -> StorageService:
    """
    Get an appropriate storage service based on configuration.
    
    Args:
        testing_mode: Override testing mode setting
        local_output: Override local output setting
        
    Returns:
        An instance of StorageService
    """
    settings = get_settings()
    
    # Use provided values or fall back to settings
    testing = testing_mode if testing_mode is not None else settings.testing_mode
    local = local_output if local_output is not None else settings.local_output
    
    # In testing or local output mode, use local storage
    if testing or local:
        logger.info("Using LocalStorageService for testing/local output")
        return LocalStorageService()
    
    # Otherwise, use GCS
    logger.info("Using GCSStorageService for production")
    return GCSStorageService()