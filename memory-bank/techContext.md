# Tech Context

**Technologies Used:**  
- **Backend:**  
  - Python 3.9+
  - Docker
  - Google Cloud SDK
  - Google Cloud Run
  - Vertex AI (Gemini)
  - YouTube API
  - Firestore triggers (backend listener for UI-driven updates)
  - pytest (for testing)
  - **google-cloud-storage (for GCS signed URL generation)**
- **Frontend:**  
  - React (Vite)
  - TanStack Start (app framework)
  - TanStack Router (routing)
  - TanStack Query (data fetching/caching)
  - Tailwind CSS (styling)
  - shadcn UI components for all new UI, styled with Tailwind
  - Firebase JS SDK (Firestore integration)
  - Single firebase.js at the root of the frontend for all Firestore config/imports (deduplication)
  - TypeScript (migration in progress)
  - pnpm (package manager)
  - PostCSS (with Tailwind)
  - Vite dev server
  - **Custom UI components:**
    - ProgressSteps: Visualization of processing stages
    - VideoProgressCard: Processing status card for individual videos
    - ProcessingDashboard: Central hub for monitoring all videos in processing
    - ContentEditor: Universal editor for generated text content
    - TitleSelector: UI for selecting and managing AI-generated title options
    - ThumbnailGallery: Interface for managing video thumbnails
    - VideoDetail: Comprehensive view of a processed video with all assets
  - **Cypress/Playwright (for E2E testing, see testing-strategy.md)**

**Development Setup:**  
- **Backend:**  
  - Virtual environment (venv) for Python dependencies  
    - **Location:** `backend/venv/`
    - **Activation:**  
      - macOS/Linux: `source backend/venv/bin/activate`
      - Windows: `backend\venv\Scripts\activate`
    - **Install dependencies:**  
      - `pip install -r backend/requirements.txt` (after activating venv)
  - **Refactored backend structure:**  
    ```
    backend/
      ├── deploy.sh
      ├── docker-compose.yml
      ├── Dockerfile
      ├── requirements.txt
      ├── scripts/
      ├── test_data/
      ├── tests/
      │   ├── unit/              # Unit tests
      │   ├── integration/       # Integration tests
      │   ├── e2e/               # End-to-end tests
      │   ├── conftest.py        # Common test fixtures
      │   ├── README.md          # Testing guide
      │   └── outdated/          # Legacy tests for reference
      ├── venv/
      └── video_processor/
          ├── api/               # API endpoints and controllers
          │   ├── controllers.py
          │   ├── routes.py
          │   └── schemas.py
          ├── app.py             # Main entry point
          ├── config/            # Configuration management
          │   ├── environment.py
          │   └── settings.py
          ├── core/              # Core domain logic
          │   ├── models/        # Domain models
          │   └── processors/    # Processing components
          ├── services/          # External service integrations
          │   ├── storage/       # Storage services (GCS, local)
          │   ├── ai/            # AI model services
          │   └── youtube/       # YouTube integration
          ├── utils/             # Shared utilities
          │   ├── error_handling.py
          │   ├── file_handling.py
          │   └── logging.py
          └── README.md          # Module documentation
    ```
  - **Rules for running backend scripts and Flask app:**
    - Always activate the venv before running any Python scripts.
    - To run the Flask app for local development:
      ```
      GCS_UPLOAD_BUCKET=automations-youtube-videos-2025 \
      GOOGLE_APPLICATION_CREDENTIALS=/Users/parkerrex/Developer/Automations/@credentials/service_account.json \
      python app.py
      ```
      (Run from `backend/video_processor/` directory. Adjust credentials path as needed.)
    - Service account credentials are stored in `@credentials/service_account.json`.
    - The canonical GCS bucket for production video uploads is `automations-youtube-videos-2025`.
    - All environment variables must be set explicitly if not using Docker.
  - Docker for containerization and local testing
  - Service account credentials stored in @credentials/
  - **GCS buckets for video storage and processing (canonical storage for all video files in production)**
  - Firestore "videos" collection for real-time status and metadata
  - Environment variables for configuration (including `GCS_UPLOAD_BUCKET`)
  - **/api/gcs-upload-url endpoint for generating signed upload URLs**
