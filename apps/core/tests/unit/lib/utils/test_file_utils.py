"""
Unit tests for the FileUtils class.
"""

import os
import shutil
from unittest.mock import patch

import pytest

from apps.core.lib.utils.file_utils import FileUtils


class TestFileUtils:
    """Test cases for the FileUtils class."""

    def test_create_temp_dir_default_prefix(self):
        """Test creating a temporary directory with the default prefix."""
        with patch("tempfile.mkdtemp") as mock_mkdtemp:
            mock_mkdtemp.return_value = "/tmp/echo_tmp_12345"

            # Call the method
            temp_dir = FileUtils.create_temp_dir()

            # Verify tempfile.mkdtemp was called with the default prefix
            mock_mkdtemp.assert_called_once_with(prefix="echo_tmp_")

            # Verify the return value
            assert temp_dir == "/tmp/echo_tmp_12345"

    def test_create_temp_dir_custom_prefix(self):
        """Test creating a temporary directory with a custom prefix."""
        with patch("tempfile.mkdtemp") as mock_mkdtemp:
            mock_mkdtemp.return_value = "/tmp/custom_prefix_12345"

            # Call the method with a custom prefix
            temp_dir = FileUtils.create_temp_dir(prefix="custom_prefix_")

            # Verify tempfile.mkdtemp was called with the custom prefix
            mock_mkdtemp.assert_called_once_with(prefix="custom_prefix_")

            # Verify the return value
            assert temp_dir == "/tmp/custom_prefix_12345"

    def test_cleanup_temp_dir_existing(self):
        """Test cleaning up an existing temporary directory."""
        # Create a real temp directory for testing
        temp_dir = os.path.join(os.path.dirname(__file__), "test_temp_dir")
        os.makedirs(temp_dir, exist_ok=True)

        # Create a test file in the directory
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Verify the directory and file exist
        assert os.path.exists(temp_dir)
        assert os.path.exists(test_file)

        # Call the method
        FileUtils.cleanup_temp_dir(temp_dir)

        # Verify the directory and file are gone
        assert not os.path.exists(temp_dir)
        assert not os.path.exists(test_file)

    def test_cleanup_temp_dir_nonexistent(self):
        """Test cleaning up a non-existent directory doesn't raise an error."""
        non_existent_dir = "/tmp/non_existent_dir_12345"

        # Make sure the directory doesn't exist
        if os.path.exists(non_existent_dir):
            shutil.rmtree(non_existent_dir)

        # Verify the directory doesn't exist
        assert not os.path.exists(non_existent_dir)

        # This should not raise an exception
        FileUtils.cleanup_temp_dir(non_existent_dir)

    def test_actual_directory_creation(self):
        """Test the actual creation of a temporary directory."""
        # Call the method
        temp_dir = FileUtils.create_temp_dir(prefix="test_file_utils_")

        try:
            # Verify the directory exists
            assert os.path.exists(temp_dir)

            # Verify the prefix
            assert os.path.basename(temp_dir).startswith("test_file_utils_")

            # Create a test file in the directory
            test_file = os.path.join(temp_dir, "test_file.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            # Verify the file exists
            assert os.path.exists(test_file)

        finally:
            # Clean up
            FileUtils.cleanup_temp_dir(temp_dir)

            # Verify the cleanup worked
            assert not os.path.exists(temp_dir)
