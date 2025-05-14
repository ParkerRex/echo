"""
Integration tests for API health endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from video_processor.infrastructure.api.server import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test that the health endpoint returns a 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_detailed_endpoint(client):
    """Test that the detailed health endpoint returns service status information."""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "services" in response.json()
    assert "version" in response.json()
    assert "uptime" in response.json()
