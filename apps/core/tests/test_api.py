import pytest
from httpx import AsyncClient  # Changed from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# main.app and its dependency_overrides will be handled by test_client_fixture from conftest
# from main import app
# from lib.database import Base, create_session # Not used directly anymore
# from sqlalchemy import create_engine # Not used directly anymore
# from sqlalchemy.orm import sessionmaker # Not used directly anymore
# from sqlalchemy.pool import StaticPool # Not used directly anymore

# Setup in-memory SQLite for testing - This is now handled by conftest.py
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
# engine = create_engine(
# SQLALCHEMY_DATABASE_URL,
# connect_args={"check_same_thread": False},
# poolclass=StaticPool,
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency - This is now handled by test_client_fixture in conftest.py
# def override_get_db():
# db = TestingSessionLocal()
# try:
# yield db
# finally:
# db.close()


# app.dependency_overrides[create_session] = override_get_db

# client = TestClient(app) # Client will come from test_client_fixture


# @pytest.fixture(scope="function")
# def test_db():
# # Create the database tables - Handled by async_engine_fixture in conftest.py
# Base.metadata.create_all(bind=engine)
# yield
# # Drop the database tables
# Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
async def test_create_user(
    client: AsyncClient,  # Changed from TestClient
):  # client injected from conftest.test_client_fixture
    response = await client.post(  # Added await, client is now AsyncClient
        "/api/v1/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_user(
    client: AsyncClient,  # Changed from TestClient
):  # client injected from conftest.test_client_fixture
    # First create a user
    response_create = await client.post(  # Added await
        "/api/v1/users/",
        json={
            "username": "testuser_get",  # Use a different username to avoid conflicts if tests run in parallel or state leaks
            "email": "testget@example.com",
            "full_name": "Test User Get",
            "password": "password123",
        },
    )
    assert response_create.status_code == 201
    user_id = response_create.json()["id"]

    # Now get the user
    response_get = await client.get(f"/api/v1/users/{user_id}")  # Added await
    assert response_get.status_code == 200
    data_get = response_get.json()
    assert data_get["username"] == "testuser_get"
    assert data_get["email"] == "testget@example.com"
    assert data_get["id"] == user_id
