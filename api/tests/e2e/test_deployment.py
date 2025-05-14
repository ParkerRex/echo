"""End-to-end tests for verifying deployment."""
import os
import pytest
import requests
from typing import Optional


@pytest.fixture
def api_base_url() -> str:
    """Get the base URL of the deployed API from environment variable."""
    # Use environment variable or default to local development URL
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8080")
    # Ensure URL doesn't end with a slash
    return base_url.rstrip("/")


@pytest.fixture
def api_key() -> Optional[str]:
    """Get API key for authentication from environment variable."""
    return os.environ.get("API_KEY")


@pytest.mark.e2e
class TestDeployment:
    """End-to-end tests for verifying deployment."""
    
    def test_health_endpoint(self, api_base_url):
        """Test that the health endpoint is responding."""
        response = requests.get(f"{api_base_url}/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_detailed_health_endpoint(self, api_base_url):
        """Test that the detailed health endpoint is responding."""
        response = requests.get(f"{api_base_url}/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "components" in data
        assert "version" in data
        
        # Check for expected components
        components = data["components"]
        assert "storage" in components
        assert "ai" in components
        assert "database" in components
    
    def test_api_documentation(self, api_base_url):
        """Test that the API documentation is accessible."""
        response = requests.get(f"{api_base_url}/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["Content-Type"]
    
    def test_openapi_schema(self, api_base_url):
        """Test that the OpenAPI schema is accessible."""
        response = requests.get(f"{api_base_url}/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "paths" in schema
        assert "components" in schema
        assert "/videos" in schema["paths"]
    
    @pytest.mark.skipif(not os.environ.get("API_KEY"), reason="API_KEY not set")
    def test_api_key_authentication(self, api_base_url, api_key):
        """Test that API key authentication is working."""
        # Attempt to access protected endpoint without API key
        response_without_key = requests.get(f"{api_base_url}/videos")
        assert response_without_key.status_code in (401, 403)
        
        # Attempt to access protected endpoint with API key
        headers = {"Authorization": f"Bearer {api_key}"}
        response_with_key = requests.get(f"{api_base_url}/videos", headers=headers)
        
        # Should get 200 or 204 if empty list
        assert response_with_key.status_code in (200, 204)
    
    @pytest.mark.skipif(not os.environ.get("API_KEY"), reason="API_KEY not set")
    def test_video_lifecycle(self, api_base_url, api_key):
        """Test basic video processing lifecycle.
        
        This test submits a video processing job and verifies that the API
        responds correctly at each stage. It doesn't test the full processing
        pipeline, just that the API endpoints work.
        """
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # 1. Get pre-signed upload URL
        response = requests.post(
            f"{api_base_url}/videos/upload-url",
            json={"filename": "test_video.mp4"},
            headers=headers
        )
        assert response.status_code == 200
        upload_data = response.json()
        assert "upload_url" in upload_data
        assert "job_id" in upload_data
        
        job_id = upload_data["job_id"]
        
        # 2. Check job status (should be PENDING or similar)
        response = requests.get(
            f"{api_base_url}/videos/job/{job_id}",
            headers=headers
        )
        assert response.status_code == 200
        job_data = response.json()
        assert "status" in job_data
        assert job_data["status"] in ("PENDING", "UPLOADED", "PROCESSING", "FAILED", "COMPLETED")
        
        # 3. Verify job appears in jobs list
        response = requests.get(
            f"{api_base_url}/videos/jobs",
            headers=headers
        )
        assert response.status_code == 200
        jobs_data = response.json()
        assert isinstance(jobs_data, list)
        
        # Find our job in the list
        job_found = False
        for job in jobs_data:
            if job.get("id") == job_id:
                job_found = True
                break
        
        assert job_found, f"Job {job_id} not found in jobs list" 