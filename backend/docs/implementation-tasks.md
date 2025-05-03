# Video Processing Pipeline Implementation Tasks - Atomized

This document provides detailed, step-by-step implementation tasks for refactoring the video processing pipeline. Each task is broken down into atomic units with specific guidance for junior developers.

## Phase 1: Core Architecture & Domain Model

### Task 1.1: Project Structure Setup

1. **Create base directory structure** ✅
   - Create the following directories:
     ```
     video_processor/
     ├── adapters/
     │   ├── ai/
     │   │   └── gemini.py
     │   ├── publishing/
     │   └── storage/
     ├── application/
     │   ├── dtos/
     │   ├── interfaces/
     │   └── services/
     ├── domain/
     │   └── models/
     ├── infrastructure/
     │   ├── api/
     │   │   └── routes/
     │   ├── config/
     │   ├── messaging/
     │   └── repositories/
     └── utils/
     ```
   - Success criteria: Directory structure exists as specified

2. **Create pyproject.toml**
   - Create `pyproject.toml` in the project root
   - Include these sections:
     - `[build-system]` with dependencies
     - `[project]` with name, version, description
     - `[project.dependencies]` listing all required packages
     - `[project.optional-dependencies]` for dev dependencies
     - `[tool.pytest]` for test configuration
     - `[tool.black]` for code formatting
     - `[tool.ruff]` for linting
   - Success criteria: Valid TOML file that can be parsed without errors

3. **Configure pre-commit hooks**
   - Create `.pre-commit-config.yaml` in the project root
   - Configure hooks for:
     - black (code formatting)
     - ruff (linting)
     - mypy (type checking)
     - pytest (test running)
   - Success criteria: Running `pre-commit install` succeeds without errors

4. **Create package initialization files** ✅
   - Add empty `__init__.py` files to all directories created in step 1
   - In the root `__init__.py`, add version information
   - Success criteria: All directories are valid Python packages

### Task 1.2: Domain Model Implementation

1. **Create Video entity** ✅
   - Create `video_processor/domain/models/video.py`
   - Implement `Video` class with these attributes:
     - `id`: unique identifier
     - `file_path`: path to video file
     - `duration`: video duration in seconds
     - `format`: video format
     - `resolution`: video resolution (width, height)
     - `created_at`: creation timestamp
   - Add relevant methods:
     - `get_thumbnail_time()`: calculate ideal thumbnail timestamp
     - `get_file_extension()`
     - `is_valid_video()`
   - Success criteria: Class can be instantiated with test data

2. **Extract VideoMetadata** ✅
   - Create `video_processor/domain/models/metadata.py`
   - Copy the metadata-related fields from existing `VideoJob` class in `video_processor/core/models/video_job.py` (lines ~30-50)
   - Add these fields:
     - `title`: video title
     - `description`: video description
     - `tags`: list of tags
     - `show_notes`: generated show notes
     - `thumbnail_url`: URL of thumbnail
     - `transcript`: full transcript text
   - Success criteria: Class matches all fields in current implementation

3. **Refactor VideoJob** ✅
   - Create `video_processor/domain/models/job.py`
   - Implement `JobStatus` enum with states from existing code (PENDING, PROCESSING, COMPLETED, FAILED)
   - Implement `VideoJob` class with:
     - `id`: unique job identifier
     - `video`: reference to Video entity
     - `metadata`: reference to VideoMetadata entity
     - `status`: JobStatus enum
     - `created_at`: job creation time
     - `updated_at`: last update time
     - `error`: error message (if any)
   - Add methods currently in `video_processor/core/models/video_job.py` (lines ~50-100)
   - Success criteria: Class can replace functionality of existing VideoJob

4. **Create domain exceptions** ✅
   - Create `video_processor/domain/exceptions.py`
   - Define these exception classes:
     - `VideoProcessingError`: base exception for all domain errors
     - `InvalidVideoError`: for invalid video files
     - `MetadataGenerationError`: for AI metadata generation failures
     - `PublishingError`: for YouTube publishing failures
     - `StorageError`: for file storage/retrieval errors
   - Success criteria: Exceptions can be raised and caught in tests

