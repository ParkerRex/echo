"""
Application settings loaded from environment variables.
"""

import os
from dataclasses import dataclass
from typing import List


@dataclass
class StorageSettings:
    """Google Cloud Storage settings."""

    gcs_bucket: str = os.environ.get("GCS_BUCKET", "video-processor")
    gcs_input_prefix: str = os.environ.get("GCS_INPUT_PREFIX", "uploads/")
    gcs_output_prefix: str = os.environ.get("GCS_OUTPUT_PREFIX", "processed/")
    local_storage_path: str = os.environ.get(
        "LOCAL_STORAGE_PATH", "/tmp/video-processor"
    )
    use_local_storage: bool = (
        os.environ.get("USE_LOCAL_STORAGE", "false").lower() == "true"
    )


@dataclass
class AISettings:
    """AI service settings."""

    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-pro")
    vertex_ai_project: str = os.environ.get("VERTEX_AI_PROJECT", "")
    vertex_ai_location: str = os.environ.get("VERTEX_AI_LOCATION", "us-central1")
    vertex_ai_model: str = os.environ.get("VERTEX_AI_MODEL", "text-bison")
    use_vertex_ai: bool = os.environ.get("USE_VERTEX_AI", "false").lower() == "true"


@dataclass
class YouTubeSettings:
    """YouTube publishing settings."""

    client_secrets_file: str = os.environ.get("YOUTUBE_CLIENT_SECRETS", "")
    token_file: str = os.environ.get("YOUTUBE_TOKEN_FILE", "")
    redirect_uri: str = os.environ.get(
        "YOUTUBE_REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob"
    )
    scopes: List[str] = None

    def __post_init__(self):
        """Initialize default values for collections."""
        if self.scopes is None:
            self.scopes = [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
            ]


@dataclass
class APISettings:
    """API server settings."""

    host: str = os.environ.get("API_HOST", "0.0.0.0")
    port: int = int(os.environ.get("API_PORT", "8080"))
    debug: bool = os.environ.get("API_DEBUG", "false").lower() == "true"
    allowed_origins: List[str] = None

    def __post_init__(self):
        """Initialize default values for collections."""
        if self.allowed_origins is None:
            origins = os.environ.get("ALLOWED_ORIGINS", "*")
            self.allowed_origins = [o.strip() for o in origins.split(",")]


@dataclass
class AppSettings:
    """Main application settings."""

    environment: str = os.environ.get("ENVIRONMENT", "development")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    storage: StorageSettings = None
    ai: AISettings = None
    youtube: YouTubeSettings = None
    api: APISettings = None

    def __post_init__(self):
        """Initialize nested settings."""
        if self.storage is None:
            self.storage = StorageSettings()
        if self.ai is None:
            self.ai = AISettings()
        if self.youtube is None:
            self.youtube = YouTubeSettings()
        if self.api is None:
            self.api = APISettings()


# Create a singleton instance
settings = AppSettings()
