# Echo Developer Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Development Setup](#development-setup)
4. [API Startup Guide](#api-startup-guide)
5. [Backend Development](#backend-development)
6. [Frontend Development](#frontend-development)
7. [Database Management](#database-management)
8. [API Reference](#api-reference)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

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

- **Docker** and **Docker Compose** for containerized development
- **Git** for version control
- **Optional**: Node.js 20+ and Python 3.11+ for local development without Docker

### Quick Start (Docker - Recommended)

1. **Clone and navigate to the project:**

```bash
git clone <repository-url>
cd echo
```

2. **Start the complete development environment:**

```bash
pnpm dev
```

This single command will:

- Start local Supabase database
- Start Python FastAPI backend (port 8000)
- Start TypeScript frontend (port 3000)
- Set up the complete development environment with hot reloading

3. **Access the application:**

- 🌐 **Frontend**: http://localhost:3000
- 🚀 **Backend API**: http://localhost:8000
- 📊 **API Documentation**: http://localhost:8000/docs
- 🗄️ **Supabase API**: http://localhost:54321
- 📧 **Email UI (Inbucket)**: http://localhost:54325

### Development Commands

```bash
# Essential commands
pnpm dev                    # Start entire development environment
pnpm build                  # Build all applications
pnpm test                   # Run all tests and quality checks

# Database operations
pnpm db:start              # Start Supabase
pnpm db:stop               # Stop Supabase
pnpm db:push               # Push schema changes
pnpm db:reset              # Reset database

# Type generation
pnpm gen:types             # Generate all types
pnpm gen:types:supabase    # Generate Supabase types only

# Quality checks
pnpm typecheck             # Type check all applications
pnpm lint                  # Lint all applications
pnpm format                # Format all applications

# Targeted development
pnpm dev:web               # Frontend only
pnpm dev:core              # Backend only
pnpm dev:api               # API only (simple startup)
```

### Alternative Setup (Local Development)

If you prefer to run services locally without Docker:

1. **Install dependencies:**

```bash
# Install Node.js dependencies
pnpm install

# Set up Python environment (UV handles this automatically)
cd apps/core
uv sync --dev  # Creates venv and installs dependencies automatically
cd ../..
```

2. **Start Supabase locally:**

```bash
pnpm db:start
```

3. **Apply migrations and generate types:**

```bash
pnpm db:push
pnpm types:generate
```

4. **Start development servers:**

```bash
# Terminal 1: Backend API
pnpm dev:api

# Terminal 2: Frontend
pnpm dev:web
```

## API Startup Guide

### TL;DR - Just Start the API

```bash
# Option 1: Use the simple script
./start-api.sh

# Option 2: Use pnpm alias (recommended)
pnpm dev:api

# Option 3: Use the existing turbo command
pnpm dev:core
```

### What This Does

- ✅ Uses `uv` for fast, reliable Python package management
- ✅ Automatically creates virtual environment if missing
- ✅ Sets correct PYTHONPATH for module imports
- ✅ Starts FastAPI with hot reload on port 8000
- ✅ No complex orchestration or dependencies

### API Endpoints

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **OpenAPI**: http://localhost:8000/openapi.json

### Requirements

- Python 3.13+ (managed by `uv`)
- `uv` package manager (install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Troubleshooting API Startup

If you get import errors:

1. Make sure you're running from the project root
2. The script automatically sets `PYTHONPATH` correctly
3. Virtual environment is created automatically with all dependencies

### No More Clusterfuck

This replaces all the complex startup scripts with one simple, reliable approach:

- No manual virtual environment activation needed
- No complex PYTHONPATH management
- No dependency on other services
- Just works™️

## Backend Development

### Setup

1. **Navigate to core app:**

```bash
cd apps/core
```

2. **Set up environment and install dependencies:**

```bash
uv sync --dev  # Creates venv and installs all dependencies automatically
```

3. **Start the API server:**

```bash
# Use the simple startup script
./start-api.sh

# Or use the pnpm command
pnpm dev:api
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

## Type Generation Strategy

Echo uses a comprehensive type generation strategy to maintain type safety across the entire stack. The process follows a dependency chain from database schema to frontend types.

### Type Generation Flow

```
SQL Schema (Supabase)
    ↓
SQLAlchemy ORM Models (Python)
    ↓
Pydantic Models (Python)
    ↓
TypeScript Types (Frontend)
    ↓
API Client Types (Frontend)
```

### Automated Type Generation

The unified type generation script handles all type generation with proper dependency ordering:

```bash
# Generate all types in correct order
pnpm types:generate

# Generate specific type layers
pnpm types:orm        # SQLAlchemy models from database
pnpm types:pydantic   # Pydantic models from database
pnpm types:typescript # TypeScript types from database
pnpm types:api        # API client types from Pydantic models
```

### Type Generation Details

#### 1. SQLAlchemy ORM Models

- **Source**: PostgreSQL database schema via Supabase
- **Tool**: `sqlacodegen`
- **Output**: `apps/core/models/generated.py`
- **Command**: `pnpm types:orm`

Generated models provide the data access layer for the Python backend.

#### 2. Pydantic Models

- **Source**: PostgreSQL database schema via Supabase
- **Tool**: `supabase-pydantic`
- **Output**: `apps/core/models/supabase_pydantic.py`
- **Command**: `pnpm types:pydantic`

These models are used for API serialization and validation.

#### 3. TypeScript Database Types

- **Source**: PostgreSQL database schema via Supabase
- **Tool**: `supabase gen types typescript`
- **Output**: `packages/supabase/types/database.ts`
- **Command**: `pnpm types:typescript`

Provides type-safe database access for the frontend Supabase client.

#### 4. API Client Types

- **Source**: Pydantic models from backend API
- **Tool**: `pydantic-to-typescript`
- **Output**: `apps/web/app/types/api.ts`
- **Command**: `pnpm types:api`

Ensures type safety between frontend and backend API communication.

### Type Generation Best Practices

1. **Always regenerate after schema changes:**

```bash
# After database migrations
pnpm db:push
pnpm types:generate
```

2. **Verify type consistency:**
   The generation script includes validation to ensure all files are created successfully.

3. **Development workflow:**

- Make database schema changes in Supabase migrations
- Apply migrations with `pnpm db:push`
- Regenerate all types with `pnpm types:generate`
- Update API schemas and frontend code as needed

4. **Troubleshooting type generation:**

- Ensure all services are running (database, API)
- Check that migrations are applied
- Verify tool dependencies are installed
- Review generation script logs for specific errors

## Database Management

### Local Database Workflow

```bash
# Apply migrations and regenerate types
pnpm db:push
pnpm types:generate

# Quick database reset (development only)
pnpm db:reset
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

The application includes comprehensive Docker support for both development and production environments.

#### Development Deployment

```bash
# Start complete development environment
pnpm dev

# Or manually with Docker Compose
docker-compose up --build
```

#### Production Deployment

1. **Build production images:**

```bash
# Build all services for production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

2. **Deploy with production configuration:**

```bash
# Set production environment variables
export ENVIRONMENT=production
export DATABASE_URL=<production_db_url>
export SUPABASE_URL=<production_supabase_url>
# ... other production variables

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### Container Architecture

- **echo-api**: FastAPI backend with hot reloading in development
- **echo-web**: React frontend with Vite dev server (development) or Nginx (production)
- **supabase-db**: PostgreSQL database with automatic migration application
- **supabase-api**: Supabase API server for auth and real-time features
- **redis**: Caching layer for AI responses and session management

#### Docker Best Practices

- Multi-stage builds for optimized production images
- Volume mounts for development hot reloading
- Health checks for service dependency management
- Proper environment variable handling
- Automated migration application on startup

## Troubleshooting

### Common Issues

#### Docker Environment Issues

- **Docker not running**: Ensure Docker Desktop is started
- **Port conflicts**: Check if ports 3000, 8000, 54321, 54322, 6379 are available
- **Services not starting**: Run `pnpm dev:status` to check service health
- **Container build failures**: Try `docker-compose down && docker-compose up --build`

#### Database Connection Issues

- **Local development**: Services should connect automatically via Docker networking
- **Connection refused**: Ensure Supabase container is healthy (`pnpm dev:status`)
- **Migration issues**: Check that migrations are applied during startup
- **Schema out of sync**: Run `pnpm types:generate` to regenerate types

#### Type Generation Issues

- **Generation script fails**: Ensure all services are running (`pnpm dev:status`)
- **Missing dependencies**: Check that generation tools are installed in containers
- **File not found errors**: Verify database schema exists and migrations are applied
- **Permission issues**: Ensure generated files directory is writable

#### Authentication Issues

- **JWT token invalid**: Check Supabase auth configuration in Docker environment
- **CORS issues**: Verify frontend and backend are running on expected ports
- **RLS policies**: Ensure policies are correctly configured in migrations

#### Hot Reloading Issues

- **Changes not reflected**: Check that volume mounts are working correctly
- **Frontend not updating**: Verify Vite dev server is running in container
- **Backend not restarting**: Check uvicorn reload configuration in Docker

#### Performance Issues

- **Slow startup**: First-time container builds take longer; subsequent starts are faster
- **High resource usage**: Adjust Docker Desktop resource limits if needed
- **Network latency**: Use `docker-compose logs` to identify bottlenecks

### Development Tips

1. **Use the unified development commands:**

   - `pnpm dev` - Start complete Docker development environment
   - `pnpm types:generate` - Regenerate all types after schema changes
   - `pnpm dev:logs` - Monitor all service logs
   - `pnpm dev:status` - Check service health

2. **Monitor logs effectively:**

   - All services: `pnpm dev:logs`
   - Specific service: `pnpm dev:logs echo-api`
   - Backend API: Check FastAPI logs for API errors
   - Frontend: Use browser dev tools for client-side issues
   - Database: Check Supabase dashboard for query issues

3. **Docker development workflow:**

   - Services auto-restart on code changes (hot reloading)
   - Database persists between container restarts
   - Use `pnpm dev:restart` for clean environment reset
   - Access services via localhost ports (see Quick Start section)

4. **Type safety maintenance:**

   - Always run `pnpm types:generate` after database schema changes
   - Verify type generation completed successfully
   - Check that all generated files are properly imported

5. **Code quality:**
   - Follow the cursor rules in `.cursor/rules/`
   - Run tests before committing
   - Use type checking: `mypy` for Python, `tsc` for TypeScript
   - Leverage Docker for consistent development environment

### Docker Development Benefits

- **Consistent Environment**: Same setup across all developer machines
- **Service Isolation**: Each service runs in its own container
- **Hot Reloading**: Code changes automatically trigger rebuilds
- **Easy Reset**: Quick environment cleanup and restart
- **Production Parity**: Development closely matches production setup

For additional help, refer to the specific documentation in the `.cursor/rules/` directory for development guidelines and best practices.
