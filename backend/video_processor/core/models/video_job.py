"""
Video job models for tracking processing state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional


class ProcessingStage(Enum):
    """Stages of video processing."""

    DOWNLOAD = auto()
    EXTRACT_AUDIO = auto()
    GENERATE_TRANSCRIPT = auto()
    GENERATE_SUBTITLES = auto()
    GENERATE_SHOWNOTES = auto()
    GENERATE_CHAPTERS = auto()
    GENERATE_TITLES = auto()
    UPLOAD_OUTPUTS = auto()
    UPLOAD_TO_YOUTUBE = auto()
    COMPLETE = auto()


class ProcessingStatus(Enum):
    """Status of job processing."""

    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PARTIAL = auto()  # Some stages completed but not all


@dataclass
class VideoMetadata:
    """Metadata for a video."""

    title: str
    description: Optional[str] = None
    keywords: Optional[str] = None
    category_id: str = "22"  # Default to "People & Blogs"
    duration_seconds: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    channel: str = "daily"  # 'daily' or 'main'

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "category_id": self.category_id,
            "duration_seconds": self.duration_seconds,
            "width": self.width,
            "height": self.height,
            "channel": self.channel,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VideoMetadata":
        """Create from dictionary."""
        return cls(
            title=data.get("title", ""),
            description=data.get("description"),
            keywords=data.get("keywords"),
            category_id=data.get("category_id", "22"),
            duration_seconds=data.get("duration_seconds"),
            width=data.get("width"),
            height=data.get("height"),
            channel=data.get("channel", "daily"),
        )


@dataclass
class VideoJob:
    """
    A video processing job.

    Tracks the state of a video being processed, including its
    metadata, processing stage, and output paths.
    """

    bucket_name: str
    file_name: str
    job_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: VideoMetadata = field(default_factory=lambda: VideoMetadata(title=""))
    status: ProcessingStatus = ProcessingStatus.PENDING
    current_stage: ProcessingStage = ProcessingStage.DOWNLOAD
    completed_stages: List[ProcessingStage] = field(default_factory=list)
    error_message: Optional[str] = None
    processed_path: Optional[str] = None
    output_files: Dict[str, str] = field(default_factory=dict)
    youtube_video_id: Optional[str] = None

    def update_status(
        self, status: ProcessingStatus, error: Optional[str] = None
    ) -> None:
        """Update the job status and timestamp."""
        self.status = status
        self.updated_at = datetime.now()
        if error:
            self.error_message = error

    def move_to_stage(self, stage: ProcessingStage) -> None:
        """Move to a new processing stage."""
        if self.current_stage not in self.completed_stages:
            self.completed_stages.append(self.current_stage)
        self.current_stage = stage
        self.updated_at = datetime.now()

    def complete_current_stage(self) -> None:
        """Mark the current stage as completed."""
        if self.current_stage not in self.completed_stages:
            self.completed_stages.append(self.current_stage)
        self.updated_at = datetime.now()

    def is_stage_completed(self, stage: ProcessingStage) -> bool:
        """Check if a stage has been completed."""
        return stage in self.completed_stages

    def add_output_file(self, file_type: str, file_path: str) -> None:
        """Add an output file to the job."""
        self.output_files[file_type] = file_path
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "bucket_name": self.bucket_name,
            "file_name": self.file_name,
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata.to_dict(),
            "status": self.status.name,
            "current_stage": self.current_stage.name,
            "completed_stages": [stage.name for stage in self.completed_stages],
            "error_message": self.error_message,
            "processed_path": self.processed_path,
            "output_files": self.output_files,
            "youtube_video_id": self.youtube_video_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VideoJob":
        """Create from dictionary."""
        return cls(
            bucket_name=data["bucket_name"],
            file_name=data["file_name"],
            job_id=data["job_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=VideoMetadata.from_dict(data["metadata"]),
            status=ProcessingStatus[data["status"]],
            current_stage=ProcessingStage[data["current_stage"]],
            completed_stages=[ProcessingStage[s] for s in data["completed_stages"]],
            error_message=data.get("error_message"),
            processed_path=data.get("processed_path"),
            output_files=data.get("output_files", {}),
            youtube_video_id=data.get("youtube_video_id"),
        )
