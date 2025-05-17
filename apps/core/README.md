# Echo Core Application

## Project Overview

The Echo Core Application is a backend service for video processing featuring:

- Video upload, processing, and metadata extraction
- Integration with AI services for transcription and content analysis
- Secure storage in cloud or local filesystem
- Support for Supabase authentication and PostgreSQL
- Standardized API for frontend integration

## Architecture

The application follows a clean, layered architecture:

```
apps/core/
├── api/             # API Layer (FastAPI endpoints, Pydantic schemas)
├── core/            # Core configurations and shared utilities
├── lib/             # Common libraries and adapters
│   ├── ai/             # AI service adapters (Gemini, cache)
│   ├── publishing/     # Publishing adapters (YouTube)
│   ├── storage/        # Storage adapters (GCS, local)
│   └── utils/          # Helper utilities (FFmpeg, file, subtitle)
├── models/          # SQLAlchemy data models
├── operations/      # Data access layer (repositories)
├── services/        # Business logic and orchestration
└── tests/           # Automated tests
    ├── integration/    # API and service integration tests
    └── unit/           # Component-level unit tests
```

### Architecture Layers

1. **API Layer** - HTTP interface using FastAPI
2. **Service Layer** - Business logic orchestration
3. **Operations Layer** - Data access through repositories
4. **Model Layer** - Database schema definitions
5. **Library Layer** - Common utilities and external integrations:
   - **AI Adapters** - Integrations with AI services (Gemini)
   - **Storage Adapters** - File storage implementations (GCS, local)
   - **Publishing Adapters** - Distribution channel integrations (YouTube)
   - **Utilities** - Common tools for video/audio processing

## Local Development Setup

### Prerequisites

- Python 3.10+ installed
- [uv](https://github.com/astral-sh/uv) for package management
- [Docker](https://www.docker.com/) for running Supabase locally
- [Supabase CLI](https://supabase.com/docs/guides/cli) for local development

### Environment Setup

1. Clone the repository and navigate to the core application:

```bash
cd apps/core
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

### Supabase Local Setup

1. Install Supabase CLI:

```bash
npm install supabase --save-dev
```

2. Initialize and start local Supabase:

```bash
cd ../../  # Navigate to the project root
supabase init
supabase start
```

3. Copy the environment variables displayed by the Supabase CLI.

### Environment Configuration

1. Create a `.env` file in `apps/core/`:

```bash
cp .env.example .env
```

2. Edit the `.env` file with your local Supabase credentials and other environment variables.

### Database Migrations

Apply migrations to your local database:

```bash
cd apps/core
alembic upgrade head
```

### Starting the API Server

```bash
cd apps/core
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Authentication

Authentication is handled by Supabase. The backend expects a JWT token in the `Authorization` header.

### Video Processing API

#### Upload a Video

```
POST /api/v1/videos/upload
```

**Request:**
- Multipart form data with `file` field containing the video

**Response:**
```json
{
  "job_id": 123,
  "status": "PENDING"
}
```

#### Get Job Status

```
GET /api/v1/videos/jobs/{job_id}
```

**Response:**
```json
{
  "id": 123,
  "video_id": 456,
  "status": "COMPLETED",
  "processing_stages": {
    "transcription": true,
    "metadata": true
  },
  "error_message": null,
  "created_at": "2025-05-16T12:00:00Z",
  "updated_at": "2025-05-16T12:05:00Z",
  "video": {
    "id": 456,
    "uploader_user_id": "user-uuid",
    "original_filename": "my-video.mp4",
    "storage_path": "uploads/user-uuid/my-video.mp4",
    "content_type": "video/mp4",
    "size_bytes": 1024000,
    "created_at": "2025-05-16T12:00:00Z",
    "updated_at": "2025-05-16T12:00:00Z"
  },
  "metadata": {
    "id": 789,
    "job_id": 123,
    "title": "Auto-generated title",
    "description": "Auto-generated description",
    "tags": ["tag1", "tag2"],
    "transcript_text": "Full transcript of the video...",
    "transcript_file_url": "https://example.com/transcripts/123.txt",
    "subtitle_files_urls": {
      "vtt": "https://example.com/subtitles/123.vtt",
      "srt": "https://example.com/subtitles/123.srt"
    },
    "thumbnail_file_url": "https://example.com/thumbnails/123.jpg",
    "extracted_video_duration_seconds": 120.5,
    "extracted_video_resolution": "1920x1080",
    "extracted_video_format": "mp4",
    "show_notes_text": "Auto-generated show notes...",
    "created_at": "2025-05-16T12:05:00Z",
    "updated_at": "2025-05-16T12:05:00Z"
  }
}
```

## Environment Variables

| Variable                         | Description                        | Default          |
| -------------------------------- | ---------------------------------- | ---------------- |
| `ENVIRONMENT`                    | Development/production environment | `development`    |
| `DATABASE_URL`                   | PostgreSQL connection string       |                  |
| `SUPABASE_URL`                   | Supabase project URL               |                  |
| `SUPABASE_ANON_KEY`              | Supabase anonymous key             |                  |
| `SUPABASE_SERVICE_ROLE_KEY`      | Supabase service role key          |                  |
| `SUPABASE_JWT_SECRET`            | Supabase JWT secret                |                  |
| `STORAGE_BACKEND`                | Storage backend (`local` or `gcs`) | `local`          |
| `LOCAL_STORAGE_PATH`             | Path for local file storage        | `./output_files` |
| `GCS_BUCKET_NAME`                | Google Cloud Storage bucket name   |                  |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP credentials JSON       |                  |
| `GEMINI_API_KEY`                 | Google Gemini AI API key           |                  |
| `REDIS_URL`                      | Redis connection URL for caching   |                  |

## Testing

### Running Tests

```bash
cd apps/core

# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run integration tests only
pytest tests/integration

# Run with coverage report
pytest --cov=.
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
  - Mock dependencies to focus on component behavior
  - Fast and independent of external systems
  
- **Integration Tests**: Test API endpoints and database interactions
  - `tests/integration/api/`: Tests for API endpoints
  - `tests/integration/conftest.py`: Common fixtures for database and API testing
  - Test authentication, error handling, and success paths
  
- **Test Fixtures**: Common test utilities and setup in `conftest.py` files
  - Database session management
  - Authentication helpers
  - File upload utilities
  - Mocked services

## Video Processing Architecture

The video processing functionality is distributed across several modules following clean architecture principles:

1. **Domain Models** (`models/`): Define the core entities
   - Video, VideoJob, VideoMetadata models with SQLAlchemy
   - Pydantic schemas for API validation and responses

2. **Service Layer** (`services/`): Contains core business logic
   - Video processing orchestration
   - Transcription and metadata generation
   - Job status management

3. **Adapters** (`lib/`): Interface implementations
   - AI adapters for transcription and content analysis
   - Storage adapters for file management
   - Publishing adapters for distribution (YouTube)

4. **API Layer** (`api/endpoints/`): External interface
   - FastAPI endpoints for video upload and processing
   - Authentication and validation middleware
   - Response formatting

This architecture ensures:
- **Testability**: Each layer can be tested in isolation
- **Maintainability**: Changes in one layer don't affect others
- **Flexibility**: Easy to swap implementations (e.g., storage providers)

## Deployment

The application can be deployed as a container or as a standard Python application. For production, ensure:

1. Set `ENVIRONMENT=production` in environment variables
2. Use a production-ready ASGI server like Gunicorn with Uvicorn workers
3. Set up proper logging and monitoring
4. Configure proper security settings for Supabase