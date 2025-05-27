"""
Supabase client for Echo backend.

This module provides a clean interface to Supabase database operations
using the official Supabase Python SDK. No code generation needed -
the SDK handles all the typing automatically.
"""

from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from apps.core.core.config import settings


class SupabaseClient:
    """Supabase client wrapper for database operations."""

    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
        )

    # Video operations
    def get_video(self, video_id: int) -> Optional[Dict[str, Any]]:
        """Get a video by ID."""
        response = self.client.table("videos").select("*").eq("id", video_id).execute()
        return response.data[0] if response.data else None

    def get_videos_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all videos for a user."""
        response = self.client.table("videos").select("*").eq("uploader_user_id", user_id).execute()
        return list(response.data) if response.data else []

    def create_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new video record."""
        response = self.client.table("videos").insert(video_data).execute()
        return dict(response.data[0]) if response.data else {}

    def update_video(self, video_id: int, video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a video record."""
        response = self.client.table("videos").update(video_data).eq("id", video_id).execute()
        return response.data[0] if response.data else None

    def delete_video(self, video_id: int) -> bool:
        """Delete a video record."""
        response = self.client.table("videos").delete().eq("id", video_id).execute()
        return len(response.data) > 0

    # Video job operations
    def get_video_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a video job by ID."""
        response = self.client.table("video_jobs").select("*").eq("id", job_id).execute()
        return response.data[0] if response.data else None

    def get_video_jobs_by_video(self, video_id: int) -> List[Dict[str, Any]]:
        """Get all jobs for a video."""
        response = self.client.table("video_jobs").select("*").eq("video_id", video_id).execute()
        return list(response.data) if response.data else []

    def create_video_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new video job."""
        response = self.client.table("video_jobs").insert(job_data).execute()
        return dict(response.data[0]) if response.data else {}

    def update_video_job(self, job_id: int, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a video job."""
        response = self.client.table("video_jobs").update(job_data).eq("id", job_id).execute()
        return response.data[0] if response.data else None

    def get_jobs_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all jobs with a specific status."""
        response = self.client.table("video_jobs").select("*").eq("status", status).execute()
        return list(response.data) if response.data else []

    # Video metadata operations
    def get_video_metadata(self, metadata_id: int) -> Optional[Dict[str, Any]]:
        """Get video metadata by ID."""
        response = self.client.table("video_metadata").select("*").eq("id", metadata_id).execute()
        return response.data[0] if response.data else None

    def get_video_metadata_by_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get video metadata by job ID."""
        response = self.client.table("video_metadata").select("*").eq("job_id", job_id).execute()
        return response.data[0] if response.data else None

    def create_video_metadata(self, metadata_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new video metadata."""
        response = self.client.table("video_metadata").insert(metadata_data).execute()
        return dict(response.data[0]) if response.data else {}

    def update_video_metadata(self, metadata_id: int, metadata_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update video metadata."""
        response = self.client.table("video_metadata").update(metadata_data).eq("id", metadata_id).execute()
        return response.data[0] if response.data else None

    # Complex queries
    def get_video_with_job_and_metadata(self, video_id: int) -> Optional[Dict[str, Any]]:
        """Get video with its latest job and metadata."""
        response = self.client.table("videos").select(
            "*, video_jobs(*, video_metadata(*))"
        ).eq("id", video_id).execute()
        return response.data[0] if response.data else None


# Global client instance
supabase_client = SupabaseClient()


# Dependency function for FastAPI
def get_supabase_client() -> SupabaseClient:
    """Dependency function to get Supabase client."""
    return supabase_client
