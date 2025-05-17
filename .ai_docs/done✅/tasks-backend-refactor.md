# Video Processor Refactoring Plan

---

## Project Standards Checklist

- [x] All Python environment and package management in `apps/core` is performed using `uv` and `pyproject.toml` only (no pip, venv, conda, poetry, etc.)
- [x] All backend code strictly follows `.cursor/rules/architecture.mdc` (layered architecture, domain separation, import order, error handling, testing, etc.)

**Project Goal:** Refactor the video processing logic from the old `video_processor` directory into the new `apps/core` architecture, leveraging Supabase for Auth and PostgreSQL, and ensuring a good developer experience with local development parity.

---

## Implementation Progress Update (2025-05-16)

### Backend Video Processing API Milestone Complete

- **VideoProcessingService** implemented to orchestrate the video upload and processing pipeline, integrating repositories, storage, AI, and utility classes.
- **Pydantic schemas** for video upload responses, video/job/metadata models are defined.
- **API endpoints** for video upload and job status retrieval are created and registered under `/api/v1/videos`.
- **Router aggregation** pattern established in `api/endpoints/__init__.py` for scalable API structure.
- **main.py** updated to register the aggregated router.
- All type and runtime errors addressed.
- **Backend is now ready for end-to-end testing and frontend integration.**

---

## Final Status (2025-05-17)

### Completed Work

✅ **Core Architecture Implementation**
- All data models defined and migrations created
- Repository layer for database operations complete
- Service layer with business logic implemented
- API endpoints for video upload and processing in place
- Authentication with Supabase JWT integrated

✅ **Testing**
- Unit tests for all components completed
- Integration tests for API endpoints created
- Test fixtures and helpers implemented

✅ **Documentation**
- README updated with setup instructions and API details
- Python docstrings added to critical modules
- API documentation with OpenAPI support configured

### Remaining Tasks

