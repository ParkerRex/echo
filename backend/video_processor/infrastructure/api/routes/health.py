"""
Health check routes for the API.

This module provides health check endpoints to verify the API is running and
to check the status of various backend services.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from video_processor.application.interfaces.repositories import JobRepositoryInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.infrastructure.api.dependencies import (
    get_job_repository,
    get_storage_adapter,
)

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/health", tags=["health"])


@router.get("", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Dictionary with status information
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


@router.get("/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check(
    job_repository: JobRepositoryInterface = Depends(get_job_repository),
    storage_adapter: StorageInterface = Depends(get_storage_adapter),
) -> Dict[str, Any]:
    """
    Detailed health check endpoint that verifies backend services are operational.

    Args:
        job_repository: Job repository dependency
        storage_adapter: Storage adapter dependency

    Returns:
        Dictionary with detailed status information
    """
    services_status = {
        "api": {"status": "ok"},
        "job_repository": {"status": "unknown"},
        "storage": {"status": "unknown"},
    }

    # Check job repository
    try:
        # Try to get a dummy job
        job_repository.get_by_id("health-check")
        services_status["job_repository"]["status"] = "ok"
    except Exception as e:
        logger.warning(f"Job repository health check failed: {str(e)}")
        services_status["job_repository"]["status"] = "error"
        services_status["job_repository"]["message"] = str(e)

    # Check storage
    try:
        # Just get the URL format as a simple test
        test_url = storage_adapter.get_public_url("test-file.txt")
        services_status["storage"]["status"] = "ok"
    except Exception as e:
        logger.warning(f"Storage health check failed: {str(e)}")
        services_status["storage"]["status"] = "error"
        services_status["storage"]["message"] = str(e)

    # Overall status
    overall_status = "ok"
    for service in services_status.values():
        if service["status"] == "error":
            overall_status = "degraded"
            break

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": services_status,
    }
