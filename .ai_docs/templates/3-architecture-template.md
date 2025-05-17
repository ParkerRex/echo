--- 
> This is a template of the expected output when generating an architecture document

Be sure to read the following files to understand the context of the project:

`pitch.md`
`prd.md`
`architecture.md`
`system-patterns.md`

## Run the following command

eza . --tree --git-ignore

# Pass in the files you want included in the tree.
> Read the files below and nothing else.

{apps/web/}
{supabase/}



---




# File Structure Comparison: Current vs. Proposed

## Current Backend Structure

The current backend follows a partially modular architecture but has significant monolithic components:

```
backend/
├── video_processor/                           # Main application module
│   ├── core/                                  # Core application logic
│   │   ├── models/                            # Domain models
│   │   │   ├── __init__.py                    # (8 lines) Module exports
│   │   │   └── video_job.py                   # (167 lines) VideoJob and ProcessingStage models
│   │   ├── processors/                        # Processing components
│   │   │   ├── __init__.py                    # (16 lines) Module exports
│   │   │   ├── audio.py                       # (196 lines) Audio extraction and processing
│   │   │   ├── chapters.py                    # (154 lines) Chapter generation
│   │   │   ├── transcript.py                  # (132 lines) Transcript generation
│   │   │   └── video.py                       # (252 lines) Video processing
│   │   └── __init__.py                        # (4 lines) Module exports
│   ├── services/                              # External service integrations
│   │   ├── ai/                                # AI service integrations
│   │   ├── storage/                           # Cloud storage services
│   │   ├── youtube/                           # YouTube API integration
│   │   └── __init__.py                        # (4 lines) Module exports
│   ├── api/                                   # API definitions
│   │   ├── __init__.py                        # (8 lines) Module exports
│   │   ├── controllers.py                     # (139 lines) Request handlers
│   │   ├── routes.py                          # (99 lines) API route definitions
│   │   └── schemas.py                         # (64 lines) API data schemas
│   ├── utils/                                 # Utility functions
│   ├── config/                                # Configuration management
│   ├── tests/                                 # Test directory (nested)
│   ├── __init__.py                            # (2 lines) Package initialization
│   ├── process_uploaded_video.py              # (711 lines) Main processing logic (monolithic)
│   ├── youtube_uploader.py                    # (535 lines) YouTube uploading functionality
│   ├── generate_youtube_token.py              # (151 lines) Token generation for YouTube API
│   ├── firestore_trigger_listener.py          # (69 lines) Firestore event processing
│   ├── setup_youtube_secrets.py               # (205 lines) YouTube credential setup
│   ├── app.py                                 # (27 lines) Flask application entry point
│   ├── main.py                                # (103 lines) Entry point for cloud functions
│   ├── test_process_video.py                  # (72 lines) Tests for video processing
│   ├── test_audio_processing.py               # (95 lines) Tests for audio processing
│   ├── conftest.py                            # (59 lines) Pytest fixtures
│   ├── pytest.ini                             # (11 lines) Pytest configuration
│   ├── setup.py                               # (22 lines) Package setup
│   ├── README.md                              # (190 lines) Module documentation
│   ├── youtube_uploader_README.md             # (114 lines) YouTube uploader documentation
│   └── .gcloudignore                          # (9 lines) GCP deployment ignore patterns
├── tests/                                     # Test suite (root level)
│   ├── unit/                                  # Unit tests
│   ├── integration/                           # Integration tests
│   └── e2e/                                   # End-to-end tests
├── scripts/                                   # Utility scripts
├── docs/                                      # Documentation
├── requirements.txt                           # (31 lines) Dependencies
├── Dockerfile                                 # (27 lines) Container definition
├── Dockerfile.mock                            # (19 lines) Mock container for testing
└── deploy.sh                                  # (268 lines) Deployment script
```

## Key Issues with Current Structure

1. **Monolithic Files:**
   - `process_uploaded_video.py` (711 lines) handles multiple concerns:
     - Video and audio processing
     - AI content generation
     - Cloud storage management
     - Process orchestration
   - `youtube_uploader.py` (535 lines) combines too many YouTube API operations

2. **Mixed Responsibilities:**
   - Tests are split between the module-level and project-level directories
   - Configuration is spread across multiple files
   - No clear separation between domain logic and infrastructure

3. **Limited Modularity:**
   - Difficult to replace components with alternative implementations
   - Testing requires many mock objects
   - Heavy coupling between processing stages

## Proposed Backend Structure

The proposed architecture follows clean architecture principles with well-defined layers:

