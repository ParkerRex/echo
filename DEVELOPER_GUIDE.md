# Echo Developer Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Development Setup](#development-setup)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Database Management](#database-management)
7. [API Reference](#api-reference)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## Project Overview

Echo is an AI-powered YouTube video metadata generator that helps users automatically generate titles, subtitles, chapters, and descriptions using Google Gemini.

### Tech Stack
- **Backend**: FastAPI with Python 3.10+
- **Frontend**: React with TanStack Router
- **Database**: PostgreSQL via Supabase
- **Storage**: Google Cloud Storage
- **AI**: Google Gemini via Vertex AI
- **Auth**: Supabase Auth

## Architecture

The application follows a clean, layered architecture:

```
echo/
├── apps/
│   ├── core/           # FastAPI Backend
│   │   ├── api/        # API Layer (FastAPI endpoints, Pydantic schemas)
│   │   ├── core/       # Core configurations and shared utilities
│   │   ├── lib/        # Common libraries and adapters
│   │   │   ├── ai/     # AI service adapters (Gemini, cache)
│   │   │   ├── publishing/ # Publishing adapters (YouTube)
│   │   │   ├── storage/    # Storage adapters (GCS, local)
│   │   │   └── utils/      # Helper utilities (FFmpeg, file, subtitle)
│   │   ├── models/     # SQLAlchemy data models
│   │   ├── operations/ # Data access layer (repositories)
│   │   ├── services/   # Business logic and orchestration
│   │   └── tests/      # Automated tests
│   └── web/            # React Frontend
│       ├── app/
│       │   ├── components/ # React components
│       │   ├── lib/        # Frontend utilities
│       │   ├── routes/     # TanStack Router routes
│       │   └── services/   # API client services
└── packages/
    ├── db/             # Database utilities
    └── supabase/       # Supabase configuration and migrations
```

### Architecture Layers

1. **API Layer** - HTTP interface using FastAPI
2. **Service Layer** - Business logic orchestration
3. **Operations Layer** - Data access through repositories
4. **Model Layer** - Database schema definitions
5. **Library Layer** - Common utilities and external integrations

## Development Setup

### Prerequisites

- **Python 3.10+** with [uv](https://github.com/astral-sh/uv) for package management
- **Node.js 18+** with [pnpm](https://pnpm.io/) for frontend dependencies
- **Docker** for running Supabase locally
- **Supabase CLI** for local development

### Initial Setup

1. **Clone and navigate to the project:**
```bash
git clone <repository-url>
cd echo
```

2. **Install Supabase CLI:**
```bash
npm install -g @supabase/cli
```

3. **Start local Supabase:**
```bash
supabase start
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your local Supabase credentials
```

## Backend Development

### Setup

1. **Navigate to core app:**
```bash
cd apps/core
```

2. **Create and activate virtual environment:**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
uv pip install -r pyproject.toml
```

4. **Apply database migrations:**
```bash
alembic upgrade head
```

5. **Start the API server:**
```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Environment Variables

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

## Frontend Development

### Setup

1. **Navigate to web app:**
```bash
cd apps/web
```

2. **Install dependencies:**
```bash
pnpm install
```

3. **Start development server:**
```bash
pnpm dev
```

The frontend will be available at `http://localhost:3000`.

### Key Frontend Technologies

- **React 18** with TypeScript
- **TanStack Router** for routing
- **TanStack Query** for server state management
- **Supabase JS** for auth and database operations
- **Tailwind CSS** for styling

### Type Generation

To maintain type safety between backend and frontend:

```bash
# Generate TypeScript types from Pydantic models
pnpm run generate:api-types
```

This generates TypeScript types in `apps/web/src/types/api.ts` from the Pydantic models in `apps/core/api/schemas/`.

## Database Management

### Local Database Workflow

```bash
# Apply migrations
pnpm run db:migrate

# Regenerate ORM models
pnpm run db:codegen

# Combined refresh
pnpm run db:refresh
```

### Creating Migrations

1. **Create new migration:**
```bash
supabase migration new <migration_name>
```

2. **Write SQL in the generated file**

3. **Apply migration:**
```bash
supabase db push
```

### Database Schema

The application uses three main tables:

- **`videos`** - Stores uploaded video information
- **`video_jobs`** - Tracks processing status
- **`video_metadata`** - Stores AI-generated metadata

## API Reference

### Authentication

All API endpoints require authentication via Supabase JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

### Core Endpoints

#### Upload Video
```http
POST /api/v1/videos/upload
Content-Type: multipart/form-data

file: <video_file>
```

**Response:**
```json
{
  "job_id": 123,
  "status": "PENDING"
}
```

#### Get Job Status
```http
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
    "transcript_text": "Full transcript...",
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

## Testing

### Backend Testing

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

### Frontend Testing

```bash
cd apps/web

# Run unit tests
pnpm test

# Run E2E tests
pnpm test:e2e
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints and database interactions
- **E2E Tests**: Test complete user workflows

## Deployment

### Production Environment

1. **Set environment variables:**
```bash
export ENVIRONMENT=production
export DATABASE_URL=<production_db_url>
export SUPABASE_URL=<production_supabase_url>
# ... other production variables
```

2. **Deploy backend:**
```bash
cd apps/core
# Build and deploy using your preferred method (Docker, Cloud Run, etc.)
```

3. **Deploy frontend:**
```bash
cd apps/web
pnpm build
# Deploy build output to your hosting provider
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
- Verify Supabase is running: `supabase status`
- Check environment variables in `.env`
- Ensure migrations are applied: `supabase db push`

#### Type Generation Issues
- Ensure backend is running before generating types
- Check that Pydantic models are properly exported
- Verify `pydantic-to-typescript` is installed

#### Authentication Issues
- Verify JWT token is valid and not expired
- Check Supabase project configuration
- Ensure RLS policies are correctly configured

### Development Tips

1. **Use the monorepo scripts:**
   - `pnpm run db:migrate` - Apply database migrations
   - `pnpm run db:codegen` - Regenerate ORM models
   - `pnpm run generate:api-types` - Generate TypeScript types

2. **Monitor logs:**
   - Backend: Check FastAPI logs for API errors
   - Frontend: Use browser dev tools for client-side issues
   - Database: Check Supabase dashboard for query issues

3. **Code quality:**
   - Follow the cursor rules in `.cursor/rules/`
   - Run tests before committing
   - Use type checking: `mypy` for Python, `tsc` for TypeScript

For additional help, refer to the specific documentation in the `.cursor/rules/` directory for development guidelines and best practices. 