# System Patterns: Echo Platform (Consolidated)

---

## Backend Architecture Rule Enforcement

**All backend code must strictly adhere to the architectural rules defined in `.cursor/rules/architecture.mdc`. This file is the canonical source for backend architecture, code organization, and quality standards. Code reviews and all development work must enforce these rules. Any deviations must be explicitly justified and documented in the Memory Bank.**

## Overall Architecture Philosophy

The Echo platform is designed as a distributed system with a clear separation between the backend API (responsible for processing, AI integration, and core logic) and the frontend web application (responsible for user interaction and presentation). Communication primarily occurs via RESTful APIs and WebSockets for real-time updates.

```mermaid
graph TD
    User[User] -- HTTPS --> Frontend[Frontend Web App (React/Next.js)]
    Frontend -- REST API / WebSockets --> BackendAPI[Backend API (FastAPI)]

    BackendAPI -- Integrates with --> AIServices[AI Services (Gemini, OpenAI, etc.)]
    BackendAPI -- Integrates with --> CloudStorage[Cloud Storage (GCS)]
    BackendAPI -- Integrates with --> Database[Database (Supabase/Postgres)]
    BackendAPI -- Integrates with --> Publishing[Publishing Platforms (YouTube)]

    Frontend -- Direct Upload --> CloudStorage
    Frontend -- Auth/Data --> Database
```

---

## Backend (API) System Patterns

### Recent Infrastructure & Utility Patterns

- **Router Aggregation Pattern**: All API routers are aggregated and re-exported in a single `api/endpoints/__init__.py` file as `router`. This enables scalable API structure, simplifies router registration in `main.py`, and supports future expansion with minimal changes to the app entrypoint.
- **Async Redis Caching**: Use of an async `RedisCache` class (`lib/cache/redis_cache.py`) for non-blocking cache operations, settings-driven, with simple get/set interface. Used for AI adapter caching and other backend caching needs.
- **Utility Classes**: All infrastructure utilities (FFmpeg, file handling, subtitle generation) are implemented as stateless classes in `lib/utils/`, with only static methods and no side effects. This ensures testability and reusability.
- **Authentication Utilities**: Supabase JWT validation and user extraction are handled by a dedicated module (`lib/auth/supabase_auth.py`) using Pydantic models and FastAPI dependencies.
- **Custom Exception Hierarchy**: All service and utility errors are handled via a custom exception hierarchy in `core/exceptions.py`, with base and specialized error types for video processing, AI, and FFmpeg.
- **Repository Pattern**: All data access for core models is handled by repository classes in `operations/`, each with static CRUD and update methods, accepting a SQLAlchemy Session as the first argument. No business logic is present in repositories.

### Core Architecture: Clean Architecture
The backend adheres to Clean Architecture principles, ensuring a separation of concerns and promoting maintainability, testability, and scalability. The layers are:

1.  **Domain Layer**: Contains core business entities (e.g., `Video`, `Job`, `Metadata`), value objects, domain events, and business rules. It has no dependencies on outer layers.
    *   *Key Patterns*: Rich Domain Models, Value Objects, Domain Events.
2.  **Application Layer**: Orchestrates use cases and defines service interfaces (e.g., `VideoProcessorService`, `StorageInterface`, `AIInterface`). It depends only on the Domain layer.
    *   *Key Patterns*: Application Services, Port (Interface) definitions.
3.  **Adapters Layer**: Implements the interfaces defined by the Application layer, connecting to external systems or providing specific implementations. Examples include GCS storage adapter, Gemini AI adapter.
    *   *Key Patterns*: Adapter Pattern, concrete implementations of Application Ports.
4.  **Infrastructure Layer**: Provides technical capabilities, framework-specific code (FastAPI setup, routing, schemas), configuration, dependency injection container, and actual external system integrations (database connections, API clients for external services).
    *   *Key Patterns*: Dependency Injection Container, Repository Implementations, API Route Handlers, Configuration Management.

```mermaid
graph LR
    subgraph BackendAPI
        direction LR
        Infrastructure[Infrastructure Layer (FastAPI, GCS Client, DB Client)] -- Implements/Uses --> Adapters
        Adapters[Adapters Layer (GCSStorageAdapter, GeminiAIAdapter)] -- Implements --> Application
        Application[Application Layer (VideoService, IStorage)] -- Uses --> Domain
        Domain[Domain Layer (Video, Job, Metadata)]
    end
```

