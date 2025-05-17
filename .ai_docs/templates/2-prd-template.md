---
> The purpose of this file is to show an example of the PRD we want to generate for a given pitch.
---

# VIDEO PROCESSING PIPELINE - PRODUCT REQUIREMENTS DOCUMENT

## 1. Overview

This Product Requirements Document (PRD) outlines the specifications for developing a modern, scalable video processing pipeline system that automates the conversion of raw video content into publishable assets complete with AI-generated metadata. The system utilizes Google Cloud Platform services, particularly Cloud Run and Vertex AI, to process videos, extract audio, and generate high-quality transcripts, subtitles, chapters, titles, and other metadata to streamline the content publishing workflow.

## 2. Project goals

### 2.1 Primary goals

- Create a scalable, modular backend architecture for processing video files
- Implement AI-powered content generation for video metadata
- Develop a flexible system that supports multiple content channels and platforms
- Establish a maintainable codebase with modern Python design patterns
- Provide a robust API for frontend integration
- Enable automated deployment to Google Cloud Platform

### 2.2 Success metrics

- Processing time < 10 minutes for videos up to 30 minutes in length
- 95% accuracy in AI-generated transcripts (compared to manual transcription)
- 99.5% system availability
- 100% of videos successfully processed with complete metadata
- < 5% error rate in automated metadata generation
- Ability to process at least 50 concurrent video jobs

## 3. Current architecture

The project currently follows a partially modular architecture with several key components already implemented:

```
backend/
├── video_processor/               # Main application module
│   ├── core/                      # Core application logic
│   │   ├── models/                # Domain models
│   │   │   └── video_job.py       # VideoJob and ProcessingStage models
│   │   └── processors/            # Processing components
│   │       ├── audio.py           # Audio extraction and processing
│   │       ├── chapters.py        # Chapter generation
│   │       ├── transcript.py      # Transcript generation
│   │       └── video.py           # Video processing
│   ├── services/                  # External service integrations
│   │   ├── ai/                    # AI service integrations
│   │   ├── storage/               # Cloud storage services
│   │   └── youtube/               # YouTube API integration
│   ├── api/                       # API definitions
│   │   ├── controllers.py         # Request handlers
│   │   ├── routes.py              # API route definitions
│   │   └── schemas.py             # API data schemas
│   ├── utils/                     # Utility functions
│   ├── config/                    # Configuration management
│   ├── process_uploaded_video.py  # Main processing logic (monolithic)
│   ├── youtube_uploader.py        # YouTube uploading functionality
│   └── main.py                    # Entry point for cloud functions
```

The current implementation primarily uses a monolithic approach in `process_uploaded_video.py` (711 lines), which handles multiple responsibilities:
- Video and audio processing (`extract_audio()` function)
- AI content generation (`generate_transcript()`, `generate_vtt()`, etc.)
- GCS bucket management (`write_blob()`, `move_processed_file()`)
- Process orchestration (`process_video_event()`)

This monolithic approach lacks clear separation of concerns, making it difficult to maintain, test, and extend the codebase.

## 4. Proposed architecture

We propose refactoring the existing codebase to follow a more modern Python architecture using a proper hexagonal/clean architecture approach:

