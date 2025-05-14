# Developer Setup Guide

## Setup Python Environment

This project uses Python 3.11. We recommend using a virtual environment:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (including development tools)
pip install -e ".[dev]"
```

## Configuration

The application requires Supabase credentials and other environment variables:

1. Copy the example .env file: `cp ../.env .env` (if not already in the API directory)
2. Set needed environment variables in the .env file

## Running the Application

```bash
# Start the FastAPI application
uvicorn video_processor.infrastructure.api.main:app --reload
```


`uvicorn video_processor.infrastructure.api.server:app --reload --host 0.0.0.0 --port 8000`


## Testing

```bash
# Run tests
pytest
```

## Code Quality

This project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit hooks manually
pre-commit run --all-files
```

---
# Original README Content Follows:

# Echo Project

## Project Structure

This is a monorepo containing different components of the Echo project.

### API (Python Backend)

All Python development is consolidated in the `/api` directory. For setup instructions, see [API README](/api/README.md).

### Web Frontend

Frontend code is in the `/apps/web` directory.

### Packages

Shared libraries and utilities can be found in `/packages`.

## Development

Please see individual component READMEs for development setup instructions:

- [API Development](/api/README.md)
- [Web Development](/apps/web/README.md) (if available)

## Architecture Overview

This project integrates a web frontend, a Python backend API, and a Supabase package to deliver a comprehensive video processing pipeline.

-   **Web App (`apps/web`)**: A React/Vite application serving as the user interface. It handles user authentication via Supabase (Google OAuth), video uploads (to GCS via signed URLs), and real-time status updates using WebSockets.
-   **API (`api`)**: A Python/FastAPI backend responsible for the core video processing logic. It authenticates requests using Supabase JWTs, interacts with Google Cloud Storage (GCS) for files, utilizes AI services (Gemini/Vertex AI) for content analysis, and communicates with the web app via REST APIs and WebSockets.
-   **Supabase Package (`packages/supabase` or `db`)**: This TypeScript package provides Supabase client abstractions for authentication and database interactions.
    -   **Supabase migrations and CLI project files are now located in `packages/supabase/`.**  
        - Run all Supabase CLI commands (e.g., `supabase db reset`, `supabase start`) from the `packages/supabase/` directory.
        - The canonical location for database migrations is `packages/supabase/migrations/`.
    -   The `web` app uses the client-side Supabase client from this package (or a similar setup) for its authentication flow.
    -   The `api` (Python) uses `supabase-py` to verify JWTs and interact with the Supabase database for metadata storage (e.g., job status, user information).

### System Interaction Diagram

```mermaid
graph LR
    subgraph "User Space"
        User[User]
    end

    subgraph "Frontend Application (apps/web)"
        WebApp[Web App (React/Vite)]
    end

    subgraph "Backend Application (api)"
        API[API (Python/FastAPI - Video Processing)]
    end

    subgraph "Shared Abstraction (packages/supabase)"
        SupabaseTSClient["Supabase Client (TypeScript for Web App Auth)"]
    end

    subgraph "External Services"
        SupabaseCloud["Supabase Cloud (Auth, Database)"]
        GCS[GCS (Video Files)]
        AIServices[AI Services (Gemini/Vertex AI)]
    end

    User -- "Interacts" --> WebApp

    WebApp -- "1. Auth via Supabase Client" --> SupabaseTSClient
    SupabaseTSClient -- "2. Supabase Client interacts" --> SupabaseCloud
    SupabaseCloud -- "3. Returns JWT to Client" --> SupabaseTSClient
    SupabaseTSClient -- "4. JWT to WebApp" --> WebApp

    WebApp -- "5. API Requests with JWT (e.g., get signed URL, job status)" --> API
    WebApp -- "6. Direct Upload to GCS (using signed URL from API)" --> GCS

    API -- "7. Validates JWT using `supabase-py`" --> SupabaseCloud
    API -- "8. Stores/Retrieves Job Metadata using `supabase-py`" --> SupabaseCloud
    API -- "9. Interacts with Storage" --> GCS
    API -- "10. Uses AI for Processing" --> AIServices
    API -- "11. Sends Real-time Updates (WebSockets)" --> WebApp

    %% Styling
    style WebApp fill:#D1E8FF,stroke:#333,stroke-width:2px
    style API fill:#E8D1FF,stroke:#333,stroke-width:2px
    style SupabaseTSClient fill:#D1FFD1,stroke:#333,stroke-width:2px
    style SupabaseCloud fill:#FFF3D1,stroke:#333,stroke-width:2px
    style GCS fill:#FFD1D1,stroke:#333,stroke-width:2px
    style AIServices fill:#D1FFFF,stroke:#333,stroke-width:2px
```

