"""
Integration tests for the Jobs API endpoints.
"""

from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.core.api.schemas.video_processing_schemas import (
    VideoJobSchema,  # For response validation
    VideoMetadataSchema,
    VideoSchema,
)
from apps.core.lib.auth.supabase_auth import (
    AuthenticatedUser,  # For mocking get_current_user
    get_current_user,
)
from apps.core.main import app  # Import the FastAPI application
from apps.core.models.enums import ProcessingStatus

client = TestClient(app)


@pytest.fixture
def mock_authenticated_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id="test-user-id", email="test@example.com", aud="authenticated"
    )


@pytest.fixture
def override_get_current_user(mock_authenticated_user_fixture: AuthenticatedUser):
    """Overrides the get_current_user dependency for testing."""

    # It's important that this inner function matches the signature of the original dependency
    async def _override():
        return mock_authenticated_user_fixture

    return _override


# Test cases for GET /api/v1/jobs/


def test_get_my_processing_jobs_success_default_statuses(
    override_get_current_user_fixture,  # Renamed for clarity
):
    """Test successful retrieval of jobs with default status handling in service."""
    app.dependency_overrides[get_current_user] = override_get_current_user_fixture

    # Mock the service call
    # Provide None for optional nested schemas if not testing their content
    mock_job1 = VideoJobSchema(
        id=1, video_id=1, status=ProcessingStatus.PENDING, video=None, metadata=None
    )
    mock_job2 = VideoJobSchema(
        id=2, video_id=2, status=ProcessingStatus.PROCESSING, video=None, metadata=None
    )
    mock_service_response = [mock_job1, mock_job2]

    with patch(
        "apps.core.api.endpoints.jobs_endpoints.get_user_jobs_by_statuses",
        new_callable=MagicMock,
    ) as mock_service_call:

        async def async_mock_service(*args, **kwargs):
            return mock_service_response

        mock_service_call.side_effect = async_mock_service

        response = client.get("/api/v1/jobs/")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["id"] == mock_job1.id
        assert response_data[1]["id"] == mock_job2.id
        # Service should be called with current_user.id and default statuses (handled by service)
        mock_service_call.assert_called_once()
        # We can add more specific assertions on call_args if needed, e.g., checking user_id
        # call_args = mock_service_call.call_args
        # assert call_args[1]['user_id'] == "test-user-id"
        # assert call_args[1]['statuses'] is None # Endpoint passes None, service defaults

    app.dependency_overrides = {}  # Clear overrides


def test_get_my_processing_jobs_with_specific_statuses(
    override_get_current_user_fixture,  # Renamed for clarity
):
    app.dependency_overrides[get_current_user] = override_get_current_user_fixture

    mock_job_completed = VideoJobSchema(
        id=3, video_id=3, status=ProcessingStatus.COMPLETED, video=None, metadata=None
    )
    mock_service_response_completed = [mock_job_completed]

    with patch(
        "apps.core.api.endpoints.jobs_endpoints.get_user_jobs_by_statuses",
        new_callable=MagicMock,
    ) as mock_service_call:

        async def async_mock_service_completed(*args, **kwargs):
            if kwargs.get("statuses") == [ProcessingStatus.COMPLETED]:
                return mock_service_response_completed
            return []

        mock_service_call.side_effect = async_mock_service_completed

        response = client.get("/api/v1/jobs/?status=COMPLETED")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["id"] == mock_job_completed.id
        mock_service_call.assert_called_once()
        call_args = mock_service_call.call_args
        assert call_args.kwargs["statuses"] == [ProcessingStatus.COMPLETED]

    app.dependency_overrides = {}  # Clear overrides


def test_get_my_processing_jobs_unauthenticated():
    """Test API returns 401 if user is not authenticated."""

    # No override for get_current_user, so it should use the real one which expects a token
    # Or, explicitly override to raise HTTPException(status_code=401)
    async def _override_raise_401():
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Not authenticated")

    # Patch where get_current_user is defined and used by FastAPI's dependency injection
    # This is typically in the module where the dependency is defined.
    with patch(
        "apps.core.lib.auth.supabase_auth.get_current_user", new=_override_raise_401
    ):
        response = client.get("/api/v1/jobs/")
        assert (
            response.status_code == 401
        )  # FastAPI TestClient might convert HTTPException to this


def test_get_my_processing_jobs_invalid_status_parameter(
    override_get_current_user_fixture,  # Added missing fixture to allow auth override
):
    """Test API returns 422 for invalid status query parameter."""
    app.dependency_overrides[get_current_user] = override_get_current_user_fixture

    response = client.get("/api/v1/jobs/?status=INVALID_STATUS_VALUE")
    assert response.status_code == 422  # Unprocessable Entity

    app.dependency_overrides = {}  # Clear overrides
