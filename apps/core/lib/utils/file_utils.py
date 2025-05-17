"""
FileUtils: Utility functions for temporary directory management.

- Provides methods for creating and cleaning up temporary directories.
- Designed for use in the infrastructure/lib layer.

Directory: apps/core/lib/utils/file_utils.py
Layer: Infrastructure/Lib
"""

import os
import shutil
import tempfile
from typing import Optional


class FileUtils:
    """
    Utility class for temporary directory creation and cleanup.
    """

    @staticmethod
    def create_temp_dir(prefix: Optional[str] = "echo_tmp_") -> str:
        """
        Creates a temporary directory for processing.

        Args:
            prefix (Optional[str]): Prefix for the temp directory name.

        Returns:
            str: Path to the created temporary directory.
        """
        return tempfile.mkdtemp(prefix=prefix)

    @staticmethod
    def cleanup_temp_dir(dir_path: str) -> None:
        """
        Removes a temporary directory and all its contents.

        Args:
            dir_path (str): Path to the directory to remove.
        """
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
