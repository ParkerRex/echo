"""
Pydantic schemas for video processing API requests and responses.

This module defines the data models used for API input validation and response
serialization in the video processing API endpoints. These schemas provide a
contract between the backend services and API clients, ensuring type safety
and proper documentation.

The schemas are designed to map cleanly to the database models while providing
appropriate defaults, validation rules, and documentation for the API layer.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from apps.core.models.enums import ProcessingStatus

# --- Response Schemas for 3-Table Structure ---


class VideoResponseSchema(BaseModel):
    """Response schema for video file information."""

    id: int = Field(..., description="Unique identifier for the video.")
    uploader_user_id: str = Field(..., description="User ID of the uploader.")
    original_filename: str = Field(..., description="Original filename of the video.")
    storage_path: str = Field(..., description="Storage path of the video file.")
    content_type: str = Field(..., description="MIME type of the video file.")
    size_bytes: int = Field(..., description="Size of the video file in bytes.")
    created_at: datetime = Field(
        ..., description="Timestamp when the video was created."
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the video was last updated."
    )

    model_config = ConfigDict(from_attributes=True)


class VideoJobResponseSchema(BaseModel):
    """Response schema for video processing job information."""

    id: int = Field(..., description="Unique identifier for the processing job.")
    video_id: int = Field(..., description="ID of the associated video.")
    status: ProcessingStatus = Field(..., description="Current processing status.")
    processing_stages: Optional[Dict[str, Any]] = Field(
        default=None, description="Dictionary tracking completion of processing stages."
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if processing failed."
    )
    created_at: datetime = Field(..., description="Timestamp when the job was created.")
    updated_at: datetime = Field(
        ..., description="Timestamp when the job was last updated."
    )

    model_config = ConfigDict(from_attributes=True)


class VideoMetadataResponseSchema(BaseModel):
    """Response schema for video metadata information."""

    id: int = Field(..., description="Unique identifier for the metadata.")
    job_id: int = Field(..., description="ID of the associated processing job.")
    title: Optional[str] = Field(default=None, description="Title of the video.")
    description: Optional[str] = Field(
        default=None, description="Description of the video."
    )
    tags: Optional[List[str]] = Field(
        default=None, description="List of tags for the video."
    )
    transcript_text: Optional[str] = Field(
        default=None, description="Full transcript text."
    )
    transcript_file_url: Optional[str] = Field(
        default=None, description="URL to transcript file."
    )
    subtitle_files_urls: Optional[Dict[str, str]] = Field(
        default=None, description="Dictionary mapping subtitle format to file URLs."
    )
    thumbnail_file_url: Optional[str] = Field(
        default=None, description="URL to thumbnail image."
    )
    extracted_video_duration_seconds: Optional[float] = Field(
        default=None, description="Duration of the video in seconds."
    )
    extracted_video_resolution: Optional[str] = Field(
        default=None, description="Resolution of the video (e.g., '1920x1080')."
    )
    extracted_video_format: Optional[str] = Field(
        default=None, description="Format/codec of the video file."
    )
    show_notes_text: Optional[str] = Field(
        default=None, description="Show notes or summary text."
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the metadata was created."
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the metadata was last updated."
    )

    model_config = ConfigDict(from_attributes=True)


class VideoSummarySchema(BaseModel):
    """Summary schema for video information in lists."""

    id: int = Field(..., description="Unique identifier for the video.")
    original_filename: str = Field(..., description="Original filename of the video.")
    title: Optional[str] = Field(default=None, description="Title of the video.")
    thumbnail_file_url: Optional[str] = Field(
        default=None, description="URL to thumbnail image."
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the video was created."
    )
    status: Optional[ProcessingStatus] = Field(
        default=None, description="Current processing status."
    )

    model_config = ConfigDict(from_attributes=True)


class VideoUploadResponseSchema(BaseModel):
    """Response schema for video upload completion."""

    video_id: int = Field(..., description="ID of the created video record.")
    job_id: int = Field(..., description="ID of the created processing job.")
    status: ProcessingStatus = Field(..., description="Initial processing status.")

    model_config = ConfigDict(from_attributes=True)


class VideoWithJobsResponseSchema(BaseModel):
    """Response schema for video with associated processing jobs."""

    id: int = Field(..., description="Unique identifier for the video.")
    uploader_user_id: str = Field(..., description="User ID of the uploader.")
    original_filename: str = Field(..., description="Original filename of the video.")
    storage_path: str = Field(..., description="Storage path of the video file.")
    content_type: str = Field(..., description="MIME type of the video file.")
    size_bytes: int = Field(..., description="Size of the video file in bytes.")
    created_at: datetime = Field(
        ..., description="Timestamp when the video was created."
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the video was last updated."
    )
    jobs: List[VideoJobResponseSchema] = Field(
        default_factory=list, description="List of associated processing jobs."
    )

    model_config = ConfigDict(from_attributes=True)


class VideoJobWithDetailsResponseSchema(BaseModel):
    """Response schema for processing job with video and metadata details."""

    id: int = Field(..., description="Unique identifier for the processing job.")
    video_id: int = Field(..., description="ID of the associated video.")
    status: ProcessingStatus = Field(..., description="Current processing status.")
    processing_stages: Optional[Dict[str, Any]] = Field(
        default=None, description="Dictionary tracking completion of processing stages."
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if processing failed."
    )
    created_at: datetime = Field(..., description="Timestamp when the job was created.")
    updated_at: datetime = Field(
        ..., description="Timestamp when the job was last updated."
    )
    video: VideoResponseSchema = Field(..., description="Associated video details.")
    video_metadata: Optional[VideoMetadataResponseSchema] = Field(
        default=None, description="Associated metadata details if available."
    )

    model_config = ConfigDict(from_attributes=True)


# --- Request Schemas ---


class VideoMetadataUpdateRequestSchema(BaseModel):
    """Request schema for updating video metadata."""

    title: Optional[str] = Field(default=None, description="New title for the video.")
    description: Optional[str] = Field(
        default=None, description="New description for the video."
    )
    tags: Optional[List[str]] = Field(
        default=None, description="New list of tags for the video."
    )

    model_config = ConfigDict(extra="forbid")


# --- API Client Specific Schemas ---


class ApiErrorDetail(BaseModel):
    """Individual error detail, often part of a list in ApiErrorResponse."""

    loc: Optional[List[Union[str, int]]] = Field(
        default=None, description="Location of the error (e.g., field path)"
    )
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Type of error (e.g., 'value_error')")
    ctx: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context for the error"
    )


class ApiErrorResponse(BaseModel):
    """Standard error response structure for API errors."""

    detail: Union[str, List[ApiErrorDetail]] = Field(
        ..., description="Error message or list of error details"
    )


class SignedUploadUrlRequest(BaseModel):
    """Request schema for obtaining a signed URL for video upload."""

    filename: str = Field(..., description="Original filename of the video.")
    contentType: str = Field(
        ..., alias="content_type", description="MIME type of the video file."
    )
    # Using alias for contentType to match frontend usage, backend might prefer content_type

    model_config = ConfigDict(populate_by_name=True)


class SignedUploadUrlResponse(BaseModel):
    """Response schema after requesting a signed URL."""

    uploadUrl: str = Field(
        ..., alias="upload_url", description="The GCS signed URL for direct PUT upload."
    )
    videoId: str = Field(
        ...,
        alias="video_id",
        description="The unique ID assigned to this video upload attempt/record.",
    )
    # Assuming videoId is a string identifier generated for the upload process,
    # which might later be associated with an integer DB ID.

    model_config = ConfigDict(populate_by_name=True)


class UploadCompleteRequest(BaseModel):
    """Request schema to notify the backend that a direct upload is complete."""

    videoId: str = Field(
        ..., alias="video_id", description="The unique ID of the video upload."
    )
    originalFilename: str = Field(
        ...,
        alias="original_filename",
        description="Original filename of the uploaded video.",
    )
    contentType: str = Field(
        ..., alias="content_type", description="MIME type of the video file."
    )
    sizeBytes: int = Field(
        ..., alias="size_bytes", description="Size of the video file in bytes."
    )
    storagePath: Optional[str] = Field(
        default=None,
        alias="storage_path",
        description="Canonical path in GCS if known by uploader; backend may infer.",
    )
    # Aliases to match frontend camelCase, Python typically uses snake_case.

    model_config = ConfigDict(populate_by_name=True)


class VideoSummary(BaseModel):
    """Summarized video information, typically for lists."""

    id: int = Field(..., description="Unique identifier for the video.")
    original_filename: str = Field(..., description="Original filename of the video.")
    title: Optional[str] = Field(default=None, description="Title of the video.")
    created_at: Optional[datetime] = Field(
        default=None, description="Timestamp of video creation."
    )
    status: Optional[ProcessingStatus] = Field(
        default=None, description="Current processing status of the video."
    )
    thumbnail_file_url: Optional[str] = Field(
        default=None, description="URL to the video's thumbnail."
    )
    # Add other fields like duration, title if available and desired in summary

    model_config = ConfigDict(from_attributes=True)


class VideoMetadataUpdateRequest(BaseModel):
    """Request schema for updating video metadata."""

    title: Optional[str] = Field(default=None, description="New title for the video.")
    description: Optional[str] = Field(
        default=None, description="New description for the video."
    )
    tags: Optional[List[str]] = Field(
        default=None, description="New list of tags for the video."
    )
    # Add other editable metadata fields from VideoMetadataSchema as needed

    model_config = ConfigDict(extra="forbid")  # Prevent unspecified fields


# --- Existing Schemas (ensure they are compatible) ---


class VideoSchema(BaseModel):
    """Schema representing a video file in the system. (Existing)"""

    id: int
    uploader_user_id: str
    original_filename: str
    storage_path: str
    content_type: str
    size_bytes: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VideoMetadataSchema(BaseModel):
    """Schema representing metadata extracted from a processed video. (Existing)"""

    id: Optional[int] = None
    job_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    transcript_text: Optional[str] = None
    transcript_file_url: Optional[str] = None
    subtitle_files_urls: Optional[Dict[str, Any]] = Field(default_factory=dict)
    thumbnail_file_url: Optional[str] = None
    extracted_video_duration_seconds: Optional[float] = None
    extracted_video_resolution: Optional[str] = None
    extracted_video_format: Optional[str] = None
    show_notes_text: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VideoJobSchema(BaseModel):
    """Schema representing a video processing job. (Existing)"""

    id: int
    video_id: int
    status: ProcessingStatus
    processing_stages: Optional[Union[List[str], Dict[str, Any]]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    video: Optional[VideoSchema] = None
    metadata: Optional[VideoMetadataSchema] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class VideoDetailsResponse(
    BaseModel
):  # Renamed from VideoJobSchema for clarity if it's the primary response for video details
    """
    Comprehensive details for a specific video, including its job and metadata.
    This often mirrors VideoJobSchema if that schema is the primary source of truth.
    Alternatively, it can be a composition of VideoSchema, VideoMetadataSchema, and job details.
    Let's make it closely related to VideoJobSchema for now.
    """

    id: int = Field(
        ...,
        description="Video Job ID. If this is for Video Details, this might be Video ID with Job details nested or vice-versa",
    )  # Clarify if this ID is Video or Job
    video_id: int = Field(..., description="Associated Video ID")
    uploader_user_id: Optional[str] = Field(
        None, description="ID of the user who uploaded the video. (Derived from video)"
    )
    original_filename: Optional[str] = Field(
        None, description="Original filename from the upload. (Derived from video)"
    )

    status: ProcessingStatus = Field(
        ..., description="Current status of the processing job."
    )
    processing_stages: Optional[Union[List[str], Dict[str, Any]]] = Field(
        default=None, description="Progress information."
    )
    error_message: Optional[str] = Field(
        default=None, description="Error details if the job failed."
    )

    created_at: Optional[datetime] = Field(
        default=None, description="When the job (or video) was created."
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="When the job (or video) was last updated."
    )

    # Nested video and metadata details
    video: Optional[VideoSchema] = Field(
        default=None, description="Associated video details."
    )
    metadata: Optional[VideoMetadataSchema] = Field(
        default=None, description="Associated metadata details."
    )

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    # If VideoDetailsResponse is intended to be populated from a VideoJobModel that has
    # related VideoModel and VideoMetadataModel, `from_attributes=True` helps.
    # The direct fields like uploader_user_id and original_filename can be populated if
    # the ORM query for VideoJobModel also loads related VideoModel and these are exposed.
    # Otherwise, they might be better inside the nested `video: VideoSchema`.
    # For now, keeping them potentially at top level for flexibility in how backend serves it.


# Ensure all schemas intended for generation are defined above this line or imported.
# ProcessingStatus is an enum and should be handled correctly by pydantic-to-typescript.
