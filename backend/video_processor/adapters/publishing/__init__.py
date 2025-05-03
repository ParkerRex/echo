"""
Publishing adapters for video distribution.

This package contains implementations of the PublishingInterface for
various platforms like YouTube, Vimeo, etc.
"""

from video_processor.adapters.publishing.youtube import YouTubeAdapter

__all__ = ["YouTubeAdapter"]
