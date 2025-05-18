"""
Integration tests for the Jobs API endpoints.
"""

from typing import List, Optional
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from apps.core.api.schemas.video_processing_schemas import (
    VideoJobSchema,  # For response validation
    VideoMetadataSchema,
    VideoSchema,
)
from apps.core.lib.auth.supabase_auth import (
    AuthenticatedUser,  # For mocking get_current_user
    get_current_user,
)
from apps.core.models.enums import ProcessingStatus


@pytest.fixture
def mock_authenticated_user_fixture() -> AuthenticatedUser:
    return AuthenticatedUser(
        id="test-user-id", email="test@example.com", aud="authenticated"
    )


@pytest.fixture
def auth_override(mock_authenticated_user_fixture: AuthenticatedUser):
    """Overrides the get_current_user dependency for testing."""

    # It's important that this inner function matches the signature of the original dependency
    async def _override():
        return mock_authenticated_user_fixture

    return _override


@pytest.fixture
def unauth_override():
    async def _override_raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    return _override_raise_401


# Test cases for GET /api/v1/jobs/


def test_get_my_processing_jobs_success_default_statuses(
    test_client_fixture,
    auth_override,
    mock_authenticated_user_fixture: AuthenticatedUser,
):
    """Test successful retrieval of jobs with default status handling in service."""
    app = test_client_fixture.app
    app.dependency_overrides[get_current_user] = auth_override

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
        new_callable=AsyncMock,
    ) as mock_service_call:

        async def async_mock_service(*args, **kwargs):
            return mock_service_response

        mock_service_call.return_value = mock_service_response

        response = test_client_fixture.get("/api/v1/jobs/")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["id"] == mock_job1.id
        assert response_data[1]["id"] == mock_job2.id
        # Service should be called with current_user.id and default statuses (handled by service)
        mock_service_call.assert_awaited_once_with(
            user_id=mock_authenticated_user_fixture.id,
            db=ANY,
            statuses=None,
        )

    app.dependency_overrides.clear()  # Clear overrides


def test_get_my_processing_jobs_with_specific_statuses(
    test_client_fixture,
    auth_override,
    mock_authenticated_user_fixture: AuthenticatedUser,
):
    app = test_client_fixture.app
    app.dependency_overrides[get_current_user] = auth_override

    mock_job_completed = VideoJobSchema(
        id=3, video_id=3, status=ProcessingStatus.COMPLETED, video=None, metadata=None
    )
    mock_service_response_completed = [mock_job_completed]

    with patch(
        "apps.core.api.endpoints.jobs_endpoints.get_user_jobs_by_statuses",
        new_callable=AsyncMock,
    ) as mock_service_call:

        async def async_mock_service_completed(*args, **kwargs):
            if kwargs.get("statuses") == [ProcessingStatus.COMPLETED]:
                return mock_service_response_completed
            return []

        mock_service_call.return_value = mock_service_response_completed

        response = test_client_fixture.get("/api/v1/jobs/?status=COMPLETED")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["id"] == mock_job_completed.id
        mock_service_call.assert_awaited_once_with(
            user_id=mock_authenticated_user_fixture.id,
            db=ANY,
            statuses=[ProcessingStatus.COMPLETED],
        )

    app.dependency_overrides.clear()  # Clear overrides


def test_get_my_processing_jobs_unauthenticated(test_client_fixture, unauth_override):
    """Test API returns 401 if user is not authenticated."""

    app = test_client_fixture.app
    # Override get_current_user to simulate unauthenticated state
    app.dependency_overrides[get_current_user] = unauth_override

    response = test_client_fixture.get("/api/v1/jobs/")
    assert response.status_code == 401

    app.dependency_overrides.clear()


def test_get_my_processing_jobs_invalid_status_parameter(
    test_client_fixture, auth_override
):
    """Test API returns 422 for invalid status query parameter."""
    app = test_client_fixture.app
    app.dependency_overrides[get_current_user] = auth_override

    response = test_client_fixture.get("/api/v1/jobs/?status=INVALID_STATUS_VALUE")
    assert response.status_code == 422  # Unprocessable Entity

    app.dependency_overrides.clear()  # Clear overrides
