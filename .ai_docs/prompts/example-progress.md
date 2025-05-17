# Video Processor Refactoring Plan

**Project Goal:** Refactor the video processing logic from the old `video_processor` directory into the new `apps/core` architecture, leveraging Supabase for Auth and PostgreSQL, and ensuring a good developer experience with local development parity.

---

**Phase 0: Project Setup & Essential Configuration**

1.   **Directory Structure & Dependency Setup:**
    * [x]  Task 0.1: **Verify/Create Core Directories:** Ensure the following directories exist within `apps/core/`. If not, create them:
        *   `lib/ai/`
        *   `lib/auth/`
        *   `lib/database/`
        *   `lib/messaging/` (if not already present)
        *   `lib/publishing/`
        *   `lib/storage/`
        *   `lib/utils/`
        *   `api/schemas/`
        *   `api/endpoints/`
        *   `models/`
        *   `operations/`
        *   `services/`
        *   `core/` (for shared core logic like exceptions, config)
        *   `tests/unit/`
        *   `tests/integration/`
    * [x]  Task 0.2: **Initialize Python Dependencies:**
        *   Open `apps/core/pyproject.toml`.
        *   Add necessary dependencies:
            *   `fastapi`, `uvicorn`
            *   `sqlalchemy` (for ORM)
            *   `psycopg2-binary` (PostgreSQL adapter)
            *   `pydantic` (with email validation, settings management)
            *   `pydantic-settings` (for loading from .env)
            *   `python-jose[cryptography]` (for JWT handling)
            *   `python-multipart` (for file uploads)
            *   `google-cloud-storage` (if using GCS)
            *   Relevant AI SDKs (e.g., `google-generativeai`, `google-cloud-aiplatform`)
            *   `alembic` (for database migrations)
            *   `supabase` (Python client, if direct interaction is needed beyond auth)
            *   Testing libraries: `pytest`, `pytest-cov`, `httpx` (for TestClient)
        *   Ensure your project uses a tool like `uv`, `poetry`, or `pdm` to manage dependencies based on `pyproject.toml`. Example: `uv pip install fastapi sqlalchemy psycopg2-binary pydantic pydantic-settings python-jose[cryptography] python-multipart google-cloud-storage google-generativeai alembic supabase pytest pytest-cov httpx uvicorn`