- **Frontend:**  
  - Vite dev server for local development (`pnpm dev`)
  - All frontend code in `/frontend/`
  - TanStack Start for app structure and routing
  - Tailwind CSS for utility-first styling
  - Firebase JS SDK for real-time Firestore integration
  - **Uploads video files directly to GCS using signed URLs for production.**
  - **Firebase Storage is used for uploads only in local/dev mode for convenience, if needed.**
  - pnpm for dependency management
  - TypeScript migration planned (currently mixed JS/TS)
  - PostCSS for CSS processing

**Technical Constraints:**  
- Cloud-native, scalable, and secure
- Support for multiple video and audio formats
- Secure handling of credentials and API keys
- Integration with Google Cloud and YouTube APIs
- **GCS is the only supported storage for video files in production.**
- **Frontend uploads directly to GCS using signed URLs for production.**
- **Firestore is used for metadata/status only.**
- **Firebase Storage is NOT used for video files in production.**
- Frontend must support real-time Firestore updates and inline editing
- No authentication required for initial local use
- Fast, modern, and maintainable UI
- **Backend follows modular architecture with dependency injection**
- **Services are interface-based to allow multiple implementations**

**Dependencies:**  
- **Backend:**  
  - Python packages listed in requirements.txt
  - Google Cloud libraries (storage, secretmanager, etc.)
  - YouTube API client libraries
  - ffmpeg for audio extraction
- **Frontend:**  
  - React, Vite, TanStack Start, TanStack Router, TanStack Query
  - Tailwind CSS, PostCSS
  - Firebase JS SDK
  - pnpm
  - TypeScript (in progress)

**Tool Usage Patterns:**  
- **Backend:**  
  - Dependency injection for service composition and testability
  - Interface-based service design with multiple implementations (e.g., GCS vs local storage)
  - Centralized configuration management with environment variable validation
  - Specialized error handling with custom exceptions and retry mechanisms
  - Structured logging with consistent format
  - Automated test fixtures for mock services and test data generation
  - Firestore trigger listener (backend/video_processor/firestore_trigger_listener.py) for automated backend processing in response to UI actions
  - `/api/gcs-upload-url` endpoint for generating signed upload URLs for GCS
  - Simulation script (backend/scripts/simulate_firestore_update.py) for testing Firestore-triggered flows
  - Scripts for local and Docker-based testing (scripts/)
  - Modular test suite using pytest
  - Deployment via deploy.sh and Docker Compose
- **Frontend:**  
  - Vite dev server for rapid local development
  - TanStack Router for route management
  - TanStack Query for Firestore data fetching/caching
  - Tailwind for styling
  - shadcn UI components for all new UI, styled with Tailwind
  - Firebase JS SDK for Firestore integration
  - Single firebase.js at the root of the frontend for all Firestore config/imports (deduplication, avoids confusion)
  - Inline editing and real-time updates for video metadata and thumbnails
  - **Custom UI components for enhanced user experience:**
    - ProgressSteps component for visualizing processing workflow
    - Video processing dashboard with real-time status updates
    - Title selection interface with voting system for AI-generated titles
    - Thumbnail gallery with preview, selection, and regeneration options
    - Content editor for managing transcripts, subtitles, and chapters
    - Tabbed interface for video details with real-time updates
  - **Real-time progress tracking with visual feedback for all processing stages**
  - **Uploads video files directly to GCS using signed URLs for production (secure, credentials never exposed to frontend).**
  - **E2E tests use dedicated test GCS buckets and Firestore collections to avoid polluting production data (see testing-strategy.md)**

**Recent Regression & Restoration:**  
- A recent regression ("video123 header changes") broke Firestore integration and backend triggers. This has been fully restored: frontend now uses a single firebase.js, and backend triggers again respond to UI-driven changes. All new UI uses shadcn components styled with Tailwind.

**Backend Architecture Principles:**
- **Separation of Concerns**: Clear boundaries between API, core logic, and external services
- **Dependency Injection**: Services receive dependencies rather than creating them
- **Interface-Based Design**: Components work with abstractions rather than concrete implementations
- **Testability**: All components are designed to be easily tested in isolation
- **Configuration Management**: Environment variables and settings centralized
- **Error Handling**: Consistent error handling with specialized exceptions and retry mechanisms
- **Logging**: Structured logging with consistent format throughout the application

**Source:**  
- [README.md](../README.md) (Prerequisites, Setup, Project Structure)  
- [ROADMAP.md](../ROADMAP.md) (Technical Improvements)