```
backend/
├── video_processor/
│   ├── domain/                      # Domain models and business logic
│   │   ├── models/                  # Domain entities
│   │   │   ├── video.py             # Video entity
│   │   │   ├── job.py               # Processing job entity
│   │   │   └── metadata.py          # Video metadata entity
│   │   ├── exceptions.py            # Domain-specific exceptions
│   │   └── value_objects.py         # Value objects for domain
│   ├── application/                 # Application services and use cases
│   │   ├── services/                # Application services
│   │   │   ├── video_processor.py   # Video processing orchestration
│   │   │   ├── transcription.py     # Transcript generation service
│   │   │   ├── subtitle.py          # Subtitle generation service
│   │   │   └── metadata.py          # Metadata generation service
│   │   ├── interfaces/              # Service interfaces
│   │   │   ├── storage.py           # Storage service interface
│   │   │   ├── ai.py                # AI service interface
│   │   │   └── publishing.py        # Publishing service interface
│   │   └── dtos/                    # Data Transfer Objects
│   │       └── video_job_dto.py     # DTOs for API communication
│   ├── adapters/                    # External service adapters
│   │   ├── ai/                      # AI service adapters
│   │   │   ├── vertex_ai.py         # Vertex AI implementation
│   │   │   └── gemini.py            # Gemini API implementation
│   │   ├── storage/                 # Storage adapters
│   │   │   ├── gcs.py               # Google Cloud Storage implementation
│   │   │   └── local.py             # Local filesystem implementation
│   │   └── publishing/              # Publishing adapters
│   │       └── youtube.py           # YouTube API implementation
│   ├── infrastructure/              # Framework-specific code
│   │   ├── config/                  # Configuration management
│   │   │   ├── settings.py          # Application settings
│   │   │   └── container.py         # Dependency injection container
│   │   ├── api/                     # API framework implementation
│   │   │   ├── server.py            # FastAPI server definition
│   │   │   ├── routes/              # API route handlers
│   │   │   │   ├── videos.py        # Video-related endpoints
│   │   │   │   └── health.py        # Health and status endpoints
│   │   │   ├── schemas/             # API schemas using Pydantic
│   │   │   │   └── video.py         # Video-related schemas
│   │   │   └── dependencies.py      # FastAPI dependencies
│   │   ├── repositories/            # Data repositories
│   │   │   ├── job_repository.py    # Job persistence
│   │   │   └── video_repository.py  # Video metadata persistence
│   │   └── messaging/               # Messaging infrastructure
│   │       └── pubsub.py            # Google Pub/Sub integration
│   ├── utils/                       # Utility functions and helpers
│   │   ├── logging.py               # Logging configuration
│   │   ├── ffmpeg.py                # FFmpeg wrapper (from current audio.py)
│   │   └── profiling.py             # Performance profiling tools
│   └── main.py                      # Application entry point
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── e2e/                         # End-to-end tests
└── scripts/                         # Utility scripts for development/deployment
```

## 5. Key features & requirements

### 5.1 Video processing pipeline

**REQ-VP-001: Video upload and storage**
- System must accept video uploads from GCS bucket triggers
- Reuse existing `bucket_name` and `file_name` handling from `process_uploaded_video.py`
- Refactor `should_process_file()` and `setup_output_paths()` into domain services

**REQ-VP-002: Audio extraction**
- Extract audio from video files for AI analysis
- Maintain existing functionality from `extract_audio()` in `process_uploaded_video.py`
- Refactor to follow adapter pattern in `utils/ffmpeg.py`

**REQ-VP-003: Transcript generation**
- Generate high-quality transcripts from audio
- Migrate logic from `generate_transcript()` to dedicated service
- Implement as adapter in `adapters/ai/gemini.py`

**REQ-VP-004: Subtitle generation**
- Create WebVTT format subtitles for videos
- Migrate logic from `generate_vtt()` to dedicated service
- Implement in `application/services/subtitle.py`

**REQ-VP-005: Content summarization**
- Generate show notes based on video content
- Migrate logic from `generate_shownotes()` to dedicated service
- Use dependency injection to allow different AI providers

**REQ-VP-006: Chapter generation**
- Create timestamped chapters for video content
- Migrate logic from `generate_chapters()` to dedicated service
- Use existing domain model structure from `core/processors/chapters.py`

**REQ-VP-007: Title suggestion**
- Generate optimized title variations for video
- Migrate logic from `generate_titles()` to dedicated service
- Implement in `application/services/metadata.py`

**REQ-VP-008: YouTube integration**
- Support publishing processed videos to YouTube
- Maintain functionality from `youtube_uploader.py`
- Refactor to adapter pattern in `adapters/publishing/youtube.py`

