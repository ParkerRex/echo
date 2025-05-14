"""
FastAPI server for the video processing API.

This module provides the main FastAPI application for the video processing API.
"""

from dotenv import load_dotenv

load_dotenv()  # Load .env file at the very beginning

import logging
import os
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from video_processor.domain.exceptions import VideoProcessingError
from video_processor.infrastructure.api.routes import auth_routes, health, videos
from video_processor.infrastructure.config.settings import APISettings

# Configure logger
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Current server time"
    )


def create_app(settings: APISettings = None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        settings: API settings

    Returns:
        Configured FastAPI application
    """
    # Create FastAPI app with metadata for Swagger UI
    app = FastAPI(
        title="Video Processor API",
        description=(
            "API for processing videos, generating transcripts, "
            "and creating metadata"
        ),
        version="1.0.0",
        docs_url=None,  # Disable default docs to customize
        redoc_url=None,  # Disable default redoc to customize
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=(
            settings.cors_origins
            if settings
            else os.environ.get("CORS_ORIGINS", "*").split(",")
        ),
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

    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Add JWT authentication to OpenAPI schema
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token",
            },
            "apiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for authentication",
            },
        }

        openapi_schema["security"] = [{"bearerAuth": []}, {"apiKeyAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Custom docs endpoints
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """Serve custom Swagger UI."""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - API Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        )

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Check if the service is healthy.

        Returns:
            Health status
        """
        return {
            "status": "ok",
            "version": app.version,
            "timestamp": datetime.utcnow(),
        }

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(videos.router, prefix="/api/v1")
    app.include_router(auth_routes.router, prefix="/api/v1")

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