⏳ **Final Verification**
- End-to-end manual testing with real video uploads
- Team review and sign-off on migration completion
- Removal of legacy `apps/core/video_processor` directory after verification

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
        # ... (rest unchanged)
        ```
    * [x]   Task 0.2.5: **Configuration Loading (`apps/core/core/config.py`):**
        *   Create/Update `apps/core/core/config.py`.
        *   Implement a Pydantic `Settings` class inheriting from `BaseSettings` (from `pydantic_settings`) to load configurations from the `.env` file.
        # ... (rest unchanged)
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
    * [x]   Task 3.1: **Video Model (`apps/core/models/video_model.py`):**
        *   Define `VideoModel(Base)`: `id` (PK, Integer, autoincrement), `uploader_user_id` (String, index=True, corresponds to Supabase Auth user ID), `original_filename` (String), `storage_path` (String, unique path in GCS or local filesystem), `content_type` (String), `size_bytes` (Integer), `created_at` (DateTime, default=func.now()), `updated_at` (DateTime, default=func.now(), onupdate=func.now()).
    * [x]   Task 3.2: **Enums (`apps/core/models/enums.py`):**
        *   Define `ProcessingStatus(str, Enum)`: `PENDING = "PENDING"`, `PROCESSING = "PROCESSING"`, `COMPLETED = "COMPLETED"`, `FAILED = "FAILED"`.
    * [x]   Task 3.3: **Video Job Model (`apps/core/models/video_job_model.py`):**
        *   Define `VideoJobModel(Base)`: `id` (PK), `video_id` (Integer, ForeignKey("videos.id")), `status` (SQLAlchemy `EnumType(ProcessingStatus)`), `processing_stages` (JSON or Text, nullable), `error_message` (Text, nullable), `created_at`, `updated_at`. Relationship: `video = relationship("VideoModel")`.
    * [x]   Task 3.4: **Video Metadata Model (`apps/core/models/video_metadata_model.py`):**
        *   Define `VideoMetadataModel(Base)`: `id` (PK), `job_id` (Integer, ForeignKey("video_jobs.id"), unique=True), `title` (String, nullable), `description` (Text, nullable), `tags` (JSON or `sqlalchemy.dialects.postgresql.ARRAY(String)` for PostgreSQL, nullable), `transcript_text` (Text, nullable), `transcript_file_url` (String, nullable), `subtitle_files_urls` (JSON, nullable, e.g., `{"vtt": "url", "srt": "url"}`), `thumbnail_file_url` (String, nullable), `extracted_video_duration_seconds` (Float, nullable), `extracted_video_resolution` (String, nullable), `extracted_video_format` (String, nullable), `show_notes_text` (Text, nullable), `created_at`, `updated_at`. Relationship: `job = relationship("VideoJobModel", back_populates="metadata")`. Add `metadata = relationship("VideoMetadataModel", back_populates="job", uselist=False)` to `VideoJobModel`.
    * [x]   Task 3.5: **Model Imports & Alembic:**
        *   Ensure `apps/core/models/__init__.py` imports all model classes (e.g., `from .video_model import VideoModel`) and `Base`.
        *   Update `apps/core/alembic/env.py` `target_metadata` to `Base.metadata`.
    * [x]   Task 3.6: **Generate and Apply Migrations:**
        *   Run `cd apps/core && alembic revision --autogenerate -m "create_video_processing_tables"`.
        *   Inspect the generated migration script in `apps/core/alembic/versions/`.
        *   Run `cd apps/core && alembic upgrade head` to apply to your local Supabase DB.

4.  **Develop/Enhance Core Libraries (`apps/core/lib/`)**:
    *   **Storage (`apps/core/lib/storage/file_storage.py`):**
        * [x]   Task 4.1: Define `FileStorageService` class. Constructor `__init__(self, settings: Settings)`.
        * [x]   Task 4.2: Method `async save_file(self, file_content: bytes, filename: str, subdir: Optional[str] = "uploads") -> str`:
            *   If `self.settings.STORAGE_BACKEND == "local"`: Save to `{self.settings.LOCAL_STORAGE_PATH}/{subdir}/{filename}`. Ensure directory exists. Return the local path.
            *   If `self.settings.STORAGE_BACKEND == "gcs"`: Use `google-cloud-storage` client to upload to `self.settings.GCS_BUCKET_NAME` under `{subdir}/{filename}`. Return GCS URI `gs://{bucket_name}/{subdir}/{filename}`.
        * [x]   Task 4.3: Method `async download_file(self, storage_path: str, destination_local_path: str) -> str`: Downloads from GCS or copies from local.
        * [x]   Task 4.4: Method `async get_public_url(self, storage_path: str) -> Optional[str]`: Returns HTTP URL for GCS objects or a placeholder for local files.
    *   **AI (`apps/core/lib/ai/`)**:
        * [x]   Task 4.5: **Base Adapter (`base_adapter.py`):** `AIAdapterInterface(ABC)` with `async generate_text(self, prompt: str, context: Optional[str] = None) -> str`, `async transcribe_audio(self, audio_file_path: str) -> str` (returns structured transcript if possible).
        * [x]   Task 4.6: **Gemini Adapter (`gemini_adapter.py`):** `GeminiAdapter(AIAdapterInterface)` using `settings.GEMINI_API_KEY`.
        * [x]   Task 4.7: **AI Client Factory (`ai_client_factory.py`):** `def get_ai_adapter(settings: Settings) -> AIAdapterInterface: return GeminiAdapter(settings)`.
    *   **AI Caching (`apps/core/lib/cache/redis_cache.py`):**
        * [x]   Task 4.8: **Redis Caching System:** `RedisCache` class using `redis-py` (async), settings-driven, with `get`/`set` methods.
        *   Modify AI adapters to use this cache for relevant API calls.
    *   **Utilities (`apps/core/lib/utils/`)**:
        * [x]   Task 4.9: **FFmpeg (`ffmpeg_utils.py`):** `FfmpegUtils` class. Methods: `extract_audio_sync(video_path, output_audio_path)`, `extract_frame_sync(video_path, timestamp_seconds, output_image_path)`, `get_video_metadata_sync(video_path) -> dict`. Use `subprocess.run`. Ensure `ffmpeg` is an accessible command.
        * [x]   Task 4.10: **File Handling (`file_utils.py`):** `FileUtils` class. Methods for temp dir creation/cleanup: `create_temp_dir()`, `cleanup_temp_dir(dir_path)`.
        * [x]   Task 4.11: **Subtitles (`subtitle_utils.py`):** `SubtitleUtils` class. Methods: `generate_vtt(transcript_segments: list) -> str`, `generate_srt(transcript_segments: list) -> str`. Define `transcript_segments` structure (e.g., `[{'text': '...', 'start_time': 0.0, 'end_time': 1.5}, ...]`).
    *   **Authentication Utilities (`apps/core/lib/auth/supabase_auth.py`):**
        * [x]   Task 4.12: Create `AuthenticatedUser(BaseModel)`: `id: str`, `email: Optional[str] = None`, `aud: Optional[str] = None`.
        * [x]   Task 4.13: `async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))) -> AuthenticatedUser:`
            *   Use `python-jose.jwt.decode` with `settings.SUPABASE_JWT_SECRET` and audience `authenticated`.
            *   Extract `sub` (user_id), `email`, `aud`. Return `AuthenticatedUser`. Handle `JWTError` with `HTTPException`.
            *   (Note: `tokenUrl` is a dummy here as Supabase handles token issuance.)