**REQ-VP-009: Processing job management**
- Track status of video processing through workflow
- Expand current `VideoJob` model from `core/models/video_job.py`
- Implement repository pattern for job persistence

### 5.2 API requirements

**REQ-API-001: Video processing API**
- API endpoint for triggering video processing
- Refactor existing API implementation in `api/routes.py` and `api/controllers.py`
- Migrate to FastAPI framework in `infrastructure/api/server.py`

**REQ-API-002: Job status API**
- Endpoint for checking video processing status
- Create new endpoint based on current job tracking
- Implement in `infrastructure/api/routes/videos.py`

**REQ-API-003: API documentation**
- OpenAPI documentation for all endpoints
- Automatic generation via FastAPI
- Example requests and responses

**REQ-API-004: Authentication & authorization**
- Secure API endpoints with authentication
- Token-based authentication for frontend access
- Role-based access control for administrative functions

**REQ-API-005: Health check endpoints**
- Service health monitoring endpoints
- Connectivity checks for dependent services
- Version information endpoint

### 5.3 Technical requirements

**REQ-TECH-001: Clean architecture**
- Refactor existing code following clean architecture principles
- Separate domain logic from infrastructure concerns
- Implement proper dependency injection

**REQ-TECH-002: Testing strategy**
- Comprehensive unit test coverage for domain and application layers
- Integration tests for adapters and infrastructure
- End-to-end tests for critical flows
- Maintain test fixtures in line with current `conftest.py`

**REQ-TECH-003: Containerization**
- Docker container configuration for local testing
- Utilize and expand existing `Dockerfile` and `docker-compose.yml`
- Multi-stage build for efficient deployment

**REQ-TECH-004: Configuration management**
- Environment-based configuration
- Secrets management using GCP Secret Manager
- Feature flags for progressive rollout

**REQ-TECH-005: Performance optimization**
- Benchmark processing stages
- Implement performance profiling
- Optimize AI service usage

**REQ-TECH-006: Monitoring & observability**
- Structured logging throughout application
- Performance metric collection
- Error reporting and alerting

**REQ-TECH-007: Continuous integration/deployment**
- Automated testing pipeline
- Deployment to GCP Cloud Run
- Infrastructure as code for deployment

### 5.4 Deployment requirements

**REQ-DEPLOY-001: Google Cloud Run deployment**
- Deploy as containerized service on Cloud Run
- Optimize existing `deploy.sh` script (268 lines)
- Configure service accounts and permissions

**REQ-DEPLOY-002: Cloud functions integration**
- Maintain Cloud Function triggers for GCS events
- Refactor `main.py` event handlers
- Optimize cold start performance

**REQ-DEPLOY-003: Scaling configuration**
- Configure auto-scaling parameters
- Resource allocation optimization
- Concurrency limits

**REQ-DEPLOY-004: Monitoring setup**
- Configure Cloud Monitoring
- Set up logging and alerting
- Performance dashboards

**REQ-DEPLOY-005: Cost optimization**
- Optimize resource usage
- Implement caching where appropriate
- Configure budget alerts

## 6. User stories

### 6.1 Content creator stories

**US-001: Video upload processing**
- As a content creator, I want to upload a video and have it automatically processed, so I can quickly publish it with minimal manual effort.
- *Acceptance criteria:*
  - Video is processed within 10 minutes of upload
  - Creator receives notification when processing is complete
  - All metadata (transcript, subtitles, etc.) is generated automatically
  - Implementation should refactor `process_video_event()` from `process_uploaded_video.py`

**US-002: Processing status tracking**
- As a content creator, I want to see the current status of my video processing, so I know when it will be ready.
- *Acceptance criteria:*
  - Status updates for each processing stage
  - Estimated completion time
  - Error notifications if processing fails
  - Progress indication for long-running processes
  - Leverage `ProcessingStage` and `ProcessingStatus` from `core/models/video_job.py`