### Key Backend Design Patterns:
*   **Repository Pattern**: Abstracts data persistence operations. Interfaces are defined in the Application (or Domain) layer, with implementations in the Infrastructure layer (e.g., `SupabaseJobRepository`).
*   **Dependency Injection**: Used extensively to decouple components. A DI container (e.g., `punq`) is configured in the Infrastructure layer to manage service lifecycles and inject dependencies into Application services and API controllers.
*   **Adapter Pattern**: For all external service integrations (storage, AI, publishing), isolating the core application from specific third-party library changes. Examples include:
    * `FileStorageService`: Provides a unified interface for both local filesystem and Google Cloud Storage operations.
    * `AIAdapterInterface` and `GeminiAdapter`: Abstract AI service operations behind a consistent interface.
    * `PublishingInterface` and `YouTubeAdapter`: Isolate publishing operations from specific platforms.
*   **Factory Pattern**: Used to create appropriate service instances based on configuration. Examples:
    * `get_ai_adapter()`: Creates the appropriate AI adapter based on available API keys.
    * `get_file_storage_service()`: Provides a singleton FileStorageService instance.
*   **Domain-Driven Design (DDD)**: Emphasis on rich domain models, value objects, and clearly defined bounded contexts (though the current system is largely a single primary context).
*   **SQLAlchemy ORM**: Leveraging SQLAlchemy for database model definition and querying, using `Base` declarative models, relationship mappings, and type-annotated columns. Models follow a convention of suffixing with `Model` (e.g., `VideoModel`, `VideoJobModel`) to distinguish them from domain entities.
*   **Centralized Configuration**: Using a Pydantic `Settings` class to load and validate environment variables, with a singleton instance accessible throughout the application via imports.
*   **Asynchronous Operations with Thread Pooling**: For I/O-bound operations (file storage, AI API calls), using async/await patterns with ThreadPoolExecutor to avoid blocking the event loop.
*   **Task Queuing (Conceptual - e.g., Celery/RabbitMQ/Cloud Tasks)**: For long-running video processing tasks, a task queue will be essential to handle background processing, retries, and scalability. (Specific choice to be finalized).

### Backend Component Relationships & Flows:

*   **API Request Flow (FastAPI)**:
    `HTTP Request` -> `FastAPI Router` -> `Authentication/Authorization Middleware` -> `Dependency Injection (resolves services)` -> `Application Service Method` -> `(Optional) Repository/Adapters` -> `Domain Logic` -> `Response Mapping (Pydantic Schemas)` -> `HTTP Response`.
*   **Video Processing Flow (Simplified)**:
    1.  Client (Frontend) requests a signed URL from Backend API.
    2.  Client uploads video directly to Cloud Storage (GCS).
    3.  Client notifies Backend API of successful upload, triggering a processing job.
    4.  Backend API (potentially via a task queue) initiates `VideoProcessorService`.
    5.  `VideoProcessorService` uses:
        *   `FileStorageService` to access the video, supporting both local and GCS backends.
        *   `AIAdapterInterface` implementations (selected via factory) for text generation, content analysis, and transcription.
        *   `MetadataService` to generate and store metadata.
    6.  Job status is updated in the Database (`JobRepository`).
    7.  Real-time updates sent to client via WebSockets.
    8.  (Optional) `PublishingAdapter` distributes content to platforms like YouTube.

### Backend Module Structure (Illustrative - New Structure):
```
apps/core/
├── models/                 # SQLAlchemy ORM models
│   ├── enums.py            # Enum definitions (e.g., ProcessingStatus)
│   ├── video_model.py      # Video entity model
│   ├── video_job_model.py  # Job processing model
│   └── video_metadata_model.py # Video metadata model
├── lib/                    # Core libraries and utilities
│   ├── ai/                 # AI service adapters
│   ├── database/           # Database connection, session management
│   ├── storage/            # Storage service adapters
│   ├── utils/              # Utility functions and helpers
│   └── cache/              # Caching mechanisms
├── operations/             # Repository implementations
├── services/               # Service layer orchestration
├── api/                    # FastAPI routes and schemas
│   ├── endpoints/          # API route handlers
│   └── schemas/            # Pydantic schemas for API
├── core/                   # Core application setup
│   ├── config.py           # Configuration management
│   └── exceptions.py       # Application exceptions
├── alembic/                # Database migrations
└── main.py                 # FastAPI app instantiation
```

---

## Frontend (Web Application) System Patterns

### Core Architecture: Modern React SPA
The frontend is a Single-Page Application (SPA) built with React (likely Next.js or Vite with TanStack Router, choice to be confirmed and standardized). Focus is on a responsive user experience, efficient state management, and real-time communication with the backend.

```mermaid
graph TD
    subgraph FrontendWebApp
        direction TB
        Browser[Browser]
        Browser -- Interacts --> UILayer[UI Layer (React Components - shadcn/ui, Custom)]
        UILayer -- Uses --> Routing[Routing (TanStack Router)]
        UILayer -- Manages/Uses --> StateManagement[State Management (TanStack Query, Zustand/Context)]
        StateManagement -- Interacts --> APIServices[API Services Layer]
        APIServices -- HTTP/REST --> BackendAPIClient[Backend API Client (axios/fetch)]
        APIServices -- WebSocket --> WebSocketClient[WebSocket Client]
        APIServices -- Auth/Data --> SupabaseClient[Supabase Client]
    end
```

