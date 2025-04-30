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
  - **Cypress/Playwright (for E2E testing, see testing-strategy.md)**

**Development Setup:**  
- **Backend:**  
  - Virtual environment (venv) for Python dependencies
  - Docker for containerization and local testing
  - Service account credentials stored in @credentials/
  - GCS buckets for video storage and processing
  - Firestore "videos" collection for real-time status and metadata
  - Environment variables for configuration
- **Frontend:**  
  - Vite dev server for local development (`pnpm dev`)
  - All frontend code in `/frontend/`
  - TanStack Start for app structure and routing
  - Tailwind CSS for utility-first styling
  - Firebase JS SDK for real-time Firestore integration
  - pnpm for dependency management
  - TypeScript migration planned (currently mixed JS/TS)
  - PostCSS for CSS processing

**Technical Constraints:**  
- Cloud-native, scalable, and secure
- Support for multiple video and audio formats
- Secure handling of credentials and API keys
- Integration with Google Cloud and YouTube APIs
- Frontend must support real-time Firestore updates and inline editing
- No authentication required for initial local use
- Fast, modern, and maintainable UI

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
  - Firestore trigger listener (backend/video_processor/firestore_trigger_listener.py) for automated backend processing in response to UI actions
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
  - **E2E tests use dedicated test GCS buckets and Firestore collections to avoid polluting production data (see testing-strategy.md)**

**Recent Regression & Restoration:**  
- A recent regression ("video123 header changes") broke Firestore integration and backend triggers. This has been fully restored: frontend now uses a single firebase.js, and backend triggers again respond to UI-driven changes. All new UI uses shadcn components styled with Tailwind.

**Source:**  
- [README.md](../README.md) (Prerequisites, Setup, Project Structure)  
- [ROADMAP.md](../ROADMAP.md) (Technical Improvements)