**US-003: Metadata review and editing**
- As a content creator, I want to review and edit generated metadata before publishing, so I can ensure quality and accuracy.
- *Acceptance criteria:*
  - Interface to view all generated metadata
  - Editing capabilities for transcript, title, description
  - Preview of how metadata will appear on platforms
  - Changes are saved and used for publishing

**US-004: Platform-specific publishing**
- As a content creator, I want to publish my processed video to multiple platforms with optimized metadata, so I can maximize my audience reach.
- *Acceptance criteria:*
  - One-click publishing to YouTube
  - Platform-specific metadata optimization
  - Scheduling options for delayed publishing
  - Publishing status and confirmation
  - Extend existing YouTube integration in `youtube_uploader.py`

**US-005: Processing customization**
- As a content creator, I want to customize which processing steps are applied to my video, so I can control the output based on my needs.
- *Acceptance criteria:*
  - Options to enable/disable specific processing steps
  - Presets for common combinations of processing steps
  - Custom parameters for specific processors (e.g., subtitle style)
  - Settings are remembered for future uploads

### 6.2 Administrator stories

**US-006: System monitoring**
- As an administrator, I want to monitor the overall system performance and processing queue, so I can ensure the service is running optimally.
- *Acceptance criteria:*
  - Dashboard showing current processing queue
  - Resource utilization metrics
  - Error rate and common failure points
  - Throughput and processing time statistics

**US-007: Service configuration**
- As an administrator, I want to configure system parameters and resource allocation, so I can optimize performance and costs.
- *Acceptance criteria:*
  - Configuration interface for system parameters
  - Ability to adjust resource limits
  - Cost estimation based on configuration
  - Changes take effect without service restart

**US-008: User management**
- As an administrator, I want to manage user accounts and permissions, so I can control access to the system.
- *Acceptance criteria:*
  - User creation, deletion, and editing
  - Role assignment
  - Access control for sensitive operations
  - Audit log of administrative actions

**US-009: Error investigation**
- As an administrator, I want to investigate processing errors, so I can resolve issues and improve system reliability.
- *Acceptance criteria:*
  - Detailed error logs with context
  - Ability to reprocess failed videos
  - Trend analysis of common errors
  - Integration with monitoring tools

### 6.3 Developer stories

**US-010: API integration**
- As a developer, I want to integrate with the video processing API, so I can use its capabilities in other applications.
- *Acceptance criteria:*
  - Comprehensive API documentation
  - Authentication mechanism for API access
  - Examples and SDKs for common languages
  - Rate limiting and usage metrics

**US-011: Custom processor development**
- As a developer, I want to create custom processors for the pipeline, so I can extend its functionality for specific needs.
- *Acceptance criteria:*
  - Documentation for processor interface
  - Example processors to use as templates
  - Testing framework for custom processors
  - Deployment process for new processors

**US-012: Webhook integration**
- As a developer, I want to configure webhooks for processing events, so I can trigger actions in external systems.
- *Acceptance criteria:*
  - Configurable webhook endpoints for different event types
  - Event payload documentation
  - Retry mechanism for failed webhook deliveries
  - Webhook delivery logs

## 7. Technical architecture details

### 7.1 Domain model

**Video Job Entity**
- Currently implemented in `core/models/video_job.py`
- Will be refactored to `domain/models/job.py`
- Core attributes:
  - Job ID (unique identifier)
  - Status (pending, in-progress, completed, failed)
  - Current processing stage
  - Completed stages
  - Created/updated timestamps
  - Source video reference
  - Output references
  - Error information

**Video Entity**
- Currently partially implemented in processing logic
- Will be defined in `domain/models/video.py`
- Core attributes:
  - Video ID
  - File information (name, size, format)
  - Duration
  - Resolution
  - Source location
  - Processed state

**Video Metadata Entity**
- Currently implemented as `VideoMetadata` in `core/models/video_job.py`
- Will be refactored to `domain/models/metadata.py`
- Core attributes:
  - Title
  - Description
  - Keywords/tags
  - Chapters
  - Transcript
  - Subtitles
  - Thumbnails
  - Platform-specific metadata

