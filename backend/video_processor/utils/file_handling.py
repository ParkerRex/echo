"""
File handling utilities.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from .logging import get_logger

logger = get_logger(__name__)


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False


def get_temp_directory() -> str:
    """
    Create and return a temporary directory path.
    
    Returns:
        Path to a new temporary directory
    """
    return tempfile.mkdtemp()


def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension without the dot
    """
    return os.path.splitext(file_path)[1].lstrip(".")


def normalize_filename(filename: str) -> str:
    """
    Normalize a filename by replacing spaces with hyphens.
    
    Args:
        filename: Original filename
        
    Returns:
        Normalized filename
    """
    return filename.replace(" ", "-")


def get_safe_path(base_directory: str, *paths: str) -> str:
    """
    Create a safe path by joining path components and normalizing.
    
    Args:
        base_directory: Base directory
        *paths: Path components to join
        
    Returns:
        Normalized, safe path
    """
    path = os.path.join(base_directory, *paths)
    return os.path.normpath(path)