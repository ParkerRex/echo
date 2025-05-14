"""
Domain model for video processing job.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from video_processor.domain.models.enums import ProcessingStage, ProcessingStatus
from video_processor.domain.models.metadata import VideoMetadata
from video_processor.domain.models.video import Video


@dataclass
class VideoJob:
    """
    A video processing job.

    Tracks the state of a video being processed, including its
    metadata, processing stage, and output paths.

    The job is the central entity that coordinates the processing
    workflow for a video, maintaining state and tracking progress.
    """

    job_id: str  # Unique identifier for the job
    video: Video  # Reference to the video being processed
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

    def fail(self, error_message: str) -> None:
        """Mark the job as failed with an error message."""
        self.status = ProcessingStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Mark the job as completed."""
        if self.current_stage not in self.completed_stages:
            self.completed_stages.append(self.current_stage)
        self.current_stage = ProcessingStage.COMPLETE
        self.status = ProcessingStatus.COMPLETED
        self.updated_at = datetime.now()

    def is_complete(self) -> bool:
        """Check if the job is complete."""
        return self.status == ProcessingStatus.COMPLETED

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "job_id": self.job_id,
            "video": self.video.to_dict(),
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
        # Convert the nested video dictionary to a Video object
        video = Video.from_dict(data["video"])

        # Convert metadata dictionary to VideoMetadata
        metadata = VideoMetadata.from_dict(data["metadata"])

        return cls(
            job_id=data["job_id"],
            video=video,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=metadata,
            status=ProcessingStatus[data["status"]],
            current_stage=ProcessingStage[data["current_stage"]],
            completed_stages=[ProcessingStage[s] for s in data["completed_stages"]],
            error_message=data.get("error_message"),
            processed_path=data.get("processed_path"),
            output_files=data.get("output_files", {}),
            youtube_video_id=data.get("youtube_video_id"),
        )

    @classmethod
    def create_new(cls, video: Video) -> "VideoJob":
        """Create a new job for the given video."""
        job_id = f"job-{video.id}-{int(datetime.now().timestamp())}"

        # Create default metadata with the video file name as title
        metadata = VideoMetadata(
            title=video.file_name.rsplit(".", 1)[0].replace("_", " ").title()
        )

        return cls(
            job_id=job_id,
            video=video,
            metadata=metadata,
        )
