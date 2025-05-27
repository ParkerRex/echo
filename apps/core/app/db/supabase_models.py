"""
Supabase-generated Python models for Echo database.

These models are generated from the Supabase database schema and should be used
instead of SQLAlchemy models for all database operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ProcessingStatusEnum(str, Enum):
    """Processing status enum matching the database enum."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VideoRow(BaseModel):
    """Video table row model."""
    id: int
    content_type: str
    created_at: datetime
    original_filename: str
    size_bytes: int
    storage_path: str
    updated_at: datetime
    uploader_user_id: str


class VideoInsert(BaseModel):
    """Video table insert model."""
    content_type: str
    original_filename: str
    size_bytes: int
    storage_path: str
    uploader_user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VideoUpdate(BaseModel):
    """Video table update model."""
    content_type: Optional[str] = None
    original_filename: Optional[str] = None
    size_bytes: Optional[int] = None
    storage_path: Optional[str] = None
    uploader_user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VideoJobRow(BaseModel):
    """Video job table row model."""
    id: int
    created_at: datetime
    error_message: Optional[str] = None
    processing_stages: Optional[Dict[str, Any]] = None
    status: ProcessingStatusEnum
    updated_at: datetime
    video_id: int


class VideoJobInsert(BaseModel):
    """Video job table insert model."""
    video_id: int
    status: ProcessingStatusEnum = ProcessingStatusEnum.PENDING
    created_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_stages: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = None


class VideoJobUpdate(BaseModel):
    """Video job table update model."""
    video_id: Optional[int] = None
    status: Optional[ProcessingStatusEnum] = None
    created_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_stages: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = None


class VideoMetadataRow(BaseModel):
    """Video metadata table row model."""
    id: int
    created_at: datetime
    description: Optional[str] = None
    extracted_video_duration_seconds: Optional[float] = None
    extracted_video_format: Optional[str] = None
    extracted_video_resolution: Optional[str] = None
    job_id: int
    show_notes_text: Optional[str] = None
    subtitle_files_urls: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    thumbnail_file_url: Optional[str] = None
    title: Optional[str] = None
    transcript_file_url: Optional[str] = None
    transcript_text: Optional[str] = None
    updated_at: datetime


class VideoMetadataInsert(BaseModel):
    """Video metadata table insert model."""
    job_id: int
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    extracted_video_duration_seconds: Optional[float] = None
    extracted_video_format: Optional[str] = None
    extracted_video_resolution: Optional[str] = None
    show_notes_text: Optional[str] = None
    subtitle_files_urls: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    thumbnail_file_url: Optional[str] = None
    title: Optional[str] = None
    transcript_file_url: Optional[str] = None
    transcript_text: Optional[str] = None
    updated_at: Optional[datetime] = None


class VideoMetadataUpdate(BaseModel):
    """Video metadata table update model."""
    job_id: Optional[int] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    extracted_video_duration_seconds: Optional[float] = None
    extracted_video_format: Optional[str] = None
    extracted_video_resolution: Optional[str] = None
    show_notes_text: Optional[str] = None
    subtitle_files_urls: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    thumbnail_file_url: Optional[str] = None
    title: Optional[str] = None
    transcript_file_url: Optional[str] = None
    transcript_text: Optional[str] = None
    updated_at: Optional[datetime] = None


# Convenience aliases for common usage
Video = VideoRow
VideoJob = VideoJobRow
VideoMetadata = VideoMetadataRow
ProcessingStatus = ProcessingStatusEnum
