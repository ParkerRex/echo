import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from apps.core.lib.auth.supabase_auth import get_current_user
from apps.core.models.enums import ProcessingStatus

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_job_status_successful(client: AsyncClient, populated_db):
    """Test successful retrieval of job status for an authorized user."""
    # Get the job from the populated database
    job = populated_db["job"]

    # Make the request
    response = await client.get(f"/api/v1/videos/jobs/{job.id}")

    # Assert response status
    assert response.status_code == status.HTTP_200_OK

    # Verify response format
    json_response = response.json()
    assert "id" in json_response
    assert "status" in json_response
    assert "processing_stages" in json_response
    assert "video" in json_response

    # Verify job data
    assert json_response["id"] == job.id
    assert json_response["status"] == ProcessingStatus.COMPLETED.value

    # Verify video data
    assert json_response["video"]["id"] == populated_db["video"].id
    assert json_response["video"]["uploader_user_id"] == "test-user-id"
    assert json_response["video"]["original_filename"] == "test_video.mp4"


@pytest.mark.asyncio
async def test_get_job_status_nonexistent_job(client: AsyncClient):
    """Test error handling for non-existent job ID."""
    # Use a job ID that doesn't exist
    non_existent_job_id = 9999

    # Make the request
    response = await client.get(f"/api/v1/videos/jobs/{non_existent_job_id}")

    # Should return 404 Not Found
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_job_status_unauthorized_user(client: AsyncClient, populated_db):
    """Test unauthorized access to a job owned by another user."""
    # Get the job from the populated database
    job = populated_db["job"]

    # Temporarily override the auth dependency to return a different user
    from apps.core.lib.auth.supabase_auth import AuthenticatedUser
    from apps.core.main import app

    # Create a different user
    async def mock_different_user():
        return AuthenticatedUser(
            id="different-user-id", email="different@example.com", aud="authenticated"
        )

    # Apply the override
    original_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = mock_different_user

    try:
        # Make the request
        response = await client.get(f"/api/v1/videos/jobs/{job.id}")

        # Should return 403 Forbidden since the job belongs to another user
        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        # Restore the original override
        if original_override:
            app.dependency_overrides[get_current_user] = original_override
        else:
            del app.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_get_job_status_unauthenticated(client: AsyncClient, populated_db):
    """Test job status retrieval for unauthenticated user."""
    # Get the job from the populated database
    job = populated_db["job"]

    # Temporarily override the auth dependency to simulate unauthenticated request
    from fastapi import HTTPException

    from apps.core.main import app

    # Create a function that raises an authentication error
    async def mock_unauthenticated_user():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Apply the override
    original_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = mock_unauthenticated_user

    try:
        # Make the request
        response = await client.get(f"/api/v1/videos/jobs/{job.id}")

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        # Restore the original override
        if original_override:
            app.dependency_overrides[get_current_user] = original_override
        else:
            del app.dependency_overrides[get_current_user]