5.  **Error Handling (`apps/core/core/exceptions.py`):**
    * [x]   Task 5.1: Define custom exceptions: `VideoProcessingError(Exception)`, `AINoResponseError(VideoProcessingError)`, `FFmpegError(VideoProcessingError)`.

**Phase 2: Data Access - Operations Layer**

6.  **Implement Repositories (`apps/core/operations/`)**:
    *   (All repo methods accept `db: Session` as first arg. Typically called from services.)
    * [x]   Task 6.1: **Video Repo (`video_repository.py`):** `VideoRepository` class. Methods: `create(...) -> VideoModel`, `get_by_id(...) -> Optional[VideoModel]`.
    * [x]   Task 6.2: **Video Job Repo (`video_job_repository.py`):** `VideoJobRepository` class. Methods: `create(...) -> VideoJobModel`, `get_by_id(...) -> Optional[VideoJobModel]`, `update_status(...) -> VideoJobModel`, `add_processing_stage(...) -> VideoJobModel`.
    * [x]   Task 6.3: **Video Metadata Repo (`video_metadata_repository.py`):** `VideoMetadataRepository` class. Methods: `create_or_update(db: Session, job_id: int, **kwargs) -> VideoMetadataModel`, `get_by_job_id(...) -> Optional[VideoMetadataModel]`.

**Phase 3: Business Logic - Service Layer**

7.  **Develop Core Video Processing Service (`apps/core/services/video_processing_service.py`):**
    * [x]   Task 7.1: Define `VideoProcessingService` class.
        *   `__init__`: Inject instances of `VideoRepository`, `VideoJobRepository`, `VideoMetadataRepository`, `FileStorageService`, `AIAdapterInterface`, `FfmpegUtils`, `SubtitleUtils`, `FileUtils`.
    * [x]   Task 7.2: Method `async initiate_video_processing(self, db: Session, original_filename: str, video_content: bytes, content_type: str, uploader_user_id: str, background_tasks: BackgroundTasks) -> VideoJobModel`:
        *   Save video via `FileStorageService` (e.g., `uploads/{uploader_user_id}/{uuid_filename}`).
        *   Create `VideoModel` via repo.
        *   Create `VideoJobModel` (status PENDING) via repo.
        *   Add `self._execute_processing_pipeline(job_id=new_job.id, video_storage_path=stored_video_path)` to `background_tasks`.
        *   `db.commit()` for initial records. Return `new_job`.
    * [x]   Task 7.3: Method `async _execute_processing_pipeline(self, job_id: int, video_storage_path: str)`:
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
    * [x]   Task 7.4: Method `async get_job_details(self, db: Session, job_id: int, user_id: str) -> Optional[VideoJobModel]`: Fetch job, verify ownership (`job.video.uploader_user_id == user_id`), return job with related video and metadata.

8.  **Supporting Services:**
    * [x]   Task 8.1: `apps/core/services/user_service.py`: Implemented `get_or_create_user_profile(db: Session, auth_user: AuthenticatedUser) -> User`. Ensures a local user profile exists for each authenticated user (Supabase/JWT), using email as the unique identifier and robustly handling missing username/full_name.

**Phase 4: API Layer - Endpoints and Schemas**

9.  **Define API Schemas (`apps/core/api/schemas/`)**:
    * [x]   Task 9.1: Create `video_processing_schemas.py` (and `user_schemas.py` if `UserService` is used).
    * [x]   Task 9.2: Pydantic `VideoUploadResponseSchema(BaseModel)`: `job_id: int`, `status: ProcessingStatus`.
    * [x]   Task 9.3: Pydantic `VideoSchema(BaseModel)`: from `VideoModel`. `model_config = ConfigDict(from_attributes=True)`.
    * [x]   Task 9.4: Pydantic `VideoMetadataSchema(BaseModel)`: from `VideoMetadataModel`. `model_config = ConfigDict(from_attributes=True)`.
    * [x]   Task 9.5: Pydantic `VideoJobSchema(BaseModel)`: from `VideoJobModel`, plus `video: Optional[VideoSchema] = None`, `metadata: Optional[VideoMetadataSchema] = None`. `model_config = ConfigDict(from_attributes=True)`.

