"""
API schemas for video-related requests and responses.

This module provides Pydantic models for validating and serializing
video-related data in the API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from video_processor.domain.models.enums import ProcessingStatus


class VideoUploadRequest(BaseModel):
    """Video upload request model."""

    file_path: str = Field(..., description="Path to the video file (local or GCS)")
    title: Optional[str] = Field(None, description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    generate_metadata: bool = Field(
        True, description="Whether to generate metadata automatically"
    )
    publish_to_youtube: bool = Field(
        False, description="Whether to publish to YouTube after processing"
    )


class VideoMetadataRequest(BaseModel):
    """Video metadata request model."""

    title: Optional[str] = Field(None, description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    tags: Optional[List[str]] = Field(None, description="Video tags")
    category_id: Optional[str] = Field(None, description="YouTube category ID")
    privacy_status: Optional[str] = Field(
        "private", description="YouTube privacy status"
    )
    made_for_kids: Optional[bool] = Field(
        False, description="Whether the video is made for kids"
    )


class VideoPublishRequest(BaseModel):
    """Video publish request model."""

    job_id: str = Field(..., description="Job ID of the processed video")
    metadata: Optional[VideoMetadataRequest] = Field(
        None, description="Video metadata for publishing"
    )
    platform: str = Field(
        "youtube",
        description="Publishing platform (currently only 'youtube' is supported)",
    )


class VideoResponse(BaseModel):
    """Video response model."""

    id: str = Field(..., description="Video ID")
    file_path: str = Field(..., description="Path to the video file")
    duration: float = Field(..., description="Video duration in seconds")
    format: str = Field(..., description="Video format")
    resolution: tuple = Field(..., description="Video resolution (width, height)")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @validator("resolution")
    def validate_resolution(cls, v):
        """Validate resolution tuple."""
        if not isinstance(v, tuple) or len(v) != 2:
            raise ValueError("Resolution must be a tuple of (width, height)")
        return v

    class Config:
        """Configuration for the model."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class MetadataResponse(BaseModel):
    """Metadata response model."""

    title: str = Field(..., description="Video title")
    description: str = Field(..., description="Video description")
    tags: List[str] = Field([], description="Video tags")
    show_notes: str = Field("", description="Generated show notes")
    thumbnail_url: Optional[str] = Field(None, description="URL of thumbnail image")
    transcript: Optional[str] = Field(None, description="Full transcript text")
    transcript_url: Optional[str] = Field(None, description="URL to transcript file")
    subtitle_urls: Dict[str, str] = Field(
        {}, description="Dictionary of subtitle format to URL"
    )


class JobResponse(BaseModel):
    """Job response model."""

    id: str = Field(..., description="Job ID")
    status: ProcessingStatus = Field(..., description="Job status")
    video: VideoResponse = Field(..., description="Video information")
    metadata: MetadataResponse = Field(..., description="Video metadata")
    error: Optional[str] = Field(None, description="Error message if status is FAILED")
    processing_stages: Dict[str, Any] = Field(
        {}, description="Processing stage information"
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        """Configuration for the model."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class JobStatusResponse(BaseModel):
    """Job status response model."""

    id: str = Field(..., description="Job ID")
    status: ProcessingStatus = Field(..., description="Job status")
    error: Optional[str] = Field(None, description="Error message if status is FAILED")
    stages: List[str] = Field([], description="Completed processing stages")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        """Configuration for the model."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class PublishResponse(BaseModel):
    """Publish response model."""

    job_id: str = Field(..., description="Job ID")
    platform: str = Field(..., description="Publishing platform")
    platform_id: str = Field(
        ..., description="ID on the publishing platform (e.g., YouTube video ID)"
    )
    status: str = Field(..., description="Publishing status")
    url: Optional[HttpUrl] = Field(None, description="URL to the published video")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Publish timestamp"
    )

    class Config:
        """Configuration for the model."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