5. **Implement value objects** ✅
   - Create `video_processor/domain/value_objects.py`
   - Implement these immutable value objects:
     - `VideoResolution(width: int, height: int)`
     - `VideoFormat(name: str, codec: str)`
     - `TimestampedText(text: str, start_time: float, end_time: float)` for subtitles
   - Success criteria: Value objects can be instantiated and compared for equality

### Task 1.3: Application Service Interfaces

1. **Define storage interface** ✅
   - Create `video_processor/application/interfaces/storage.py`
   - Implement `StorageInterface` abstract base class with these methods:
     - `upload_file(file_path: str, destination_path: str) -> str`
     - `download_file(source_path: str, destination_path: str) -> str`
     - `delete_file(path: str) -> bool`
     - `get_public_url(path: str) -> str`
     - `get_signed_url(path: str, expiration_seconds: int) -> str`
   - Add type hints and docstrings to all methods
   - Success criteria: Abstract class can be imported and subclassed

2. **Define AI service interface** ✅
   - Create `video_processor/application/interfaces/ai.py`
   - Implement `AIServiceInterface` with these methods:
     - `generate_transcript(audio_file: str) -> str`
     - `generate_metadata(transcript: str) -> dict`
     - `generate_thumbnail_description(transcript: str, timestamp: float) -> str`
     - `summarize_content(transcript: str, max_length: int) -> str`
   - Add method to handle different models:
     - `set_model(model_name: str) -> None`
   - Success criteria: Abstract class can be imported and subclassed

3. **Define publishing interface** ✅
   - Create `video_processor/application/interfaces/publishing.py`
   - Implement `PublishingInterface` with these methods:
     - `upload_video(video_file: str, metadata: dict) -> str`
     - `update_metadata(video_id: str, metadata: dict) -> bool`
     - `get_upload_status(video_id: str) -> str`
     - `delete_video(video_id: str) -> bool`
   - Success criteria: Abstract class can be imported and subclassed

4. **Create data transfer objects** ✅
   - Create `video_processor/application/dtos/video_dto.py`
   - Implement `VideoDTO` with fields matching Video entity
   - Create `video_processor/application/dtos/metadata_dto.py`
   - Implement `MetadataDTO` with fields matching VideoMetadata
   - Create `video_processor/application/dtos/job_dto.py`
   - Implement `JobDTO` with fields matching VideoJob
   - Add conversion methods between DTOs and domain entities
   - Success criteria: DTOs can be serialized to/from JSON

## Phase 2: Service Implementation

### Task 2.1: Storage Adapter Implementation

1. **Extract Google Cloud Storage client** ✅
   - Create `video_processor/adapters/storage/gcs.py`
   - Copy the GCS client initialization from `process_uploaded_video.py` (around line 30)
   - Implement `GCSStorageAdapter` class implementing `StorageInterface`
   - Success criteria: Class instantiation with GCS credentials works

2. **Implement file upload method** ✅
   - In `GCSStorageAdapter`, implement `upload_file()` method
   - Refactor the logic from `write_blob()` in `process_uploaded_video.py` (line ~273)
   - Add proper error handling and retries (3 attempts with exponential backoff)
   - Success criteria: Method successfully uploads test file to GCS

3. **Implement file download method** ✅
   - In `GCSStorageAdapter`, implement `download_file()` method
   - Use Google Cloud Storage client's `download_to_filename` method
   - Add proper error handling and retries
   - Success criteria: Method successfully downloads test file from GCS

4. **Implement file movement and deletion** ✅
   - In `GCSStorageAdapter`, implement `delete_file()` method
   - Refactor the logic from `move_processed_file()` in `process_uploaded_video.py` (line ~412)
   - Add proper error handling
   - Success criteria: Methods correctly manipulate files in GCS

5. **Implement URL generation methods** ✅
   - In `GCSStorageAdapter`, implement:
     - `get_public_url()` method using GCS public URL format
     - `get_signed_url()` method using GCS signed URL generation
   - Success criteria: Generated URLs can access files in GCS