2.  **Supabase Local & Cloud Setup:**
    * [x]   Task 0.2.1: **Cloud Supabase Project:** Set up a Supabase project in the cloud (supabase.com). Enable Google Auth in the Auth providers section.
    * [x]   Task 0.2.2: **Obtain Cloud Credentials:** From your cloud Supabase project settings (Project Settings > API), note down:
        *   Project URL
        *   Anon key (public)
        *   Service role key (secret - keep this very secure)
        *   JWT Secret (Project Settings > API > JWT Settings)
    * [x]   Task 0.2.3: **Local Supabase Setup (Supabase CLI):**
        *   Install Supabase CLI: `npm install supabase --save-dev` (or global install if preferred).
        *   Navigate to your workspace root (or create a `supabase/` directory if you prefer to manage it there) and run `supabase init`. This creates a `supabase` configuration folder.
        *   Run `supabase start`. This command will download necessary Docker images and start local Supabase services. Note the local API URL, anon key, service_role key, and default JWT secret provided in the output.
    * [x]   Task 0.2.4: **Environment Variables (`.env`):**
        *   Create `apps/core/.env.example` with placeholders for all required variables.
        *   Create `apps/core/.env` (this file should be in `.gitignore`). Populate it with your *local Supabase* credentials for development, and any dev API keys for AI/GCS. For production, these will be set as environment variables in your deployment environment.
        ```dotenv
        # apps/core/.env.example
        ENVIRONMENT="development" # "production" or "test"

        # Supabase (Replace with your actual Local Dev Defaults from 'supabase start' output)
        SUPABASE_URL="http://localhost:54321"
        SUPABASE_ANON_KEY="your_local_anon_key"
        SUPABASE_SERVICE_ROLE_KEY="your_local_service_role_key"
        SUPABASE_JWT_SECRET="your_local_default_jwt_secret_at_least_32_characters_long"
        DATABASE_URL="postgresql://postgres:postgres@localhost:54322/postgres" # Default local Supabase DB URL

        # AI Service (Example Gemini)
        GEMINI_API_KEY="your_dev_gemini_api_key"

        # Storage (Local dev uses local file system, GCS for prod)
        STORAGE_BACKEND="local" # "gcs" in production
        LOCAL_STORAGE_PATH="./output_files" # Directory for local file storage (relative to apps/core)
        # GCS_BUCKET_NAME="your_gcs_bucket_name" # For production
        # GOOGLE_APPLICATION_CREDENTIALS_PATH="/path/to/your/gcs_service_account.json" # For production

        # Redis (if used for caching)
        REDIS_HOST="localhost"
        REDIS_PORT="6379"
        ```
    * [x]   Task 0.2.5: **Configuration Loading (`apps/core/core/config.py`):**
        *   Create/Update `apps/core/core/config.py`.
        *   Implement a Pydantic `Settings` class inheriting from `BaseSettings` (from `pydantic_settings`) to load configurations from the `.env` file.
        ```python
        # apps/core/core/config.py
        from typing import Optional
        from pydantic_settings import BaseSettings
        from pathlib import Path

        class Settings(BaseSettings):
            ENVIRONMENT: str = "development"

            # Supabase
            SUPABASE_URL: str
            SUPABASE_ANON_KEY: str
            SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None  # Secret, use with care
            SUPABASE_JWT_SECRET: str
            DATABASE_URL: str

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

            class Config:
                env_file = ".env"
                env_file_encoding = "utf-8"
                extra = "ignore"  # Ignore extra fields from .env

        settings = Settings()
        ```
    * [x]   Task 0.2.6: **Database Connection (`apps/core/lib/database/connection.py`):**
        *   Confirmed: `apps/core/lib/database/connection.py` already provides a FastAPI-compatible SQLAlchemy session generator (`get_db_session`), exports `Base`, and is ready for use in dependency injection and Alembic migrations. No changes needed.
    * [x]   Task 0.2.7: **Database Migrations (Alembic):**
        *   Alembic initialized in `apps/core/` with `alembic init alembic`.
        *   `apps/core/alembic/env.py` configured to:
            *   Import `Base` from `apps.core.lib.database.connection` and set `target_metadata = Base.metadata`.
            *   Import `settings` from `apps.core.core.config` and use `settings.DATABASE_URL` for the connection.
        *   `apps/core/alembic.ini` updated:
            *   `sqlalchemy.url` is blank and a comment explains it is set dynamically from `settings.DATABASE_URL` in env.py.
        *   (After defining models in Phase 1) Create an initial migration: `alembic revision -m "initial_setup_video_processing_tables"` then `alembic upgrade head`. Adhere to `sb-create-migration` guidelines if available.

**Phase 1: Foundation - Models and Core Libraries (Libs)**

3.  **Define Core Data Models (`apps/core/models/`)**:
    *   (All ORM models should inherit from `Base` defined in `apps.core.lib.database.connection`)
    * [ ]   Task 3.1: **Video Model (`apps/core/models/video_model.py`):**
        *   Define `VideoModel(Base)`: `id` (PK, Integer, autoincrement), `uploader_user_id` (String, index=True, corresponds to Supabase Auth user ID), `original_filename` (String), `storage_path` (String, unique path in GCS or local filesystem), `content_type` (String), `size_bytes` (Integer), `created_at` (DateTime, default=func.now()), `updated_at` (DateTime, default=func.now(), onupdate=func.now()).
    * [ ]   Task 3.2: **Enums (`apps/core/models/enums.py`):**
        *   Define `ProcessingStatus(str, Enum)`: `PENDING = "PENDING"`, `PROCESSING = "PROCESSING"`, `COMPLETED = "COMPLETED"`, `FAILED = "FAILED"`.
    * [ ]   Task 3.3: **Video Job Model (`apps/core/models/video_job_model.py`):**
        *   Define `VideoJobModel(Base)`: `id` (PK), `video_id` (Integer, ForeignKey("videos.id")), `status` (SQLAlchemy `EnumType(ProcessingStatus)`), `processing_stages` (JSON or Text, nullable), `error_message` (Text, nullable), `created_at`, `updated_at`. Relationship: `video = relationship("VideoModel")`.
    * [ ]   Task 3.4: **Video Metadata Model (`apps/core/models/video_metadata_model.py`):**
        *   Define `VideoMetadataModel(Base)`: `id` (PK), `job_id` (Integer, ForeignKey("video_jobs.id"), unique=True), `title` (String, nullable), `description` (Text, nullable), `tags` (JSON or `sqlalchemy.dialects.postgresql.ARRAY(String)` for PostgreSQL, nullable), `transcript_text` (Text, nullable), `transcript_file_url` (String, nullable), `subtitle_files_urls` (JSON, nullable, e.g., `{"vtt": "url", "srt": "url"}`), `thumbnail_file_url` (String, nullable), `extracted_video_duration_seconds` (Float, nullable), `extracted_video_resolution` (String, nullable), `extracted_video_format` (String, nullable), `show_notes_text` (Text, nullable), `created_at`, `updated_at`. Relationship: `job = relationship("VideoJobModel", back_populates="metadata")`. Add `metadata = relationship("VideoMetadataModel", back_populates="job", uselist=False)` to `VideoJobModel`.
    * [ ]   Task 3.5: **Model Imports & Alembic:**
        *   Ensure `apps/core/models/__init__.py` imports all model classes (e.g., `from .video_model import VideoModel`) and `Base`.
        *   Update `apps/core/alembic/env.py` `target_metadata` to `Base.metadata`.
    * [ ]   Task 3.6: **Generate and Apply Migrations:**
        *   Run `cd apps/core && alembic revision --autogenerate -m "create_video_processing_tables"`.
        *   Inspect the generated migration script in `apps/core/alembic/versions/`.
        *   Run `cd apps/core && alembic upgrade head` to apply to your local Supabase DB.

