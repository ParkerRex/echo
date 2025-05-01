"""
Global pytest fixtures and configuration.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Set environment variables for testing
os.environ["GOOGLE_CLOUD_PROJECT"] = "automations-457120"

# For CI environment, we'll use the credentials file created by the workflow
# For local testing, we'll use the credentials file in the credentials directory
credentials_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../credentials/service_account.json")
)
if os.path.exists(credentials_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
else:
    # In CI, the credentials file is created in the root directory
    ci_credentials_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../../credentials/service_account.json"
        )
    )
    if os.path.exists(ci_credentials_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ci_credentials_path
    else:
        # If no credentials file is found, we'll use mock authentication
        import pytest
        from unittest.mock import patch

        @pytest.fixture(autouse=True, scope="session")
        def mock_google_auth():
            """Mock Google Cloud authentication for all tests if no credentials file is found."""
            with patch(
                "google.auth.default", return_value=(None, "automations-457120")
            ):
                yield


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