6. **Create local storage adapter** ✅
   - Create `video_processor/adapters/storage/local.py`
   - Implement `LocalStorageAdapter` implementing `StorageInterface`
   - Use Python's `shutil` for local file operations
   - Use the existing `LOCAL_OUTPUT` logic from `process_uploaded_video.py`
   - Success criteria: Adapter works with local filesystem paths

### Task 2.2: AI Service Adapters

1. **Create Gemini adapter skeleton** ✅
   - Create `video_processor/adapters/ai/gemini.py`
   - Implement `GeminiAIAdapter` class implementing `AIServiceInterface`
   - Copy the model initialization code from `process_uploaded_video.py` (around line 40)
   - Add configuration for API key and model selection
   - Success criteria: Class can be instantiated with API credentials

2. **Implement transcript generation** ✅
   - In `GeminiAIAdapter`, implement `generate_transcript()` method
   - Refactor the logic from existing transcript generation code
   - Add retry mechanism (3 attempts with exponential backoff)
   - Handle API rate limiting with appropriate waits
   - Success criteria: Method generates transcript from sample audio

3. **Implement metadata generation** ✅
   - In `GeminiAIAdapter`, implement `generate_metadata()` method
   - Refactor logic from methods like:
     - `generate_shownotes()` (line ~100)
     - `generate_titles()` (line ~140)
     - `generate_tags()` (line ~160)
   - Add structured output validation
   - Success criteria: Method generates valid metadata from sample transcript

4. **Implement thumbnail description** ✅
   - In `GeminiAIAdapter`, implement `generate_thumbnail_description()` method
   - Refactor from `generate_thumbnail_description()` in existing code
   - Success criteria: Method produces relevant thumbnail description 

5. **Create Vertex AI adapter** ✅
   - Create `video_processor/adapters/ai/vertex_ai.py`
   - Implement `VertexAIAdapter` implementing `AIServiceInterface`
   - Configure Vertex AI client
   - Implement all required methods using Vertex AI API
   - Success criteria: Adapter can connect to Vertex AI and make requests

### Task 2.3: Video Processing Services

1. **Create video processor service** ✅
   - Create `video_processor/application/services/video_processor.py`
   - Implement `VideoProcessorService` class
   - Inject required dependencies (storage, AI, etc.) via constructor
   - Success criteria: Service can be instantiated with dependencies

2. **Implement main processing method**
   - In `VideoProcessorService`, implement `process_video(job_id: str) -> VideoJob`
   - Refactor the logic from `process_video_event()` (line ~648) in `process_uploaded_video.py`
   - Break down into smaller private methods for each processing step
   - Success criteria: Method orchestrates the complete video processing flow

3. **Create transcription service** ✅
   - Create `video_processor/application/services/transcription.py`
   - Implement `TranscriptionService` class
   - Refactor from `generate_transcript()` (line ~58) in `process_uploaded_video.py`
   - Add method to extract audio from video using FFmpeg
   - Success criteria: Service generates transcript from video file

4. **Create subtitle service** ✅
   - Create `video_processor/application/services/subtitle.py`
   - Implement `SubtitleService` class
   - Refactor from `generate_vtt()` (line ~79) in `process_uploaded_video.py`
   - Add methods for different subtitle formats (VTT, SRT)
   - Success criteria: Service generates valid subtitle files from transcript

5. **Create metadata service** ✅
   - Create `video_processor/application/services/metadata.py`
   - Implement `MetadataService` class
   - Include methods for each metadata component:
     - `generate_title(transcript: str) -> str`
     - `generate_description(transcript: str) -> str`
     - `generate_tags(transcript: str) -> List[str]`
     - `generate_thumbnail(video_path: str, transcript: str) -> str`
   - Success criteria: Service generates all metadata components

### Task 2.4: YouTube Publishing Adapter

1. **Extract YouTube client**
   - Create `video_processor/adapters/publishing/youtube.py`
   - Implement `YouTubeAdapter` class implementing `PublishingInterface`
   - Refactor YouTube client initialization from `video_processor/youtube_uploader.py`
   - Success criteria: Adapter can authenticate with YouTube API