4.  **Develop/Enhance Core Libraries (`apps/core/lib/`)**:
    *   **Storage (`apps/core/lib/storage/file_storage.py`):**
        * [ ]   Task 4.1: Define `FileStorageService` class. Constructor `__init__(self, settings: Settings)`.
        * [ ]   Task 4.2: Method `async save_file(self, file_content: bytes, filename: str, subdir: Optional[str] = "uploads") -> str`:
            *   If `self.settings.STORAGE_BACKEND == "local"`: Save to `{self.settings.LOCAL_STORAGE_PATH}/{subdir}/{filename}`. Ensure directory exists. Return the local path.
            *   If `self.settings.STORAGE_BACKEND == "gcs"`: Use `google-cloud-storage` client to upload to `self.settings.GCS_BUCKET_NAME` under `{subdir}/{filename}`. Return GCS URI `gs://{bucket_name}/{subdir}/{filename}`.
        * [ ]   Task 4.3: Method `async download_file(self, storage_path: str, destination_local_path: str) -> str`: Downloads from GCS or copies from local.
        * [ ]   Task 4.4: Method `async get_public_url(self, storage_path: str) -> Optional[str]`: Returns HTTP URL for GCS objects or a placeholder for local files.
    *   **AI (`apps/core/lib/ai/`)**:
        * [ ]   Task 4.5: **Base Adapter (`base_adapter.py`):** `AIAdapterInterface(ABC)` with `async generate_text(self, prompt: str, context: Optional[str] = None) -> str`, `async transcribe_audio(self, audio_file_path: str) -> str` (returns structured transcript if possible).
        * [ ]   Task 4.6: **Gemini Adapter (`gemini_adapter.py`):** `GeminiAdapter(AIAdapterInterface)` using `settings.GEMINI_API_KEY`.
        * [ ]   Task 4.7: **AI Client Factory (`ai_client_factory.py`):** `def get_ai_adapter(settings: Settings) -> AIAdapterInterface: return GeminiAdapter(settings)`.
        * [ ]   Task 4.8: **AI Caching (`apps/core/lib/cache/redis_cache.py`):**
            *   Create `RedisCache` class using `redis-py` (sync or async version). Connect using `settings.REDIS_HOST`, `settings.REDIS_PORT`.
            *   Methods: `get(key)`, `set(key, value, ttl_seconds)`.
            *   Modify AI adapters to use this cache for relevant API calls.
    *   **Utilities (`apps/core/lib/utils/`)**:
        * [ ]   Task 4.9: **FFmpeg (`ffmpeg_utils.py`):** `FfmpegUtils` class. Methods: `extract_audio_sync(video_path, output_audio_path)`, `extract_frame_sync(video_path, timestamp_seconds, output_image_path)`, `get_video_metadata_sync(video_path) -> dict`. Use `subprocess.run`. Ensure `ffmpeg` is an accessible command.
        * [ ]   Task 4.10: **File Handling (`file_utils.py`):** `FileUtils` class. Methods for temp dir creation/cleanup: `create_temp_dir()`, `cleanup_temp_dir(dir_path)`.
        * [ ]   Task 4.11: **Subtitles (`subtitle_utils.py`):** `SubtitleUtils` class. Methods: `generate_vtt(transcript_segments: list) -> str`, `generate_srt(transcript_segments: list) -> str`. Define `transcript_segments` structure (e.g., `[{'text': '...', 'start_time': 0.0, 'end_time': 1.5}, ...]`).
    *   **Authentication Utilities (`apps/core/lib/auth/supabase_auth.py`):**
        * [ ]   Task 4.12: Create `AuthenticatedUser(BaseModel)`: `id: str`, `email: Optional[str] = None`, `aud: Optional[str] = None`.
        * [ ]   Task 4.13: `async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))) -> AuthenticatedUser:`
            *   Use `python-jose.jwt.decode` with `settings.SUPABASE_JWT_SECRET` and audience `authenticated`.
            *   Extract `sub` (user_id), `email`, `aud`. Return `AuthenticatedUser`. Handle `JWTError` with `HTTPException`.
            *   (Note: `tokenUrl` is a dummy here as Supabase handles token issuance.)

