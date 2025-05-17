import os
import tempfile
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.core.lib.auth.supabase_auth import AuthenticatedUser, get_current_user
from apps.core.lib.database.connection import Base, get_db_session
from apps.core.main import app
from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.models.video_model import VideoModel

# Create test database engine and session
TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db() -> Generator:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the auth dependency to return test user
def override_get_current_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id="test-user-id", email="test@example.com", aud="authenticated"
    )


# Apply test dependency overrides
app.dependency_overrides[get_db_session] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def client() -> TestClient:
    """
    Test client for FastAPI application.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    Create a fresh database session for each test.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Use the session
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        # Drop all tables for a clean slate
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def authenticated_user() -> AuthenticatedUser:
    """
    Return a mock authenticated user.
    """
    return override_get_current_user()


@pytest.fixture
def test_video_file() -> Generator:
    """
    Create a temporary test video file (mock).
    """
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".mp4")

    # Write some dummy data
    with os.fdopen(fd, "wb") as f:
        f.write(b"mock video data")

    # Return the file path
    yield path

    # Clean up after the test
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def populated_db(db_session) -> Dict[str, Any]:
    """
    Populate the database with test data and return the created objects.
    """
    # Create a test video
    test_video = VideoModel(
        uploader_user_id="test-user-id",
        original_filename="test_video.mp4",
        storage_path="uploads/test-user-id/test_video.mp4",
        content_type="video/mp4",
        size_bytes=1024,
    )
    db_session.add(test_video)
    db_session.flush()

    # Create a test job
    test_job = VideoJobModel(
        video_id=test_video.id,
        status=ProcessingStatus.COMPLETED,
        processing_stages={"transcription": True, "metadata": True},
    )
    db_session.add(test_job)
    db_session.commit()

    return {"video": test_video, "job": test_job}