2. **Implement video upload**
   - In `YouTubeAdapter`, implement `upload_video()` method
   - Refactor from the upload logic in `video_processor/youtube_uploader.py`
   - Add proper progress tracking and error handling
   - Success criteria: Method uploads video with metadata to YouTube

3. **Implement metadata update**
   - In `YouTubeAdapter`, implement `update_metadata()` method
   - Use YouTube API's videos.update method
   - Handle all required metadata fields
   - Success criteria: Method updates title, description, tags, etc.

4. **Implement token refresh utility**
   - Create `video_processor/utils/youtube_auth.py`
   - Refactor from `video_processor/generate_youtube_token.py`
   - Add automatic token refresh logic
   - Success criteria: Authentication tokens refresh automatically when expired

5. **Implement status and deletion methods**
   - In `YouTubeAdapter`, implement:
     - `get_upload_status()` method
     - `delete_video()` method
   - Add proper error handling
   - Success criteria: Methods correctly interact with YouTube API

## Phase 3: Infrastructure

### Task 3.1: Dependency Injection Setup

1. **Create settings module** ✅
   - Create `video_processor/infrastructure/config/settings.py`
   - Define configuration classes for:
     - `StorageSettings`
     - `AISettings`
     - `YouTubeSettings`
     - `APISettings`
   - Load settings from environment variables
   - Success criteria: Settings successfully loaded from .env file

2. **Create container module** ✅
   - Create `video_processor/infrastructure/config/container.py`
   - Implement `Container` class using a dependency injection library (e.g., Python-Injector)
   - Define provider methods for all services
   - Success criteria: Container resolves dependencies correctly

3. **Implement service provider registry** ✅
   - In the container module, add a registry for dynamic service selection
   - Allow runtime switching between service implementations
   - Success criteria: Services can be switched at runtime (e.g., between GCS and local storage)

### Task 3.2: Repository Implementation

1. **Create job repository interface**
   - Create `video_processor/application/interfaces/repositories.py`
   - Define `JobRepositoryInterface` with CRUD methods
   - Success criteria: Interface defines all needed operations

2. **Implement job repository**
   - Create `video_processor/infrastructure/repositories/job_repository.py`
   - Implement `FirestoreJobRepository` class
   - Refactor from Firestore operations in `video_processor/firestore_trigger_listener.py`
   - Success criteria: Repository performs CRUD operations on jobs

3. **Implement video repository**
   - Create `video_processor/infrastructure/repositories/video_repository.py`
   - Implement `VideoRepository` class
   - Add methods for video metadata storage and retrieval
   - Success criteria: Repository manages video data correctly

### Task 3.3: FastAPI Server Implementation

1. **Set up FastAPI application**
   - Create `video_processor/infrastructure/api/server.py`
   - Implement the FastAPI app setup:
     ```python
     from fastapi import FastAPI
     
     app = FastAPI(
         title="Video Processor API",
         description="API for video processing pipeline",
         version="1.0.0"
     )
     
     # Include routers here
     ```
   - Add middleware configuration
   - Success criteria: FastAPI app starts without errors

2. **Create API schemas**
   - Create `video_processor/infrastructure/api/schemas/video.py`
   - Refactor schemas from `video_processor/api/schemas.py`
   - Use Pydantic models for:
     - `VideoRequest`
     - `VideoResponse`
     - `JobStatusResponse`
   - Success criteria: Schemas validate test data correctly

3. **Implement video routes**
   - Create `video_processor/infrastructure/api/routes/videos.py`
   - Implement a FastAPI router:
     ```python
     from fastapi import APIRouter, Depends
     
     router = APIRouter(prefix="/videos", tags=["videos"])
     
     # Define routes here
     ```
   - Refactor endpoints from `video_processor/api/routes.py`
   - Success criteria: Routes handle requests correctly

4. **Implement health check**
   - Create `video_processor/infrastructure/api/routes/health.py`
   - Implement health check endpoints:
     - `GET /health` - basic health check
     - `GET /health/detailed` - service status check
   - Success criteria: Endpoints return correct health status

