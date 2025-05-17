****# Technical Context: Echo Platform (Consolidated)

---

## Python Environment & Package Management Policy

**All Python virtual environment and package management for the backend (`apps/core`) must be performed using [`uv`](https://github.com/astral-sh/uv). No other tools (pip, venv, conda, poetry, etc.) are permitted. All dependencies are managed via `pyproject.toml`, and all developers must use `uv` commands for environment creation, dependency installation, and management. This is a permanent, enforced project standard.**

## Guiding Principles
*   **Leverage Managed Services**: Prefer managed services (Supabase, GCS, Cloud Run, Vertex AI) to reduce operational overhead.
*   **Python for Backend, TypeScript for Frontend**: Utilize the strengths of each language in its respective domain.
*   **Clean Architecture & Modularity**: Ensure maintainability and scalability through well-defined interfaces and separation of concerns.
*   **Automation**: Automate testing, linting, building, and deployment wherever possible.
*   **Security by Design**: Integrate security considerations throughout the development lifecycle.

---

## Backend (API) - Technical Context

### Core Technologies:
*   **Programming Language**: Python 3.12+
*   **Web Framework**: FastAPI (for its performance, async capabilities, and Pydantic integration).
*   **API Router Aggregation**: All API routers are aggregated and re-exported in `api/endpoints/__init__.py` as `router`, enabling scalable API structure and simple registration in `main.py`. See systemPatterns.md for details.
*   **Data Validation & Schemas**: Pydantic.
*   **Dependency Injection**: `punq` or a similar lightweight DI library (to be standardized if `punq` is not the final choice).
*   **Storage**:
    *   **Local File Storage**: Async wrapper around Python's file I/O for development and testing environments.
    *   **Google Cloud Storage**: Using the `google-cloud-storage` client library with async wrappers for production deployments.
*   **AI/ML Integration**:
    *   **Google Gemini API**: Using `google-generativeai` package for text generation, content analysis, and summarization.
    *   **Async Operations**: All AI operations use async/await patterns with thread pooling for non-blocking behavior.
*   **Video Processing**: FFmpeg (called as a subprocess).
*   **Async Redis Caching**: `lib/cache/redis_cache.py` provides a settings-driven, async cache utility for backend and AI adapter use.
*   **Infrastructure Utilities**: All core backend utilities are implemented as stateless classes in `lib/utils/`:
    *   `ffmpeg_utils.py` for audio/frame extraction and metadata
    *   `file_utils.py` for temp directory management
    *   `subtitle_utils.py` for VTT/SRT subtitle generation
*   **Authentication Utilities**: Supabase JWT validation and user extraction via `lib/auth/supabase_auth.py` (Pydantic + FastAPI dependency).
*   **Custom Exceptions**: All service and utility errors are handled via a custom exception hierarchy in `core/exceptions.py`.
*   **Repository Layer**: All data access for core models is handled by repository classes in `operations/`, each with static CRUD and update methods, accepting a SQLAlchemy Session as the first argument.
*   **Testing**: Pytest for unit, integration, and E2E tests.

### Infrastructure & Cloud Services (Primary: Google Cloud Platform):
*   **Compute**: Google Cloud Run (for containerized FastAPI application), Google Cloud Functions (for specific serverless tasks if needed).
*   **Storage (Primary)**:
    *   **Object Storage**: Google Cloud Storage (GCS) for raw video files, processed videos, thumbnails, and other large assets.
    *   **Metadata & Application Data**: Supabase (PostgreSQL) for user data, video metadata, job status, application settings.
*   **AI/ML**: Google Vertex AI (Gemini models primarily, potentially other specialized models).
*   **Messaging/Task Queues**: (To be finalized - options include GCP Pub/Sub with Cloud Functions/Run, or Celery with RabbitMQ/Redis). This is critical for decoupling long-running video processing tasks.
*   **Secrets Management**: Google Secret Manager.
*   **Containerization**: Docker.
*   **API Gateway**: (Considered if complex routing or multiple backend services emerge - for now, FastAPI handles API exposure).

### Development Environment (Backend):
*   **Local Setup**: Python 3.12+ environment managed with `uv` (preferred package manager and installer), Docker Desktop, FFmpeg installed locally, Google Cloud SDK, `.env` files for local configuration.
*   **Package Management**: `uv` for creating virtual environments, installing packages, and resolving dependencies (faster than pip, venv, or conda).
*   **Code Quality**: Pre-commit hooks (e.g., Black, Flake8/Ruff, Mypy).
*   **Preferred Tools**: VS Code (with Python/Pylance extensions), Postman/Insomnia/SwaggerUI for API testing.

### Key Backend Environment Variables (Illustrative):
```
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-supabase-service-role-key # For backend use

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/gcp-service-account.json # For local dev
STORAGE_BUCKET_NAME=your-gcs-bucket-name
VERTEX_AI_LOCATION=your-vertex-ai-region

# AI Services (if direct keys are used, otherwise through GCP service accounts)
GEMINI_API_KEY=your-gemini-api-key 

# Other
FASTAPI_ENV=development # or production
JWT_SECRET_KEY=a-very-secure-secret # For any internal JWTs if needed, Supabase JWTs handled by Supabase client
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
# Task Queue (e.g., Redis URL if using Celery with Redis)
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## Frontend (Web Application) - Technical Context

### Core Technologies:
*   **Framework/Library**: React (likely via Next.js for its features, or Vite for a simpler setup - *Standardize this choice*).
*   **Language**: TypeScript.
*   **Build Tool/Dev Server**: Next.js built-in, or Vite.
*   **Routing**: Next.js file-system router, or TanStack Router if using Vite.
*   **UI Components**: `shadcn/ui` (built on Radix UI and Tailwind CSS).
*   **Styling**: Tailwind CSS.
*   **State Management**:
    *   **Server State**: TanStack Query (React Query).
    *   **Client State**: React Context API, Zustand, or local component state (`useState`, `useReducer`) as appropriate. Avoid over-engineering global client state.
*   **API Communication**:
    *   **HTTP Client**: `fetch` API (possibly wrapped in a lightweight custom client or using a library like `axios` if advanced features are needed).
    *   **WebSockets**: Native WebSocket API for real-time communication with the FastAPI backend.

### Authentication:
*   **Provider**: Supabase Auth (Google OAuth as the primary method).
*   **Token Management**: Supabase client library handles JWT refresh and storage. Tokens are attached to API requests to the backend.

### Development Tooling (Frontend):
*   **Package Manager**: `pnpm` (preferred for efficiency) or `npm`/`yarn`.
*   **Linting/Formatting**: Biome (preferred for its all-in-one nature) or ESLint + Prettier.
*   **Testing**: Vitest (if using Vite) or Jest with React Testing Library.

### Development Setup (Frontend):
1.  Node.js (LTS version) and `pnpm` installed.
2.  Access to a running instance of the Backend API.
3.  Supabase project configured with Google OAuth and necessary tables/RLS.
4.  Google Cloud Storage bucket for direct uploads (frontend will need CORS configuration on the bucket).

### Key Frontend Environment Variables (`.env.local` or similar):
```
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 # or your deployed API URL
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws # or your deployed WebSocket URL

# Google Cloud Storage (if needed directly for signed URL construction, though backend should provide full URLs)
# NEXT_PUBLIC_GCS_BUCKET_NAME=your-gcs-bucket-name 
```

---

## Platform-Wide Technical Aspects

### Deployment & CI/CD:
*   **Source Control**: Git (hosted on GitHub).
*   **CI/CD Platform**: GitHub Actions.
*   **Backend Deployment**: Docker images built via GitHub Actions, pushed to Google Artifact Registry (or Docker Hub), and deployed to Google Cloud Run.
*   **Frontend Deployment**: Static site generation (Next.js) or build deployed to a CDN/hosting platform like Vercel, Netlify, or Google Cloud Storage with Cloud CDN.
*   **Environments**: At least `development`, `staging`, and `production` for both frontend and backend.

### Technical Constraints & Goals (Platform-Wide):
*   **Performance**: Fast API response times (<200ms for most non-processing endpoints). Quick frontend load times (e.g., LCP < 2.5s). Efficient video processing (e.g., aiming for <2x real-time duration for common operations).
*   **Scalability**: Backend services designed to scale horizontally (Cloud Run). Frontend capable of handling many concurrent users.
*   **Security**: HTTPS for all traffic. JWT-based authentication between frontend and backend. Secure handling of credentials (Secret Manager). Role-Based Access Control (RBAC) via Supabase RLS and potentially within the application logic. Protection against common web vulnerabilities (OWASP Top 10).
*   **Browser Support (Frontend)**: Modern evergreen browsers (latest 2 versions of Chrome, Firefox, Safari, Edge).
*   **API Design**: RESTful principles for HTTP APIs. Clear WebSocket message contracts.

### Integration Points (Summary):
*   **Frontend <-> Backend API**: RESTful HTTP calls (for actions, data fetching) and WebSockets (for real-time processing updates).
*   **Frontend <-> Supabase**: Authentication, direct database interaction for user-specific, non-sensitive data if appropriate and secured by RLS.
*   **Frontend <-> GCS**: Direct video uploads using signed URLs obtained from the Backend API.
*   **Backend API <-> Supabase**: Storing/retrieving metadata, user information, job statuses.
*   **Backend API <-> GCS**: Storing/retrieving video files and other assets.
*   **Backend API <-> AI Services (Vertex AI/Gemini)**: Sending data for analysis, receiving results.
*   **Backend API <-> Publishing Platforms (e.g., YouTube API)**: Sending processed video and metadata for publishing.