### 7.2 Use cases & application services

**Video Processing Service**
- Orchestrates the processing workflow
- Manages state transitions for video jobs
- Coordinates between different processing services
- Will expand `process_video_event()` from `process_uploaded_video.py`

**Transcription Service**
- Handles audio analysis and transcript generation
- Refactors `generate_transcript()` from `process_uploaded_video.py`
- Interfaces with AI services

**Subtitle Generation Service**
- Creates timestamped subtitles from audio
- Refactors `generate_vtt()` from `process_uploaded_video.py`
- Formats output for different platforms

**Metadata Generation Service**
- Creates various metadata artifacts (titles, descriptions, etc.)
- Refactors `generate_titles()` and other generation functions
- Optimizes metadata for different platforms

**Publishing Service**
- Handles video publishing to platforms
- Will refactor logic from `youtube_uploader.py`
- Manages platform-specific requirements

### 7.3 Adapters & infrastructure

**AI Service Adapters**
- Abstract interface in `application/interfaces/ai.py`
- Vertex AI implementation in `adapters/ai/vertex_ai.py`
- Gemini implementation in `adapters/ai/gemini.py`
- Mock implementation for testing

**Storage Adapters**
- Abstract interface in `application/interfaces/storage.py`
- GCS implementation in `adapters/storage/gcs.py`
- Local filesystem implementation for testing
- Refactors storage interactions from `process_uploaded_video.py`

**Publishing Adapters**
- Abstract interface in `application/interfaces/publishing.py`
- YouTube implementation in `adapters/publishing/youtube.py`
- Refactors from existing `youtube_uploader.py`

**API Infrastructure**
- FastAPI server configuration
- Route handlers for all endpoints
- Request/response schemas using Pydantic
- Dependency injection setup

### 7.4 Dependency injection

**Container Configuration**
- Will be implemented in `infrastructure/config/container.py`
- Manages application service instantiation
- Configures service dependencies
- Allows swapping implementations based on environment

**Service Locator Pattern**
- Provides access to services throughout application
- Simplifies testing through mock injection
- Enforces proper separation of concerns

### 7.5 Testing strategy

**Unit Testing**
- Domain models and business logic
- Application services with mocked dependencies
- Expand existing tests in `test_process_video.py` and `test_audio_processing.py`

**Integration Testing**
- Storage adapters against emulators/test environments
- AI service adapters with simplified models
- API endpoints with test client

**End-to-End Testing**
- Complete processing workflow
- Cloud Function triggers
- Video processing and publishing

### 7.6 Benchmarking and profiling

**Performance Metrics**
- Processing time per stage
- Memory utilization
- API response times
- AI service latency

**Profiling Tools**
- Code instrumentation for timing
- Resource usage tracking
- Bottleneck identification

### 7.7 Deployment architecture

**GCP Services**
- Cloud Run for API and processing service
- Cloud Storage for video files and artifacts
- Cloud Functions for event triggers
- Pub/Sub for asynchronous communication
- Secret Manager for credentials
- Logging and Monitoring

## 8. Implementation phases

### 8.1 Phase 1: Refactor core architecture

**Sprint 1: Domain model and structure setup**
- Establish new project structure
- Refactor domain models from existing code
- Set up dependency injection container
- Implement basic testing framework

**Sprint 2: Service layer implementation**
- Refactor processing services from monolithic code
- Implement storage adapters
- Create AI service adapters
- Unit test coverage for core services

### 8.2 Phase 2: API and infrastructure

**Sprint 3: API implementation**
- Implement FastAPI server
- Create API schemas and routes
- Add authentication and authorization
- Develop API documentation

**Sprint 4: Deployment and monitoring**
- Configure Docker and Cloud Run deployment
- Set up monitoring and logging
- Implement health checks
- Create deployment automation