10. **Create API Endpoints (`apps/core/api/endpoints/video_processing_endpoints.py`):**
    * [x]   Task 10.1: Create `router = APIRouter()`.
    * [x]   Task 10.2: `POST /upload`, response_model=`VideoUploadResponseSchema`:
        *   Dependencies: `current_user: AuthenticatedUser = Depends(get_current_user)`, `db: Session = Depends(get_db_session)`, `background_tasks: BackgroundTasks`.
        *   Inject `VideoProcessingService`. Call `initiate_video_processing`.
    * [x]   Task 10.3: `GET /jobs/{job_id}`, response_model=`VideoJobSchema`:
        *   Dependencies: `current_user: AuthenticatedUser = Depends(get_current_user)`, `db: Session = Depends(get_db_session)`.
        *   Inject `VideoProcessingService`. Call `get_job_details`. Raise 404 or 403 if not found/not owner.
    * [x]   Task 10.4: **Register Router in `apps/core/main.py`:**
        *   `app.include_router(video_processing_router, prefix="/api/v1/videos", tags=["Video Processing"])`.

**Phase 5: Testing, Documentation, and Cleanup**

11. **Testing (`apps/core/tests/`)**:
    * [x]   Task 11.1: **Unit Tests (`tests/unit/`)**: For models, libs (mock external IO), operations (mock DB session methods), services (mock repo/lib dependencies). YouTube adapter tests completed.
    * [x]   Task 11.2: **Integration Tests (`tests/integration/api/`)**:
        *   Used FastAPI `TestClient` to test endpoints.
        *   Overrode `get_current_user` to handle authorization properly in tests.
        *   Successfully tested `POST /upload` with actual files.
        *   Successfully tested `GET /jobs/{job_id}` for both authenticated and unauthorized requests.
        *   Fixed circular import dependencies between models using string-based relationships.
        *   Updated Pydantic schemas to properly handle datetime fields and nullable values.
        *   All integration tests now pass successfully.

12. **Documentation and Cleanup**:
    * [x]   Task 12.1: Update `apps/core/README.md` (API endpoints, local setup with Supabase CLI, env vars).
    * [x]   Task 12.2: Add Python docstrings (module, class, function levels).
    * [ ]   Task 12.3: (LATER) Securely remove old `apps/core/video_processor` directory after full verification.
    * [x]   Task 12.4: Update this `.ai_docs/progress.md` as tasks are completed.

13. **Unit Tests (Comprehensive Coverage)**:
    * [x]   Task 13.1: Create test file `tests/unit/lib/ai/test_gemini_adapter.py`:
        * Test initialization with valid/invalid API keys
        * Test generate_text method with various prompts and contexts
        * Test transcribe_audio method with sample audio files
        * Test proper error handling for API failures
        * Test caching integration (if implemented)
    * [x]   Task 13.2: Create test file `tests/unit/lib/ai/test_ai_client_factory.py`:
        * Test get_ai_adapter returns correct adapter based on settings
        * Test error handling for unknown adapter types
    * [x]   Task 13.3: Create test file `tests/unit/lib/storage/test_file_storage.py`:
        * Test local storage backend (save_file, download_file, get_public_url)
        * Test GCS storage backend with mocked GCS client
        * Test proper path construction and error handling
        * Test file overwrite behavior
    * [x]   Task 13.4: Create test file `tests/unit/lib/utils/test_ffmpeg_utils.py`:
        * Test extract_audio_sync with mock subprocess
        * Test extract_frame_sync with mock subprocess
        * Test get_video_metadata_sync with mock subprocess
        * Test error handling for FFmpeg failures
    * [x]   Task 13.5: Create test file `tests/unit/lib/utils/test_file_utils.py`:
        * Test create_temp_dir creates directory correctly
        * Test cleanup_temp_dir removes directory correctly
        * Test error handling for filesystem operations
    * [x]   Task 13.6: Create test file `tests/unit/lib/utils/test_subtitle_utils.py`:
        * Test generate_vtt with sample transcript segments
        * Test generate_srt with sample transcript segments
        * Test time format conversions
        * Test handling of malformed input data
    * [x]   Task 13.7: Create test file `tests/unit/lib/cache/test_redis_cache.py`:
        * Test get/set operations with mock Redis client
        * Test TTL handling
        * Test serialization/deserialization of complex objects
        * Test error handling for Redis connection issues
    * [x]   Task 13.8: Create test file `tests/unit/lib/auth/test_supabase_auth.py`:
        * Test get_current_user with valid/invalid tokens
        * Test proper extraction of user data from token
        * Test error handling for malformed tokens
    * [x]   Task 13.9: Create test file `tests/unit/operations/test_video_repository.py`:
        * Test create/get_by_id methods with mock DB session
        * Test error handling for DB errors
    * [x]   Task 13.10: Create test file `tests/unit/operations/test_video_job_repository.py`:
        * Test create/get_by_id methods with mock DB session
        * Test update_status and add_processing_stage methods
        * Test error handling for DB errors
    * [x]   Task 13.11: Create test file `tests/unit/operations/test_video_metadata_repository.py`:
        * Test create_or_update with various metadata fields
        * Test get_by_job_id with mock DB session
        * Test error handling for DB errors
    * [x]   Task 13.12: Create test file `tests/unit/services/test_video_processing_service.py`:
        * Test initiate_video_processing with mock dependencies
        * Test _execute_processing_pipeline with mock dependencies
        * Test get_job_details with mock dependencies
        * Test error handling for various failure scenarios
        * Test proper background task scheduling
    * [x]   Task 13.13: Create test file `tests/unit/services/test_user_service.py`:
        * Test get_or_create_user_profile with various input scenarios
        * Test handling of missing username/full_name
        * Test error handling for DB errors