### Architectural Setup and Data Flow:

1.  **Monorepo Structure**:
    *   Your monorepo (likely managed by `pnpm-workspace.yaml` or similar) houses the `web`, `api`, and `supabase` package (`db`). This allows for shared configurations and easier cross-component development.

2.  **Supabase Package (`db`) & Integration**:
    *   **Role**: This package, as per `db-repomix-output.txt`, primarily offers TypeScript Supabase clients (`clients/client.ts` and `clients/server.ts`).
    *   **`web` App Usage**: The `web` application will directly use the `clients/client.ts` (or a similar setup using `@supabase/supabase-js`) to handle the Google OAuth flow and manage user sessions. This client is responsible for obtaining JWTs from Supabase.
    *   **`api` App Usage**: The Python-based `api` will not directly use the TypeScript clients from the `db` package. Instead, it will use `supabase-py` (as noted in `api/api-implementation-tasks.md`). The `api` will:
        *   Verify JWTs sent by the `web` app in the `Authorization` header.
        *   Interact with the Supabase Database for operations like storing job metadata, user profiles, etc.
    *   The *concept* of abstracting Supabase interactions is what's shared. The `db` package demonstrates this for the TypeScript world.

3.  **`web` Application (Frontend)**:
    *   **Authentication**: Initiates Google OAuth through the Supabase client. Upon successful login, it receives a JWT.
    *   **API Communication**: All authenticated requests to the `api` backend will include this JWT in the `Authorization: Bearer <token>` header.
    *   **Video Uploads**:
        1.  User selects a video file.
        2.  `web` app requests a signed GCS upload URL from the `api`.
        3.  `web` app uploads the file directly to GCS using the signed URL.
        4.  Upon successful GCS upload, `web` app notifies the `api` to start processing.
    *   **Real-time Updates**: Establishes a WebSocket connection with the `api` to receive live updates on video processing status, new metadata, etc. (as planned in `apps/web/web-memory-bank/tasks.md`).

4.  **`api` Application (Backend)**:
    *   **Endpoints**: Exposes RESTful API endpoints for actions like requesting signed URLs, initiating processing jobs, retrieving job status/metadata, and updating metadata.
    *   **Security**: Endpoints are secured using JWT. The `api` verifies the token received from the `web` app using `supabase-py` and the Supabase project's JWT secret.
    *   **Video Processing**: Orchestrates the video processing pipeline:
        *   Downloads video from GCS (if necessary, or operates on GCS path).
        *   Uses AI services for transcription, metadata generation, etc.
        *   Stores processed files (thumbnails, VTTs) back to GCS.
    *   **Database Interaction**: Stores and updates job status, generated metadata (text-based), and user-related information in the Supabase database using `supabase-py`.
    *   **WebSocket Communication**: Pushes real-time updates to connected `web` clients about processing progress.

5.  **Overall Communication Flow Example (Video Upload & Processing)**:
    1.  User logs into `web` app using Google (via Supabase TS client). `web` app receives JWT.
    2.  User initiates video upload in `web` app.
    3.  `web` app requests a signed GCS upload URL from `api` (sending JWT).
    4.  `api` (Python) validates JWT, generates signed URL, and returns it to `web`.
    5.  `web` app uploads video file directly to GCS using the signed URL.
    6.  `web` app notifies `api` that upload is complete (sending JWT and GCS path).
    7.  `api` creates a processing job (storing initial metadata in Supabase DB via `supabase-py`).
    8.  `api` starts video processing. As stages complete (e.g., transcription, thumbnail generation):
        *   `api` updates job status in Supabase DB.
        *   `api` sends WebSocket messages to `web` app with progress.
        *   `api` stores generated artifacts (e.g., VTT files, thumbnails) in GCS.
    9.  `web` app UI updates in real-time based on WebSocket messages and allows users to view/edit metadata (fetching/saving via `api`).

This architecture leverages Supabase for robust authentication and database services while keeping your core application logic (`api` and `web`) focused on their respective responsibilities. The `supabase` package aids the frontend, and the `api` uses its Python equivalent for seamless integration.