### 8.3 Phase 3: Enhanced functionality

**Sprint 5: Advanced metadata generation**
- Enhance AI-powered metadata generation
- Implement feedback loop for quality improvement
- Add customization options
- Optimize AI prompt engineering

**Sprint 6: Multi-platform publishing**
- Extend YouTube integration
- Add support for additional platforms
- Implement platform-specific optimizations
- Create publishing queue and scheduling

### 8.4 Phase 4: Frontend integration and polish

**Sprint 7: Frontend API integration**
- Finalize API contracts with frontend
- Implement real-time status updates
- Create comprehensive API examples
- Develop client SDK

**Sprint 8: Performance optimization and scaling**
- Optimize processing performance
- Configure auto-scaling
- Implement caching strategies
- Conduct load testing

## 9. Metrics and analytics

### 9.1 Key performance indicators (KPIs)

- Video processing throughput (videos/hour)
- Average processing time per video
- AI generation quality scores
- API response times
- Error rates by processing stage
- System availability percentage

### 9.2 User analytics

- Processing volume by user
- Feature usage statistics
- Platform publishing distribution
- User retention and engagement

### 9.3 Cost analytics

- Processing cost per video
- AI service usage and cost
- Storage utilization and cost
- Infrastructure cost breakdown

## 10. Migration plan

### 10.1 Current code migration

- The existing code in `backend/video_processor/process_uploaded_video.py` (711 lines) will be refactored into:
  - Domain models in `domain/models/`
  - Application services in `application/services/`
  - Adapters in `adapters/`
  
- The YouTube uploader code in `backend/video_processor/youtube_uploader.py` (535 lines) will be refactored into:
  - YouTube adapter in `adapters/publishing/youtube.py`
  - Publishing service in `application/services/publishing.py`
  
- The API code in `backend/video_processor/api/` will be migrated to FastAPI in `infrastructure/api/`

### 10.2 Database migration

- Any existing data will be migrated to the new structure
- Backward compatibility maintained during transition
- Data validation and cleanup during migration

### 10.3 Testing and verification

- Parallel running of old and new systems
- Comparison of outputs for validation
- Performance benchmarking comparison
- Gradual traffic migration

## 11. Risks and mitigations

**Risk: AI service reliability**
- *Impact:* Processing failures, poor quality metadata
- *Mitigation:* Fallback providers, retry mechanisms, quality monitoring

**Risk: Processing performance issues**
- *Impact:* Long processing times, capacity limitations
- *Mitigation:* Performance profiling, optimization, scaling configuration

**Risk: GCP service limits**
- *Impact:* Processing throttling, increased costs
- *Mitigation:* Quotas monitoring, graceful degradation, cost alerts

**Risk: API compatibility issues**
- *Impact:* Frontend integration failures
- *Mitigation:* Versioned API, comprehensive testing, backward compatibility

**Risk: Security vulnerabilities**
- *Impact:* Unauthorized access, data breaches
- *Mitigation:* Security review, access controls, regular updates

## 12. Glossary

**AI service:** Cloud-based artificial intelligence services used for content analysis and generation.

**Adapter:** A software component that translates between core business logic and external services.

**Clean architecture:** A software design philosophy that separates concerns into layers with dependencies pointing inward.

**Dependency injection:** A technique where object dependencies are provided from outside rather than created internally.

**Domain model:** Core business objects and logic independent of external concerns.

**FastAPI:** A modern, high-performance web framework for building APIs with Python based on standard type hints.

**GCP:** Google Cloud Platform, the cloud infrastructure provider for the system.

**Hexagonal architecture:** An architectural pattern that allows an application to be driven by users, programs, or tests equally.

**Processing stage:** A discrete step in the video processing pipeline.

**Repository pattern:** A design pattern that mediates between the domain and data mapping layers.

**Vertex AI:** Google Cloud's unified machine learning platform.

**WebVTT:** Web Video Text Tracks format, a subtitle format for HTML5 video.
