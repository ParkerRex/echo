from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import (  # Keep pydantic BaseModel for custom schemas
    BaseModel,
    ConfigDict,
    Field,
)

# Assuming supabase-pydantic generates models into this path and module
# The actual model names (e.g., Videos, VideoJobs, VideoMetadata) will depend on your table names
# and how supabase-pydantic names them. You'll need to inspect the generated file.
# from apps.core.app.db_pydantic_models.supabase_models import (
#     Videos as GeneratedVideoSchema,
#     VideoJobs as GeneratedVideoJobSchema,
#     VideoMetadata as GeneratedVideoMetadataSchema
# )


# Your existing ProcessingStatus enum
class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# --- API Client Specific Schemas (likely remain unchanged) ---
class ApiErrorDetail(BaseModel):
    loc: Optional[List[Union[str, int]]] = Field(default=None)
    msg: str
    type: str
    ctx: Optional[Dict[str, Any]] = Field(default=None)


class ApiErrorResponse(BaseModel):
    detail: Union[str, List[ApiErrorDetail]]


class SignedUploadUrlRequest(BaseModel):
    filename: str
    content_type: str = Field(..., alias="contentType")
    model_config = ConfigDict(populate_by_name=True)


class SignedUploadUrlResponse(BaseModel):
    upload_url: str = Field(..., alias="uploadUrl")
    video_id: str = Field(..., alias="videoId")
    model_config = ConfigDict(populate_by_name=True)


class UploadCompleteRequest(BaseModel):
    video_id: str = Field(..., alias="videoId")
    original_filename: str = Field(..., alias="originalFilename")
    content_type: str = Field(..., alias="contentType")
    size_bytes: int = Field(..., alias="sizeBytes")
    storage_path: Optional[str] = Field(default=None, alias="storagePath")
    model_config = ConfigDict(populate_by_name=True)


# --- Schemas that might use or be replaced by supabase-pydantic generated models ---


# If supabase-pydantic generates a suitable `VideosSchema`, you might use it directly
# or create a specific API version like this:
class VideoSchema(BaseModel):  # This is your API representation
    id: int
    uploader_user_id: str
    original_filename: str
    storage_path: str  # This might be different from DB model if it's a URL
    content_type: str
    size_bytes: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)  # If mapping from ORM


class VideoMetadataSchema(BaseModel):  # Your API representation
    id: Optional[int] = None
    job_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=lambda: [])
    transcript_text: Optional[str] = None
    transcript_file_url: Optional[str] = None
    subtitle_files_urls: Optional[Dict[str, Any]] = Field(default_factory=lambda: {})
    thumbnail_file_url: Optional[str] = None
    extracted_video_duration_seconds: Optional[float] = None
    extracted_video_resolution: Optional[str] = None
    extracted_video_format: Optional[str] = None
    show_notes_text: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class VideoJobSchema(BaseModel):  # Your API representation
    id: int
    video_id: int
    status: ProcessingStatus  # Use your enum
    processing_stages: Optional[Union[List[str], Dict[str, Any]]] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    video: Optional[VideoSchema] = None  # Nesting your API VideoSchema
    metadata: Optional[VideoMetadataSchema] = (
        None  # Nesting your API VideoMetadataSchema
    )
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class VideoUploadResponseSchema(BaseModel):
    job_id: int
    status: ProcessingStatus  # Use your enum


class VideoSummary(BaseModel):
    id: int
    original_filename: str
    title: Optional[str] = None
    created_at: Optional[str] = None
    status: Optional[ProcessingStatus] = None  # Use your enum
    thumbnail_file_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class VideoMetadataUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    model_config = ConfigDict(extra="forbid")


# VideoDetailsResponse might be identical to VideoJobSchema or a slight variation
class VideoDetailsResponse(VideoJobSchema):  # Example: inheriting if very similar
    pass
