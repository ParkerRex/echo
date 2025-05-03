"""
Data validation schemas for API requests and responses.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


@dataclass
class GCSUploadUrlRequest:
    """Request schema for GCS upload URL endpoint."""

    filename: str
    content_type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GCSUploadUrlRequest":
        """Create from dictionary."""
        return cls(
            filename=data.get("filename", ""),
            content_type=data.get("content_type"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"filename": self.filename}
        if self.content_type:
            result["content_type"] = self.content_type
        return result


@dataclass
class GCSUploadUrlResponse:
    """Response schema for GCS upload URL endpoint."""

    url: str
    bucket: str
    object_path: str
    gcs_url: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "bucket": self.bucket,
            "object_path": self.object_path,
            "gcs_url": self.gcs_url,
        }


@dataclass
class ErrorResponse:
    """Common error response schema."""

    error: str
    details: Optional[Union[str, Dict[str, Any], List[str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"error": self.error}
        if self.details:
            result["details"] = self.details
        return result
