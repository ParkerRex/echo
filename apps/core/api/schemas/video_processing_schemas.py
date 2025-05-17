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


class VideoUploadResponseSchema(BaseModel):
    """
    Response schema for the video upload endpoint.

    This schema represents the response returned when a video is successfully
    uploaded and processing is initiated. It provides the client with the job ID
    for tracking the processing status and the initial status of the job.

    Attributes:
        job_id (int): The ID of the created video processing job.
        status (ProcessingStatus): The initial status of the job (typically PENDING).
    """

    job_id: int
    status: ProcessingStatus


class VideoSchema(BaseModel):
    """
    Schema representing a video file in the system.

    This schema corresponds to the VideoModel in the database and represents
    the core information about an uploaded video file, including its location,
    type, and ownership information.

    Attributes:
        id (int): Unique identifier for the video.
        uploader_user_id (str): ID of the user who uploaded the video.
        original_filename (str): Original filename from the upload.
        storage_path (str): Path where the file is stored in the storage backend.
        content_type (str): MIME type of the video file.
        size_bytes (int): Size of the video file in bytes.
        created_at (datetime): When the video was uploaded.
        updated_at (datetime): When the video record was last updated.
    """

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
    """
    Schema representing metadata extracted from a processed video.

    This schema corresponds to the VideoMetadataModel in the database and contains
    all the information extracted or generated during video processing, including
    AI-generated content, transcripts, technical metadata, and asset URLs.

    All fields are optional because metadata is generated incrementally during
    the processing pipeline, and the schema needs to handle partially completed jobs.

    Attributes:
        id (int): Unique identifier for the metadata record.
        job_id (int): ID of the associated processing job.
        title (str): AI-generated or user-provided title for the video.
        description (str): AI-generated or user-provided description.
        tags (List[str]): Keywords/tags related to the video content.
        transcript_text (str): Full text transcript of the video's audio.
        transcript_file_url (str): URL to the stored transcript file.
        subtitle_files_urls (Dict[str, Any]): URLs to subtitle files in various formats.
        thumbnail_file_url (str): URL to the generated thumbnail image.
        extracted_video_duration_seconds (float): Duration of the video in seconds.
        extracted_video_resolution (str): Resolution of the video (e.g., "1920x1080").
        extracted_video_format (str): Format/codec of the video.
        show_notes_text (str): AI-generated or user-provided show notes.
        created_at (datetime): When the metadata record was created.
        updated_at (datetime): When the metadata record was last updated.
    """

    # Required fields
    id: Optional[int] = None
    job_id: Optional[int] = None

    # Optional fields with defaults
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
    """
    Schema representing a video processing job.

    This schema corresponds to the VideoJobModel in the database and represents
    the status and progress of a video processing task. It includes nested schemas
    for the associated video and metadata, making it a comprehensive representation
    of the processing state.

    This is the primary schema returned by the job status endpoint, providing
    clients with complete information about their video processing request.

    Attributes:
        id (int): Unique identifier for the job.
        video_id (int): ID of the associated video.
        status (ProcessingStatus): Current status of the processing job.
        processing_stages (Union[List[str], Dict[str, Any]]): Progress information.
        error_message (str): Error details if the job failed.
        created_at (datetime): When the job was created.
        updated_at (datetime): When the job was last updated.
        video (VideoSchema): Associated video details.
        metadata (VideoMetadataSchema): Associated metadata details.
    """

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
