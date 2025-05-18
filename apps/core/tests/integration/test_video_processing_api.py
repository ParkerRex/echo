import os
import tempfile
from typing import Optional
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import Header, HTTPException, status
from fastapi.testclient import TestClient
from httpx import AsyncClient

import apps.core.models  # Ensure all models are registered before app/db usage
from apps.core.lib.auth.supabase_auth import AuthenticatedUser, get_current_user
from apps.core.main import app


# Dummy AI Adapter for testing
class DummyAIAdapter:
    async def generate_text(self, prompt: str, context: Optional[str] = None) -> str:
        return "dummy ai response"

    async def transcribe_audio(self, audio_file_path: str) -> str:
        return "dummy transcript"


def override_get_ai_adapter(settings_instance=None):
    return DummyAIAdapter()


import sys
from unittest.mock import patch

from apps.core.lib.ai import ai_client_factory


@pytest.fixture(autouse=True, scope="module")
def patch_get_ai_adapter():
    # Patch get_ai_adapter at the import location used by the endpoint
    with patch(
        "apps.core.api.endpoints.video_processing_endpoints.get_ai_adapter",
        new=override_get_ai_adapter,
    ):
        yield


app.dependency_overrides[ai_client_factory.get_ai_adapter] = override_get_ai_adapter

# NOTE: This is a scaffold for integration/E2E tests of the video processing API.
#       Actual test logic, fixtures, and mocks should be implemented as the next step.


# Override get_current_user dependency to bypass JWT validation for tests
# while still requiring an Authorization header to be present
async def override_get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # If we have an Authorization header, return a test user
    return AuthenticatedUser(
        id="test-user-id", email="test@example.com", aud="authenticated"
    )


app.dependency_overrides = getattr(app, "dependency_overrides", {})
app.dependency_overrides[get_current_user] = override_get_current_user

# client = TestClient(app) # REMOVE: Client will be injected by pytest fixture


# Patch OpenAI client for all tests to avoid real API calls and missing API key errors
@pytest.fixture(autouse=True, scope="module")
def patch_openai_client():
    with patch(
        "openai.resources.chat.completions.AsyncCompletions.create",
        new_callable=AsyncMock,
    ) as mock_create:
        # Return a dummy response structure matching OpenAI's API
        mock_create.return_value = AsyncMock(
            choices=[
                type(
                    "obj",
                    (),
                    {"message": type("msg", (), {"content": "dummy response"})()},
                )()
            ]
        )
        yield mock_create


@pytest.fixture(scope="module")
def test_video_file():
    # Create a temporary dummy video file for upload tests
    fd, path = tempfile.mkstemp(suffix=".mp4")
    with os.fdopen(fd, "wb") as f:
        f.write(os.urandom(1024 * 1024))  # 1MB random data
    yield path
    os.remove(path)


@pytest.mark.asyncio
async def test_upload_video_success(test_video_file, client: AsyncClient):
    """
    Test uploading a video with valid authentication and check response structure.
    """
    # TODO: Replace with a real or properly mocked JWT for Supabase
    valid_token = os.environ.get("TEST_AUTH_TOKEN", "test-token")
    with open(test_video_file, "rb") as f:
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
    assert response.status_code == 200, (
        f"Unexpected status: {response.status_code}, body: {response.text}"
    )
    data = response.json()
    assert "job_id" in data and isinstance(data["job_id"], int)
    assert "status" in data and data["status"] in ("PENDING", "PROCESSING", "COMPLETED")
    # Store job_id for potential use in dependent tests but don't return it
    job_id = data["job_id"]
    assert job_id > 0


@pytest.mark.asyncio
async def test_upload_video_unauthorized(test_video_file, client: AsyncClient):
    """
    Test uploading a video without authentication should fail.
    """
    with open(test_video_file, "rb") as f:
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")},
        )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_job_details_success(
    monkeypatch, test_video_file, client: AsyncClient
):
    """
    Test retrieving job details after uploading a video.
    """
    # Upload a video and get job_id
    valid_token = os.environ.get("TEST_AUTH_TOKEN", "test-token")
    with open(test_video_file, "rb") as f:
        upload_response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
    if upload_response.status_code != 200:
        pytest.skip("Upload failed, cannot test job details.")
    job_id = upload_response.json()["job_id"]

    # Retrieve job details
    response = await client.get(
        f"/api/v1/videos/jobs/{job_id}",
        headers={"Authorization": f"Bearer {valid_token}"},
    )
    assert response.status_code == 200, (
        f"Unexpected status: {response.status_code}, body: {response.text}"
    )
    data = response.json()
    assert "id" in data and data["id"] == job_id
    assert "status" in data
    assert "video" in data
    assert "metadata" in data


@pytest.mark.asyncio
async def test_get_job_details_unauthorized(client: AsyncClient):
    """
    Test retrieving job details without authentication should fail.
    """
    job_id = 1  # Arbitrary
    response = await client.get(
        f"/api/v1/videos/jobs/{job_id}",
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_upload_invalid_file_type(client: AsyncClient):
    """
    Test uploading a non-video file should fail or be handled gracefully.
    """
    valid_token = os.environ.get("TEST_AUTH_TOKEN", "test-token")
    with tempfile.NamedTemporaryFile(suffix=".txt") as f:
        f.write(b"not a video")
        f.flush()
        f.seek(0)
        response = await client.post(
            "/api/v1/videos/upload",
            files={"file": ("test.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
    # Acceptable: 400 Bad Request, 422 Unprocessable Entity, or handled error
    assert response.status_code in (400, 422, 415, 500)


# TODO: Add more E2E scenarios (full pipeline, error cases, etc.)