5.  **Error Handling (`apps/core/core/exceptions.py`):**
    * [ ]   Task 5.1: Define custom exceptions: `VideoProcessingError(Exception)`, `AINoResponseError(VideoProcessingError)`, `FFmpegError(VideoProcessingError)`.

**Phase 2: Data Access - Operations Layer**

6.  **Implement Repositories (`apps/core/operations/`)**:
    *   (All repo methods accept `db: Session` as first arg. Typically called from services.)
    * [ ]   Task 6.1: **Video Repo (`video_repository.py`):** `VideoRepository` class. Methods: `create(...) -> VideoModel`, `get_by_id(...) -> Optional[VideoModel]`.
    * [ ]   Task 6.2: **Video Job Repo (`video_job_repository.py`):** `VideoJobRepository` class. Methods: `create(...) -> VideoJobModel`, `get_by_id(...) -> Optional[VideoJobModel]`, `update_status(...) -> VideoJobModel`, `add_processing_stage(...) -> VideoJobModel`.
    * [ ]   Task 6.3: **Video Metadata Repo (`video_metadata_repository.py`):** `VideoMetadataRepository` class. Methods: `create_or_update(db: Session, job_id: int, **kwargs) -> VideoMetadataModel`, `get_by_job_id(...) -> Optional[VideoMetadataModel]`.

**Phase 3: Business Logic - Service Layer**

7.  **Develop Core Video Processing Service (`apps/core/services/video_processing_service.py`):**
    * [ ]   Task 7.1: Define `VideoProcessingService` class.
        *   `__init__`: Inject instances of `VideoRepository`, `VideoJobRepository`, `VideoMetadataRepository`, `FileStorageService`, `AIAdapterInterface`, `FfmpegUtils`, `SubtitleUtils`, `FileUtils`.
    * [ ]   Task 7.2: Method `async initiate_video_processing(self, db: Session, original_filename: str, video_content: bytes, content_type: str, uploader_user_id: str, background_tasks: BackgroundTasks) -> VideoJobModel`:
        *   Save video via `FileStorageService` (e.g., `uploads/{uploader_user_id}/{uuid_filename}`).
        *   Create `VideoModel` via repo.
        *   Create `VideoJobModel` (status PENDING) via repo.
        *   Add `self._execute_processing_pipeline(job_id=new_job.id, video_storage_path=stored_video_path)` to `background_tasks`.
        *   `db.commit()` for initial records. Return `new_job`.
    * [ ]   Task 7.3: Method `async _execute_processing_pipeline(self, job_id: int, video_storage_path: str)`:
        *   Use a `with get_db_session() as db_bg:` context for the background task's DB operations.
        *   Fetch job, update status to PROCESSING.
        *   Use `FileUtils.create_temp_dir()`.
        *   **Try/Catch/Finally (for cleanup):**
            *   Download video to temp dir using `FileStorageService`.
            *   **Step 1: Basic Metadata:** `FfmpegUtils.get_video_metadata_sync`. Update `VideoMetadataModel`.
            *   **Step 2: Extract Audio:** `FfmpegUtils.extract_audio_sync` to temp audio file.
            *   **Step 3: Transcript:** `AIAdapter.transcribe_audio`. Store text. Upload `.txt` via `FileStorageService`. Update `VideoMetadataModel`.
            *   **Step 4: Content Metadata:** `AIAdapter.generate_text` for title, desc, tags, show_notes. Update `VideoMetadataModel`.
            *   **Step 5: Subtitles:** `SubtitleUtils` using transcript. Upload `.vtt`, `.srt`. Update `VideoMetadataModel`.
            *   **Step 6: Thumbnail:** `FfmpegUtils.extract_frame_sync`. Upload `.jpg`. Update `VideoMetadataModel`.
            *   Update job to COMPLETED. `db_bg.commit()`.
        *   **Catch:** Log error. Update job to FAILED with error message. `db_bg.commit()`.
        *   **Finally:** `FileUtils.cleanup_temp_dir()`.
    * [ ]   Task 7.4: Method `async get_job_details(self, db: Session, job_id: int, user_id: str) -> Optional[VideoJobModel]`: Fetch job, verify ownership (`job.video.uploader_user_id == user_id`), return job with related video and metadata.

