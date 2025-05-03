"""
API route modules for the video processing API.

This package contains FastAPI router modules for different API endpoints.
"""

from video_processor.infrastructure.api.routes import health, videos

__all__ = ["health", "videos"]
