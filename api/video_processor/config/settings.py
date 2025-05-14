"""
Settings management for the video processor.
"""

from dataclasses import dataclass
from functools import lru_cache

from .environment import get_bool_env, get_env, get_int_env


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # General settings
    project_id: str
    region: str
    testing_mode: bool
    real_api_test: bool
    local_output: bool
    google_application_credentials: str

    # GCS settings
    gcs_upload_bucket: str

    # Supabase settings
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # AI model settings
    ai_model: str

    # YouTube settings
    default_privacy_status: str

    # API settings
    port: int
    debug: bool


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings from environment variables with defaults.

    Returns:
        Settings: Application settings
    """
    return Settings(
        # General settings
        project_id=get_env("GOOGLE_CLOUD_PROJECT", "automations-457120"),
        region=get_env("REGION", "us-east1"),
        testing_mode=get_bool_env("TESTING_MODE", False),
        real_api_test=get_bool_env("REAL_API_TEST", False),
        local_output=get_bool_env("LOCAL_OUTPUT", False),
        google_application_credentials=get_env(
            "GOOGLE_APPLICATION_CREDENTIALS", required=True
        ),
        # GCS settings
        gcs_upload_bucket=get_env(
            "GCS_UPLOAD_BUCKET", "automations-youtube-videos-2025"
        ),
        # Supabase settings
        supabase_url=get_env("SUPABASE_URL", required=True),
        supabase_anon_key=get_env("SUPABASE_ANON_KEY", required=True),
        supabase_service_role_key=get_env("SUPABASE_SERVICE_ROLE_KEY", required=True),
        # AI model settings
        ai_model=get_env("MODEL", "gemini-2.0-flash-001"),
        # YouTube settings
        default_privacy_status=get_env("DEFAULT_PRIVACY_STATUS", "unlisted"),
        # API settings
        port=get_int_env("PORT", 8080),
        debug=get_bool_env("DEBUG", False),
    )
