"""
Dependencies for FastAPI route handlers.

This module provides dependency functions for FastAPI route handlers.
These functions are used with FastAPI's dependency injection system.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.application.interfaces.repositories import (
    JobRepositoryInterface,
    VideoRepositoryInterface,
)
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.application.services.video_processor import VideoProcessorService
from video_processor.infrastructure.config.container import Container

# Configure logger
logger = logging.getLogger(__name__)

# Global dependency injection container
container = Container()


def get_container() -> Container:
    """
    Get the dependency injection container.

    Returns:
        Dependency injection container
    """
    return container


def get_job_repository(
    container: Container = Depends(get_container),
) -> JobRepositoryInterface:
    """
    Get the job repository.

    Args:
        container: Dependency injection container

    Returns:
        Job repository instance
    """
    return container.job_repository()


def get_video_repository(
    container: Container = Depends(get_container),
) -> VideoRepositoryInterface:
    """
    Get the video repository.

    Args:
        container: Dependency injection container

    Returns:
        Video repository instance
    """
    return container.video_repository()


def get_storage_adapter(
    container: Container = Depends(get_container),
) -> StorageInterface:
    """
    Get the storage adapter.

    Args:
        container: Dependency injection container

    Returns:
        Storage adapter instance
    """
    return container.storage_adapter()


def get_ai_adapter(container: Container = Depends(get_container)) -> AIServiceInterface:
    """
    Get the AI service adapter.

    Args:
        container: Dependency injection container

    Returns:
        AI service adapter instance
    """
    return container.ai_adapter()


def get_publishing_adapter(
    container: Container = Depends(get_container),
) -> PublishingInterface:
    """
    Get the publishing adapter.

    Args:
        container: Dependency injection container

    Returns:
        Publishing adapter instance
    """
    return container.publishing_adapter()


def get_video_processor(
    storage_adapter: StorageInterface = Depends(get_storage_adapter),
    ai_adapter: AIServiceInterface = Depends(get_ai_adapter),
    container: Container = Depends(get_container),
) -> VideoProcessorService:
    """
    Get the video processor service.

    Args:
        storage_adapter: Storage adapter dependency
        ai_adapter: AI service adapter dependency
        container: Dependency injection container

    Returns:
        Video processor service instance
    """
    output_bucket = container.settings.storage.output_bucket
    local_output_dir = container.settings.storage.local_output_dir

    return VideoProcessorService(
        storage_adapter=storage_adapter,
        ai_adapter=ai_adapter,
        output_bucket=output_bucket,
        local_output_dir=local_output_dir,
    )


def get_current_user(token: str = Depends(lambda: None)) -> Optional[dict]:
    """
    Get the current authenticated user.

    This is a placeholder for future authentication implementation.
    Currently, it always returns None, meaning no authentication.

    Args:
        token: Authentication token (placeholder)

    Returns:
        User information or None if not authenticated
    """
    # TODO: Implement authentication
    return None


def require_auth(user: Optional[dict] = Depends(get_current_user)) -> dict:
    """
    Require authentication for a route.

    Args:
        user: User information from get_current_user

    Returns:
        User information

    Raises:
        HTTPException: If not authenticated
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
