import io
import os

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from apps.core.api.schemas.video_processing_schemas import VideoUploadResponseSchema
from apps.core.lib.database.connection import get_db_session
from apps.core.models.enums import ProcessingStatus

# Import the fixtures from conftest.py
pytestmark = pytest.mark.integration


def test_upload_video_successful(client: TestClient, test_video_file: str, db_session):
    """Test successful video upload and initial job creation"""
    # Read the test video file
    with open(test_video_file, "rb") as f:
        file_content = f.read()

    # Create file-like object for multipart upload
    file = io.BytesIO(file_content)

    # Make the request
    response = client.post(
        "/api/v1/videos/upload",
        files={"file": ("test_video.mp4", file, "video/mp4")},
    )

    # Assert response status and format
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()

    # Verify response format matches VideoUploadResponseSchema
    assert "job_id" in json_response
    assert "status" in json_response

    # Get the job ID
    job_id = json_response["job_id"]

    # Verify job was created with PENDING status
    assert json_response["status"] == ProcessingStatus.PENDING.value

    # Verify job exists in database
    db = next(get_db_session())
    from apps.core.operations.video_job_repository import VideoJobRepository

    job_repo = VideoJobRepository()
    job = job_repo.get_by_id(db, job_id)

    assert job is not None
    assert job.status == ProcessingStatus.PENDING

    # Verify video was created in database
    from apps.core.operations.video_repository import VideoRepository

    video_repo = VideoRepository()
    video = video_repo.get_by_id(db, job.video_id)

    assert video is not None
    assert video.uploader_user_id == "test-user-id"
    assert video.original_filename == "test_video.mp4"
    assert video.content_type == "video/mp4"


def test_upload_video_no_file(client: TestClient):
    """Test uploading without a file returns 422"""
    response = client.post("/api/v1/videos/upload")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_video_unsupported_file_type(client: TestClient):
    """Test uploading an unsupported file type"""
    # Create a text file
    file = io.BytesIO(b"This is not a video")

    response = client.post(
        "/api/v1/videos/upload",
        files={"file": ("test.txt", file, "text/plain")},
    )

    # Should return 400 Bad Request for unsupported content type
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_upload_video_unauthenticated(client: TestClient, test_video_file: str):
    """Test upload fails with invalid authentication"""
    # Temporarily override the auth dependency to simulate unauthenticated request
    from fastapi import HTTPException

    from apps.core.lib.auth.supabase_auth import get_current_user
    from apps.core.main import app

    # Create a function that raises an authentication error
    def mock_unauthenticated_user():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Apply the override
    original_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = mock_unauthenticated_user

    try:
        # Read the test video file
        with open(test_video_file, "rb") as f:
            file_content = f.read()

        file = io.BytesIO(file_content)

        # Make the request
        response = client.post(
            "/api/v1/videos/upload",
            files={"file": ("test_video.mp4", file, "video/mp4")},
        )

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        # Restore the original override
        if original_override:
            app.dependency_overrides[get_current_user] = original_override
        else:
            del app.dependency_overrides[get_current_user]


def test_upload_large_video(client: TestClient):
    """Test handling of large video files"""
    # Create a large file (10MB)
    large_file = io.BytesIO(b"0" * (10 * 1024 * 1024))

    response = client.post(
        "/api/v1/videos/upload",
        files={"file": ("large_video.mp4", large_file, "video/mp4")},
    )

    # Should still succeed (assuming no file size limit in the API)
    assert response.status_code == status.HTTP_200_OK