14. **Integration Testing Enhancements**:
    * [x]   Task 14.1: Create test file `tests/integration/api/test_video_upload_flow.py`:
        * Test full API flow from video upload to completion
        * Test authentication and authorization checks
        * Test proper status code and response schema
        * Test error handling for various failure scenarios
    * [x]   Task 14.2: Create test file `tests/integration/api/test_job_status_retrieval.py`:
        * Test job status retrieval for authorized/unauthorized users
        * Test error handling for non-existent jobs
        * Test proper response schema
    * [x]   Task 14.3: Create fixtures and helpers in `tests/integration/conftest.py`:
        * Add fixture for authenticated user
        * Add fixture for test video file
        * Add fixture for test DB with predefined state

15. **Documentation Enhancements**:
    * [x]   Task 15.1: Add module-level docstrings to all Python files:
        * Document purpose, imports, and exports
        * Include example usage where applicable
    * [x]   Task 15.2: Add class-level docstrings to all classes:
        * Document purpose, initialization parameters, and main methods
        * Include example usage where applicable
    * [x]   Task 15.3: Add function/method-level docstrings to all functions/methods:
        * Document parameters, return values, and exceptions
        * Include type hints and example usage where applicable
    * [x]   Task 15.4: Create `apps/core/README.md`:
        * Add project overview and architecture description
        * Add local development setup instructions (uv, Supabase CLI)
        * Document API endpoints and example requests/responses
        * List environment variables and their purposes
        * Include testing instructions
    * [x]   Task 15.5: Create API documentation with FastAPI's OpenAPI support:
        * Add detailed descriptions to router function docstrings
        * Add examples to Pydantic schemas
        * Configure FastAPI to generate comprehensive docs

16. **Final Verification and Cleanup**:
    * [x]   Task 16.1: Run all unit tests and fix any failures:
        * Execute `cd apps/core && python -m pytest tests/unit -v`
        * Document and fix any failures
    * [x]   Task 16.2: Run all integration tests and fix any failures:
        * Execute `cd apps/core && python -m pytest tests/integration -v`
        * Document and fix any failures
    * [x]   Task 16.3: Verify no imports or dependencies on legacy code:
        * Search for any remaining imports from `video_processor/`
        * Update any code still using legacy structures
    * [ ]   Task 16.4: Conduct end-to-end manual testing:
        * Test video upload with actual video file
        * Verify processing pipeline completes successfully
        * Check all metadata extraction and generation
    * [x]   Task 16.5: Generate test coverage report:
        * Execute `cd apps/core && python -m pytest --cov=. tests/`
        * Identify and address any significant coverage gaps
    * [ ]   Task 16.6: Get team sign-off for migration completion:
        * Present test results and documentation to team
        * Address any feedback or concerns
    * [ ]   Task 16.7: Remove legacy `apps/core/video_processor` directory:
        * Create backup if needed
        * Remove directory and update imports
        * Verify application still works correctly

---