5. **Set up API dependencies**
   - Create `video_processor/infrastructure/api/dependencies.py`
   - Implement dependency functions for route handlers:
     - `get_video_processor() -> VideoProcessorService`
     - `get_job_repository() -> JobRepositoryInterface`
   - Success criteria: Dependencies are correctly injected into routes

### Task 3.4: Message Handling

1. **Create message handling interfaces**
   - Create `video_processor/application/interfaces/messaging.py`
   - Define `MessageHandlerInterface` with:
     - `publish(topic: str, message: dict) -> str`
     - `subscribe(topic: str, callback: Callable) -> None`
   - Success criteria: Interface can be implemented by adapters

2. **Implement Pub/Sub adapter**
   - Create `video_processor/infrastructure/messaging/pubsub.py`
   - Implement `PubSubAdapter` class
   - Add connection management and error handling
   - Success criteria: Adapter publishes and subscribes to test topics

3. **Create event handlers**
   - Create `video_processor/infrastructure/messaging/handlers.py`
   - Implement handler functions for:
     - `handle_video_uploaded(message: dict) -> None`
     - `handle_processing_complete(message: dict) -> None`
   - Success criteria: Handlers process messages correctly

## Phase 4: Testing

### Task 4.1: Test Infrastructure

1. **Set up test configuration**
   - Create `tests/conftest.py`
   - Refactor from `video_processor/conftest.py`
   - Add fixture functions for:
     - `storage_adapter()` - mock storage adapter
     - `ai_adapter()` - mock AI adapter
     - `publishing_adapter()` - mock YouTube adapter
     - `test_video()` - sample video file
     - `test_job()` - sample job data
   - Success criteria: Fixtures can be used in tests

2. **Create mock implementations**
   - Create `tests/mocks/storage.py`
   - Implement `MockStorageAdapter`
   - Create `tests/mocks/ai.py`
   - Implement `MockAIAdapter`
   - Create `tests/mocks/publishing.py`
   - Implement `MockPublishingAdapter`
   - Success criteria: Mocks can be used in place of real adapters

### Task 4.2: Unit Tests

1. **Add domain model tests**
   - Create `tests/unit/domain/test_video.py`
   - Test `Video` class methods and properties
   - Create `tests/unit/domain/test_metadata.py`
   - Test `VideoMetadata` class
   - Create `tests/unit/domain/test_job.py`
   - Test `VideoJob` class
   - Success criteria: All tests pass with good coverage

2. **Add service tests**
   - Create `tests/unit/application/services/test_video_processor.py`
   - Test `VideoProcessorService` with mocked dependencies
   - Add tests for other services
   - Success criteria: All services tested with >80% coverage

3. **Add adapter tests**
   - Create `tests/unit/adapters/storage/test_gcs.py`
   - Test `GCSStorageAdapter` with mocked GCS client
   - Add tests for other adapters
   - Success criteria: All adapter methods tested

### Task 4.3: Integration Tests

1. **Add API integration tests**
   - Create `tests/integration/api/test_videos.py`
   - Test video endpoints with TestClient
   - Success criteria: API responds correctly to test requests

2. **Add storage integration tests**
   - Create `tests/integration/storage/test_gcs.py`
   - Test against real GCS (with test bucket)
   - Success criteria: Storage operations work end-to-end

3. **Add AI integration tests**
   - Create `tests/integration/ai/test_gemini.py`
   - Test against real Gemini API (with API key)
   - Success criteria: AI operations generate valid results

### Task 4.4: End-to-End Tests

1. **Create video processing test**
   - Create `tests/e2e/test_video_processing.py`
   - Test complete flow with sample video
   - Success criteria: Video processes end-to-end

2. **Add deployment verification test**
   - Create `tests/e2e/test_deployment.py`
   - Test deployed service health check
   - Success criteria: Deployed service responds correctly

## Phase 5: Deployment & Utilities

### Task 5.1: Deployment Configuration

