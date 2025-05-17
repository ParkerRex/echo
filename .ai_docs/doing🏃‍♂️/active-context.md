# Active Context: Echo Platform (Consolidated)

## Overall Current Focus

The Echo platform development is now focused on validating the end-to-end flow for core features like video upload, processing, and status display, and integrating the backend API with the frontend application. The backend API milestone for video processing is complete, and the next phase is comprehensive testing, frontend integration, and documentation.

---

## Backend (API) - Active Context

### Primary Backend Workstreams:
*   **End-to-End Testing**: Validating the full video processing pipeline from upload via API to final status update, including storage and AI service integration.
*   **Frontend Integration**: Supporting the frontend team in connecting to the new API endpoints for video upload and job status.
*   **Security Audit & Hardening**: Reviewing API endpoints, authentication/authorization, and data handling for security.
*   **Documentation**: Finalizing API documentation (OpenAPI specs), architecture docs, and Memory Bank updates.
*   **Performance & Monitoring**: Planning for performance optimization and observability improvements.

### Current Backend Priorities:
1.  **End-to-End Testing**: Test the video processing API with real uploads and job status queries.
2.  **Frontend Integration**: Ensure the frontend can successfully use the new endpoints for video upload and status.
3.  **Security & Error Handling**: Audit endpoints and improve error handling and resilience.
4.  **Documentation**: Update API docs, Memory Bank, and code comments for maintainability.

### Recent Backend Changes:
*   Implemented a clean architecture with distinct layers (Domain, Application, Adapters, Infrastructure).
*   Developed modular service adapters for storage (GCS), AI (Gemini, etc.), and publishing (YouTube).
*   Created and registered FastAPI endpoints for video upload and job status retrieval, using new Pydantic schemas.
*   Implemented the VideoProcessingService to orchestrate the video processing pipeline.
*   Established router aggregation in `api/endpoints/__init__.py` for scalable API structure.
*   Updated `main.py` to register the aggregated router under `/api/v1/videos`.
*   Significantly refactored and removed legacy monolithic components and outdated structures.
*   Established basic CI/CD pipeline for automated testing and linting.
*   Implemented core data models (VideoModel, VideoJobModel, VideoMetadataModel) and enum (ProcessingStatus) for the video processing pipeline following SQLAlchemy ORM patterns with proper relationships.
*   Standardized on `uv` for Python dependency management throughout the project, replacing the previous venv/conda approach.
*   Improved configuration management by updating service adapters to use the central settings object rather than direct imports.
*   Implemented a unified `FileStorageService` with support for both local filesystem and Google Cloud Storage backends, using async operations.
*   Created a comprehensive AI framework with `AIAdapterInterface` defining a clear contract for AI operations and a concrete `GeminiAdapter` implementation.
*   Added a factory pattern for AI services with the `get_ai_adapter` function that selects the appropriate adapter based on configuration.
*   Fixed the YouTube publishing adapter to properly handle video uploads, captions, and scheduling.
*   Implemented Redis caching system (`lib/cache/redis_cache.py`) for async, settings-driven cache operations.
*   Added utility classes in `lib/utils/` for FFmpeg operations (`ffmpeg_utils.py`), temporary file management (`file_utils.py`), and subtitle generation (`subtitle_utils.py`).
*   Added authentication utilities (`lib/auth/supabase_auth.py`) for Supabase JWT validation and user extraction.
*   Defined custom exceptions (`core/exceptions.py`) for video processing, AI, and FFmpeg errors.
*   Implemented repository layer in `operations/` for `VideoModel`, `VideoJobModel`, and `VideoMetadataModel` with CRUD and update methods.
*   Implemented `get_or_create_user_profile` in `UserService` to ensure a local user profile exists for each authenticated user (Supabase/JWT), using email as the unique identifier and robustly handling missing username/full_name.

### Next Backend Steps:
*   **Immediate**: Conduct E2E and integration testing for the full video processing flow. Support frontend integration and address any issues found during testing.
*   **Upcoming**: Performance optimization, monitoring, and observability improvements. Plan for initial production deployment. Continue documentation and codebase cleanup.

---

## Frontend (Web Application) - Active Context

### Primary Frontend Workstreams:
*   **Core Architecture Setup**: Establishing a scalable and maintainable frontend architecture (e.g., component structure, state management, routing).
*   **Supabase Integration**: Implementing user authentication (Google OAuth via Supabase) and integrating with Supabase for user-specific data.
*   **API Client Implementation**: Developing a robust API client to interact with the FastAPI backend, including handling authentication tokens and error responses.
*   **UI Component Development**: Building key UI components for video upload, dashboard/video list, real-time progress display, and metadata editing.
*   **WebSocket Integration**: Implementing client-side WebSocket handling for real-time updates from the backend.

