"""
DTO (Data Transfer Object) for VideoJob entity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from video_processor.application.dtos.metadata_dto import MetadataDTO
from video_processor.application.dtos.video_dto import VideoDTO
from video_processor.domain.models.enums import ProcessingStage, ProcessingStatus
from video_processor.domain.models.job import VideoJob


@dataclass
class JobDTO:
    """
    Data Transfer Object for VideoJob entity.

    This DTO is used to transfer job data between layers of the application,
    particularly for API interactions.
    """

    job_id: str
    video: VideoDTO
    status: str  # ProcessingStatus enum name
    current_stage: str  # ProcessingStage enum name
    completed_stages: List[str] = field(
        default_factory=list
    )  # ProcessingStage enum names
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[MetadataDTO] = None
    error_message: Optional[str] = None
    processed_path: Optional[str] = None
    output_files: Dict[str, str] = field(default_factory=dict)
    youtube_video_id: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: VideoJob) -> "JobDTO":
        """
        Create DTO from domain entity.

        Args:
            entity: VideoJob domain entity

        Returns:
            JobDTO object
        """
        video_dto = VideoDTO.from_entity(entity.video)
        metadata_dto = (
            MetadataDTO.from_entity(entity.metadata) if entity.metadata else None
        )

        return cls(
            job_id=entity.job_id,
            video=video_dto,
            status=entity.status.name,
            current_stage=entity.current_stage.name,
            completed_stages=[stage.name for stage in entity.completed_stages],
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            updated_at=entity.updated_at.isoformat() if entity.updated_at else None,
            metadata=metadata_dto,
            error_message=entity.error_message,
            processed_path=entity.processed_path,
            output_files=entity.output_files.copy() if entity.output_files else {},
            youtube_video_id=entity.youtube_video_id,
        )

    def to_entity(self) -> VideoJob:
        """
        Convert DTO to domain entity.

        Returns:
            VideoJob domain entity
        """
        video = self.video.to_entity()
        metadata = self.metadata.to_entity() if self.metadata else None

        created_at = None
        if self.created_at:
            created_at = datetime.fromisoformat(self.created_at)

        updated_at = None
        if self.updated_at:
            updated_at = datetime.fromisoformat(self.updated_at)

        # Convert string enum names to actual enum values
        status = ProcessingStatus[self.status]
        current_stage = ProcessingStage[self.current_stage]
        completed_stages = [ProcessingStage[stage] for stage in self.completed_stages]

        job = VideoJob(
            job_id=self.job_id,
            video=video,
            status=status,
            current_stage=current_stage,
            completed_stages=completed_stages,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
            error_message=self.error_message,
            processed_path=self.processed_path,
            output_files=self.output_files.copy() if self.output_files else {},
            youtube_video_id=self.youtube_video_id,
        )

        return job

    def to_dict(self) -> Dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the DTO
        """
        metadata_dict = self.metadata.to_dict() if self.metadata else None

        return {
            "job_id": self.job_id,
            "video": self.video.to_dict(),
            "status": self.status,
            "current_stage": self.current_stage,
            "completed_stages": self.completed_stages,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": metadata_dict,
            "error_message": self.error_message,
            "processed_path": self.processed_path,
            "output_files": self.output_files,
            "youtube_video_id": self.youtube_video_id,
            # Add computed properties for convenience
            "progress_percent": self._calculate_progress_percent(),
            "duration_seconds": self._calculate_duration_seconds(),
            "has_error": bool(self.error_message),
            "is_complete": self.status == ProcessingStatus.COMPLETED.name,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "JobDTO":
        """
        Create from dictionary.

        Args:
            data: Dictionary with job data

        Returns:
            JobDTO object
        """
        video_dto = VideoDTO.from_dict(data["video"])
        metadata_dto = (
            MetadataDTO.from_dict(data["metadata"]) if data.get("metadata") else None
        )

        return cls(
            job_id=data["job_id"],
            video=video_dto,
            status=data["status"],
            current_stage=data["current_stage"],
            completed_stages=data["completed_stages"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=metadata_dto,
            error_message=data.get("error_message"),
            processed_path=data.get("processed_path"),
            output_files=data.get("output_files", {}),
            youtube_video_id=data.get("youtube_video_id"),
        )

    def _calculate_progress_percent(self) -> int:
        """Calculate job progress as a percentage based on completed stages."""
        total_stages = len(ProcessingStage.__members__) - 1  # Exclude COMPLETE
        completed_count = len(self.completed_stages)

        if self.status == ProcessingStatus.COMPLETED.name:
            return 100
        elif self.status == ProcessingStatus.FAILED.name:
            # For failed jobs, calculate how far it got before failing
            return min(int((completed_count / total_stages) * 100), 99)
        else:
            # For in-progress jobs, calculate based on completed stages
            return min(int((completed_count / total_stages) * 100), 99)

    def _calculate_duration_seconds(self) -> Optional[int]:
        """Calculate job duration in seconds."""
        if not self.created_at or not self.updated_at:
            return None

        created = datetime.fromisoformat(self.created_at)
        updated = datetime.fromisoformat(self.updated_at)

        return int((updated - created).total_seconds())