### Key Frontend Technical Decisions & Patterns:
1.  **Component-Based Architecture**: UI built using reusable React components, potentially leveraging a UI library like `shadcn/ui` for styling and pre-built elements.
2.  **Routing**: Client-side routing managed by a library like `TanStack Router` for navigation without full page reloads.
3.  **State Management**:
    *   **Server State**: `TanStack Query` for managing data fetched from the API, including caching, background updates, and optimistic updates.
    *   **Client/UI State**: Local component state (`useState`, `useReducer`) or a global client state solution (e.g., `Zustand`, `Context API`, or `Redux Toolkit` if complexity warrants) for UI-specific state not tied to the server.
4.  **Authentication**: Integration with Supabase for Google OAuth. JWT tokens obtained from Supabase/backend will be managed by the API client (e.g., stored securely and attached to requests).
5.  **Real-time Updates**: A dedicated WebSocket client (`use-app-websocket` hook or similar) to connect to the FastAPI backend, receive real-time messages, and update relevant state (likely by invalidating or directly updating `TanStack Query` cache).
6.  **Direct-to-Cloud Uploads**: For video uploads, the frontend will request a signed URL from the backend and then upload the file directly to GCS, reducing backend server load.
7.  **Custom Hooks (`/hooks`)**: Encapsulating reusable logic, such as WebSocket connection management, API call patterns, or device detection (`useMobile`).
8.  **TypeScript**: For static typing, improving code quality and maintainability.

### Frontend Component Relationships & Structure (Illustrative):
*   **`src/routes/`**: Components defining application pages/views, responsible for fetching data (often via `TanStack Query` loaders) and composing feature-specific components.
*   **`src/components/features/`** (or `src/components/video/`, `src/components/auth/` etc.): Components that implement specific application features (e.g., `VideoProcessingDashboard`, `MetadataEditor`). They combine UI elements and business logic relevant to that feature.
*   **`src/components/ui/`**: Reusable, presentational UI components (e.g., buttons, modals, cards from `shadcn/ui` or custom-built).
*   **`src/components/shared/`**: Common layout components like `Navbar`, `Footer`, `Container` used across multiple routes.
*   **`src/lib/` or `src/services/`**: API client setup, Supabase client instance, utility functions.
*   **`src/hooks/`**: Custom React hooks for shared logic.
*   **`src/store/`** (if using global state manager): State management configuration.

### Critical Frontend Implementation Paths:
1.  **Authentication Flow**:
    `LoginPage` -> `Supabase Google OAuth Redirect` -> `Callback Handling` -> `Store JWT/Session` -> `Authenticated API Client` -> `Protected Routes`.
2.  **Video Upload Flow**:
    `Upload UI (e.g., Dropzone)` -> `Frontend requests Signed URL (API call)` -> `Backend returns Signed URL` -> `Frontend uploads directly to GCS` -> `Frontend notifies Backend of success (API call)` -> `Backend initiates processing` -> `WebSocket status updates to Frontend`.
3.  **Real-time Dashboard Update Flow**:
    `Dashboard Mounts` -> `Establish WebSocket Connection (useAppWebSocket)` -> `Backend sends processing update message` -> `WebSocket client receives message` -> `Update TanStack Query Cache (invalidate or setData)` -> `Components re-render with new data`.
4.  **Metadata Editing Flow**:
    `VideoDetailPage loads (fetches metadata via TanStack Query)` -> `Display metadata in EditorForm` -> `User edits form` -> `Form submission (API call to save metadata)` -> `On success, invalidate TanStack Query cache for metadata` or `Optimistically update local cache`.

---

## Cross-Cutting Concerns & Platform-Wide Patterns

*   **Error Handling**: Consistent error handling strategies for both backend (domain-specific exceptions, FastAPI error handlers, structured JSON error responses) and frontend (displaying user-friendly messages, logging errors).
*   **Logging**: Structured logging on the backend. Frontend error reporting to a service like Sentry (optional).
*   **Validation**: Pydantic for backend request/response validation. Form validation libraries (e.g., `react-hook-form`, `Zod`) on the frontend.
*   **Security**: HTTPS, secure JWT handling, input sanitization, protection against common web vulnerabilities (OWASP Top 10), proper RLS policies in Supabase.
*   **Configuration Management**: Environment variables for backend (using Pydantic settings) and frontend (e.g., `VITE_` prefixed env vars).
*   **Package Management**: Backend uses `uv` for Python dependency management, virtual environment creation, and dependency installation. Frontend uses `pnpm` for Node.js package management.
*   **API Design**: Adherence to RESTful principles, clear and consistent endpoint naming, use of HTTP status codes. OpenAPI/Swagger for backend API documentation.