1. **Update Dockerfile**
   - Edit `Dockerfile` to use new structure
   - Use multi-stage build for smaller image
   - Success criteria: Docker image builds successfully

2. **Configure Cloud Run deployment**
   - Create `cloudbuild.yaml` for CI/CD
   - Define service account and permissions
   - Success criteria: Deployment script works in test environment

### Task 5.2: Utility Functions

1. **Create FFmpeg wrapper**
   - Create `video_processor/utils/ffmpeg.py`
   - Refactor from `video_processor/core/processors/audio.py`
   - Implement functions for:
     - `extract_audio(video_path: str, output_path: str) -> str`
     - `extract_frame(video_path: str, time: float, output_path: str) -> str`
     - `get_video_metadata(video_path: str) -> dict`
   - Success criteria: Functions perform media operations correctly

2. **Set up logging configuration**
   - Create `video_processor/utils/logging.py`
   - Implement structured logging setup
   - Add custom formatters for different environments
   - Success criteria: Logging works in all environments

3. **Create profiling tools**
   - Create `video_processor/utils/profiling.py`
   - Implement performance monitoring decorators
   - Add utilities for timing operations
   - Success criteria: Tools provide useful performance data

### Task 5.3: Documentation

1. **Update README.md**
   - Update with new architecture details
   - Add setup and usage instructions
   - Success criteria: README provides clear guidance

2. **Create API documentation**
   - Set up Swagger UI via FastAPI
   - Add detailed endpoint descriptions
   - Success criteria: API can be explored via Swagger UI

3. **Add developer guides**
   - Create component guides in `docs/`
   - Add diagrams explaining the architecture
   - Success criteria: Guides help new developers understand the system

## Phase 6: Refinement & Optimization

### Task 6.1: Performance Optimization

1. **Create benchmarking script**
   - Create `scripts/benchmark.py`
   - Add timing for all processing stages
   - Success criteria: Script identifies bottlenecks

2. **Optimize AI service usage**
   - Implement caching for AI responses
   - Use parallel processing where possible
   - Success criteria: Processing time decreases by >20%

### Task 6.2: Error Handling & Resilience

1. **Implement comprehensive error handling**
   - Add try/except blocks around all external calls
   - Implement proper fallback mechanisms
   - Success criteria: System recovers from common failure modes

2. **Set up monitoring**
   - Create `video_processor/infrastructure/monitoring.py`
   - Implement metrics collection
   - Success criteria: Key metrics are tracked

### Task 6.3: Security Review

1. **Conduct security audit**
   - Review authentication mechanisms
   - Check for secure credential handling
   - Success criteria: No critical security issues found

2. **Implement authentication & authorization**
   - Create `video_processor/infrastructure/api/auth.py`
   - Implement JWT-based authentication
   - Define role-based permissions (admin, user)
   - Add authentication middleware to FastAPI app
   - Create login/token endpoints
   - Add API key authentication for service-to-service communication
   - Success criteria: Protected endpoints require valid authentication

3. **Implement secure storage for API keys**
   - Use Secret Manager for sensitive credentials
   - Success criteria: No credentials in code or config files

## Migration Strategy Steps

1. **Setup parallel environment**
   - Create new directory structure alongside existing code
   - Set up CI/CD for the new codebase
   - Success criteria: Both versions can run independently

2. **Create migration test suite**
   - Implement tests that verify equivalent output between old and new code
   - Create validation script that compares results
   - Success criteria: Tests verify functional equivalence

3. **Migrate one component at a time**
   - Start with storage adapter
   - Then implement core services
   - Finally migrate API endpoints
   - Success criteria: Components work in isolation

4. **Perform canary deployment**
   - Route small percentage of traffic to new implementation
   - Monitor errors and performance
   - Gradually increase traffic
   - Success criteria: New implementation handles production traffic

5. **Complete cutover**
   - Switch all traffic to new implementation
   - Keep old code available for quick rollback
   - Success criteria: System functions in production with new code

6. **Clean up legacy code**
   - After 2 weeks of stable operation, remove old code
   - Success criteria: Codebase is clean and maintained in new structure only 