"""
Global pytest fixtures and configuration.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Set environment variables for testing
os.environ["GOOGLE_CLOUD_PROJECT"] = "automations-457120"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../credentials/service_account.json"


# For tests that need mock storage client
@pytest.fixture
def mock_storage_client():
    """Mock for Google Cloud Storage client."""
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Set up the mock chain
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Return the mock objects for use in tests
    return mock_client, mock_bucket, mock_blob