### Current Frontend Priorities:
1.  **Authentication Flow**: Complete and test the Supabase Google OAuth flow for user sign-up and login.
2.  **Video Upload UI & Logic**: Implement the UI for video upload and the logic to obtain signed URLs from the backend and upload directly to GCS.
3.  **Real-time Dashboard Display**: Develop the dashboard component to display a list of user videos and their real-time processing statuses via WebSockets.
4.  **Basic Project Structure & Tooling**: Finalize project structure, linter/formatter setup, and basic build processes.

### Recent Frontend Changes:
*   Initialized the React (Next.js/Vite - *Confirm choice*) project structure.
*   Set up basic routing and layout components.
*   Started integration with Supabase client for authentication.
*   Sketched out initial designs for dashboard and video upload components.

### Next Frontend Steps:
*   **Immediate**: Finalize and test the video upload component (including GCS direct upload). Implement WebSocket client and connect to dashboard for real-time status updates. Securely store and manage auth tokens.
*   **Upcoming**: Develop the metadata viewing/editing interface. Implement thumbnail selection. Refine UI/UX based on initial internal reviews.

---

## Overall Active Decisions & Considerations

### Architecture & Technology:
*   **Backend**: Python with FastAPI, Clean Architecture (DDD), PostgreSQL (via Supabase), Google Cloud Storage, Celery (or similar for task queuing - *Confirm choice*), AI services (Gemini, OpenAI, AssemblyAI).
*   **Frontend**: React (Next.js/Vite - *Confirm choice*), TypeScript, Supabase client library, Zustand/Redux Toolkit (for state management - *Confirm choice*), Tailwind CSS (or other UI library - *Confirm choice*).
*   **Communication**: RESTful APIs for most client-server interaction, WebSockets for real-time updates.
*   **Database**: Supabase (Postgres) as the primary database for metadata, user information, and application state.

### Implementation Considerations (Platform-wide):
*   **Modularity & Reusability**: Design components (both backend services and frontend UI elements) to be modular and reusable.
*   **Testability**: Emphasize test-driven development (TDD) or behavior-driven development (BDD) where practical. Aim for high test coverage.
*   **Error Handling & User Feedback**: Implement comprehensive error handling on both backend and frontend, providing clear feedback to the user.
*   **Security**: Prioritize security in API design, authentication, data storage, and frontend interactions.
*   **Documentation**: Maintain up-to-date documentation (Memory Bank, code comments, API specs).

## Important Patterns and Preferences (Platform-wide)

*   **Code Organization**: Adherence to Clean Architecture principles on the backend. Well-structured component hierarchy on the frontend. Consistent naming conventions.
*   **Development Workflow**: Feature-branch workflow (Git). Code reviews for all significant changes. CI/CD for automated testing and deployments.
    *   **Backend Python Environment**: All Python virtual environment and package management for `apps/core` must be performed using [`uv`](https://github.com/astral-sh/uv). No other tools (pip, venv, conda, poetry, etc.) are permitted. All dependencies are managed via `pyproject.toml`, and all developers must use `uv` commands for environment creation, dependency installation, and management. This is a permanent, enforced project standard.
    *   **Architecture Rule Enforcement**: All backend code must strictly adhere to the architectural rules defined in `.cursor/rules/architecture.mdc`. This includes layered architecture, domain separation, import order, error handling, and testing requirements. Code reviews must enforce these rules, and any deviations must be explicitly justified and documented in the Memory Bank.
*   **API Design**: RESTful principles, clear and consistent endpoint naming, versioning strategy (if applicable).
*   **State Management (Frontend)**: Deliberate choice of state management solution to handle complexity as the application grows.
*   **Package Management (Backend)**: Use `uv` for Python package management (virtual environments, installation) rather than pip+venv or conda. All dependency installations should be performed via `uv` for consistency and performance.

## Learnings and Insights (Platform-wide)
*   Establishing clear contracts (API schemas, interface definitions) between frontend and backend early is crucial.
*   The Memory Bank system is proving valuable for maintaining context and shared understanding.
*   Balancing development speed with the rigor of clean architecture and comprehensive testing requires ongoing attention.
*   Early integration of services (e.g., Supabase, GCS) helps identify and resolve issues sooner.
*   For external-auth (Supabase/JWT) users, using email as the unique key for user profile creation is robust and reliable; username/full_name should be generated or defaulted if not present in the auth payload.