```
backend/
├── video_processor/                           # Main package
│   ├── domain/                                # Domain models and business logic
│   │   ├── models/                            # Domain entities
│   │   │   ├── __init__.py                    # Package initialization
│   │   │   ├── video.py                       # Video entity
│   │   │   ├── job.py                         # Processing job entity (from video_job.py)
│   │   │   └── metadata.py                    # Video metadata entity (from video_job.py)
│   │   ├── __init__.py                        # Package initialization
│   │   ├── exceptions.py                      # Domain-specific exceptions
│   │   └── value_objects.py                   # Value objects for domain
│   ├── application/                           # Application services and use cases
│   │   ├── services/                          # Application services
│   │   │   ├── __init__.py                    # Package initialization 
│   │   │   ├── video_processor.py             # Video processing orchestration (from process_uploaded_video.py)
│   │   │   ├── transcription.py               # Transcript generation service (from generate_transcript())
│   │   │   ├── subtitle.py                    # Subtitle generation service (from generate_vtt())
│   │   │   └── metadata.py                    # Metadata generation service (from existing generators)
│   │   ├── interfaces/                        # Service interfaces
│   │   │   ├── __init__.py                    # Package initialization
│   │   │   ├── storage.py                     # Storage service interface
│   │   │   ├── ai.py                          # AI service interface
│   │   │   └── publishing.py                  # Publishing service interface
│   │   ├── __init__.py                        # Package initialization
│   │   └── dtos/                              # Data Transfer Objects
│   │       ├── __init__.py                    # Package initialization
│   │       └── video_job_dto.py               # DTOs for API communication
│   ├── adapters/                              # External service adapters
│   │   ├── ai/                                # AI service adapters
│   │   │   ├── __init__.py                    # Package initialization
│   │   │   ├── vertex_ai.py                   # Vertex AI implementation 
│   │   │   └── gemini.py                      # Gemini API implementation (from process_uploaded_video.py)
│   │   ├── storage/                           # Storage adapters
│   │   │   ├── __init__.py                    # Package initialization
│   │   │   ├── gcs.py                         # Google Cloud Storage implementation (from process_uploaded_video.py)
│   │   │   └── local.py                       # Local filesystem implementation
│   │   ├── __init__.py                        # Package initialization
│   │   └── publishing/                        # Publishing adapters
│   │       ├── __init__.py                    # Package initialization
│   │       └── youtube.py                     # YouTube API implementation (from youtube_uploader.py)
│   ├── infrastructure/                        # Framework-specific code
│   │   ├── config/                            # Configuration management
│   │   │   ├── __init__.py                    # Package initialization
│   │   │   ├── settings.py                    # Application settings
│   │   │   └── container.py                   # Dependency injection container
│   │   ├── api/                               # API framework implementation
│   │   │   ├── __init__.py                    # Package initialization
│   │   │   ├── server.py                      # FastAPI server definition (replacing Flask app.py)
│   │   │   ├── routes/                        # API route handlers
│   │   │   │   ├── __init__.py                # Package initialization
│   │   │   │   ├── videos.py                  # Video-related endpoints (from api/routes.py)
│   │   │   │   └── health.py                  # Health and status endpoints
│   │   │   ├── schemas/                       # API schemas using Pydantic
│   │   │   │   ├── __init__.py                # Package initialization
│   │   │   │   └── video.py                   # Video-related schemas (from api/schemas.py)
│   │   │   └── dependencies.py                # FastAPI dependencies
│   │   ├── repositories/                      # Data repositories
│   │   │   ├── __init__.py                    # Package initialization
│   │   │   ├── job_repository.py              # Job persistence
│   │   │   └── video_repository.py            # Video metadata persistence
│   │   ├── __init__.py                        # Package initialization
│   │   └── messaging/                         # Messaging infrastructure
│   │       ├── __init__.py                    # Package initialization
│   │       └── pubsub.py                      # Google Pub/Sub integration
│   ├── utils/                                 # Utility functions and helpers
│   │   ├── __init__.py                        # Package initialization
│   │   ├── logging.py                         # Logging configuration
│   │   ├── ffmpeg.py                          # FFmpeg wrapper (from core/processors/audio.py)
│   │   └── profiling.py                       # Performance profiling tools
│   ├── __init__.py                            # Package initialization
│   └── main.py                                # Application entry point (from main.py)
├── tests/                                     # Test suite
│   ├── unit/                                  # Unit tests
│   │   ├── domain/                            # Tests for domain models
│   │   ├── application/                       # Tests for application services 
│   │   └── adapters/                          # Tests for adapters
│   ├── integration/                           # Integration tests
│   │   ├── api/                               # API integration tests
│   │   ├── storage/                           # Storage integration tests
│   │   └── ai/                                # AI services integration tests
│   ├── e2e/                                   # End-to-end tests
│   └── conftest.py                            # Test fixtures (from video_processor/conftest.py)
├── scripts/                                   # Utility scripts for development/deployment
│   ├── deploy.sh                              # Deployment script (improved from root deploy.sh)
│   └── generate_youtube_token.py              # Token generation script (from video_processor)
├── docs/                                      # Documentation
│   ├── be-prd.txt                             # Product Requirements Document
│   └── file-structure-comparison.md           # This file
├── requirements.txt                           # Dependencies
├── Dockerfile                                 # Container definition
├── pyproject.toml                             # Project configuration (replacing setup.py)
└── README.md                                  # Project documentation
```

## Key Benefits of Proposed Structure

1. **Clean Architecture:**
   - Clear separation of concerns between layers
   - Domain logic isolated from infrastructure details
   - Easier to reason about and maintain

2. **Improved Testability:**
   - Domain logic is free from external dependencies
   - Interfaces allow easy mocking of external services
   - Dedicated test directory structure aligns with application structure

3. **Enhanced Modularity:**
   - Dependency injection enables swapping implementations
   - Adapters isolate external service interactions
   - Repository pattern separates persistence concerns

4. **Better Maintainability:**
   - Smaller, focused files with single responsibilities
   - Clear boundaries between application components
   - Standardized structure that's easier to navigate

5. **Scalability:**
   - New features can be added without affecting existing components
   - Processing stages can be evolved independently
   - Multiple developers can work on different areas simultaneously 