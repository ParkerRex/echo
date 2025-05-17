"""
Configuration settings for the Echo Core application.

This module provides a centralized configuration system using Pydantic Settings.
It loads settings from environment variables and .env files, with sensible defaults
for local development. In production, most settings should be provided via
environment variables.

Usage:
    from apps.core.core.config import settings

    # Access settings in your code
    db_url = settings.DATABASE_URL
    storage_path = settings.LOCAL_STORAGE_PATH
"""

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or .env file.

    This class defines all configuration parameters used throughout the application,
    including database connections, API keys, storage options, and service endpoints.

    For local development, settings are loaded from a .env file. In production,
    they should be set as environment variables in the deployment environment.

    Attributes:
        ENVIRONMENT (str): Runtime environment ('development', 'production', 'test')
        SUPABASE_URL (str): Base URL for Supabase API
        SUPABASE_ANON_KEY (str): Supabase anonymous/public API key
        SUPABASE_SERVICE_ROLE_KEY (Optional[str]): Privileged Supabase API key
        SUPABASE_JWT_SECRET (str): Secret used to verify Supabase JWTs
        DATABASE_URL (str): PostgreSQL connection string
        GEMINI_API_KEY (Optional[str]): Google Gemini AI API key
        OPENAI_API_KEY (Optional[str]): OpenAI API key
        STORAGE_BACKEND (str): Storage backend type ('local' or 'gcs')
        LOCAL_STORAGE_PATH (str): Path for local file storage
        GCS_BUCKET_NAME (Optional[str]): Google Cloud Storage bucket name
        GOOGLE_APPLICATION_CREDENTIALS_PATH (Optional[str]): Path to GCS credentials file
        REDIS_HOST (str): Redis server hostname
        REDIS_PORT (int): Redis server port
        REDIS_DB (int): Redis database index
        REDIS_PASSWORD (str): Redis authentication password
        PROJECT_NAME (str): Human-readable project name
        API_PREFIX (str): Prefix for all API endpoints
        DEBUG (bool): Enable debug mode
        SECRET_KEY (str): Secret key for JWT generation and validation
        ALGORITHM (str): Algorithm used for JWT encoding
        ACCESS_TOKEN_EXPIRE_MINUTES (int): JWT token expiration time in minutes
        SMTP_SERVER (str): SMTP server for sending emails
        SMTP_PORT (int): SMTP server port
        SMTP_USERNAME (str): SMTP authentication username
        SMTP_PASSWORD (str): SMTP authentication password
        EMAIL_FROM_ADDRESS (str): Default sender email address
        EMAIL_TEMPLATES_DIR (str): Directory containing email templates
        UPLOAD_DIR (str): Directory for temporary file uploads
        BASE_DIR (Path): Base directory of the application
    """

    ENVIRONMENT: str = "development"

    # Supabase
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None  # Secret, use with care
    SUPABASE_JWT_SECRET: str = "super-secret-jwt-token-with-at-least-32-characters-long"
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

    # AI Services
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Storage
    STORAGE_BACKEND: str = "local"  # 'local' or 'gcs'
    LOCAL_STORAGE_PATH: str = "./output_files"  # Ensure this path is valid
    GCS_BUCKET_NAME: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS_PATH: Optional[str] = None  # For GCS service account

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # API settings
    PROJECT_NAME: str = "AI-Driven Backend Service"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # JWT settings
    SECRET_KEY: str = "secret_key_for_development_only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM_ADDRESS: str = "noreply@example.com"
    EMAIL_TEMPLATES_DIR: str = "templates/emails"

    # File Upload
    UPLOAD_DIR: str = "uploads"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra fields from .env
    }


# Singleton instance available for import
settings = Settings()
