"""
FastAPI server for the video processing API.

This module provides the main FastAPI application for the video processing API.
"""

import logging
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from video_processor.domain.exceptions import VideoProcessingError
from video_processor.infrastructure.api.routes import health, videos
from video_processor.infrastructure.config.settings import APISettings

# Configure logger
logger = logging.getLogger(__name__)


def create_app(settings: APISettings = None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        settings: API settings

    Returns:
        Configured FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title="Video Processor API",
        description="API for video processing pipeline",
        version="1.0.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins if settings else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers
    @app.exception_handler(VideoProcessingError)
    async def video_processing_error_handler(
        request: Request, exc: VideoProcessingError
    ) -> JSONResponse:
        """Handle video processing errors."""
        return JSONResponse(
            status_code=400,
            content={"error": str(exc), "type": exc.__class__.__name__},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle general exceptions."""
        logger.exception(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)},
        )

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(videos.router, prefix="/api/v1")

    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Run tasks on application startup."""
        logger.info("Starting Video Processor API")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Run tasks on application shutdown."""
        logger.info("Shutting down Video Processor API")

    return app


# Create the FastAPI app instance
app = create_app()


@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint returning API information.

    Returns:
        API information
    """
    return {
        "name": "Video Processor API",
        "version": "1.0.0",
        "status": "operational",
    }