8.  **Supporting Services:**
    * [ ]   Task 8.1: `apps/core/services/user_service.py`: (If needed) `async def get_or_create_user_profile(db: Session, auth_user: AuthenticatedUser) -> UserModel`. Could be called after successful auth to ensure a local user profile exists.

**Phase 4: API Layer - Endpoints and Schemas**

9.  **Define API Schemas (`apps/core/api/schemas/`)**:
    * [ ]   Task 9.1: Create `video_processing_schemas.py` (and `user_schemas.py` if `UserService` is used).
    * [ ]   Task 9.2: Pydantic `VideoUploadResponseSchema(BaseModel)`: `job_id: int`, `status: ProcessingStatus`.
    * [ ]   Task 9.3: Pydantic `VideoSchema(BaseModel)`: from `VideoModel`. `model_config = ConfigDict(from_attributes=True)`.
    * [ ]   Task 9.4: Pydantic `VideoMetadataSchema(BaseModel)`: from `VideoMetadataModel`. `model_config = ConfigDict(from_attributes=True)`.
    * [ ]   Task 9.5: Pydantic `VideoJobSchema(BaseModel)`: from `VideoJobModel`, plus `video: Optional[VideoSchema] = None`, `metadata: Optional[VideoMetadataSchema] = None`. `model_config = ConfigDict(from_attributes=True)`.

10. **Create API Endpoints (`apps/core/api/endpoints/video_processing_endpoints.py`):**
    * [ ]   Task 10.1: Create `router = APIRouter()`.
    * [ ]   Task 10.2: `POST /upload`, response_model=`VideoUploadResponseSchema`:
        *   Dependencies: `current_user: AuthenticatedUser = Depends(get_current_user)`, `db: Session = Depends(get_db_session)`, `background_tasks: BackgroundTasks`.
        *   Inject `VideoProcessingService`. Call `initiate_video_processing`.
    * [ ]   Task 10.3: `GET /jobs/{job_id}`, response_model=`VideoJobSchema`:
        *   Dependencies: `current_user: AuthenticatedUser = Depends(get_current_user)`, `db: Session = Depends(get_db_session)`.
        *   Inject `VideoProcessingService`. Call `get_job_details`. Raise 404 or 403 if not found/not owner.
    * [ ]   Task 10.4: **Register Router in `apps/core/main.py`:**
        *   `app.include_router(video_processing_router, prefix="/api/v1/videos", tags=["Video Processing"])`.

**Phase 5: Testing, Documentation, and Cleanup**

11. **Testing (`apps/core/tests/`)**:
    * [ ]   Task 11.1: **Unit Tests (`tests/unit/`)**: For models, libs (mock external IO), operations (mock DB session methods), services (mock repo/lib dependencies).
    * [ ]   Task 11.2: **Integration Tests (`tests/integration/api/`)**:
        *   Use FastAPI `TestClient`.
        *   Override `get_db_session` to use a test DB (local Supabase test DB).
        *   Override `get_current_user` to return a mock `AuthenticatedUser`.
        *   Test `POST /upload` with actual files. For background tasks, either mock the service method called by it, or check DB for results after a short delay (if feasible for tests).
        *   Test `GET /jobs/{job_id}`.
        *   Configure AI/Storage services to use local/mocked backends for integration tests if possible, or carefully managed dev instances.

12. **Documentation and Cleanup**:
    * [ ]   Task 12.1: Update `apps/core/README.md` (API endpoints, local setup with Supabase CLI, env vars).
    * [ ]   Task 12.2: Add Python docstrings (module, class, function levels).
    * [ ]   Task 12.3: (LATER) Securely remove old `apps/core/video_processor` directory after full verification.
    * [ ]   Task 12.4: Update this `.ai_docs/progress.md` as tasks are completed.

---
