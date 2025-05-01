# System Patterns

## Architecture Overview

- **Event-Driven Pipeline:** Video uploads to Google Cloud Storage (GCS) trigger processing via Eventarc, which invokes a Cloud Run service.
- **Microservices:** Backend processing is containerized and deployed on Cloud Run for scalability and isolation.
- **Frontend-Backend Separation:** Modern React (Remix) frontend communicates with backend APIs and listens for real-time updates via Firestore.
- **Real-Time Feedback:** Firestore and GCS events drive UI updates, ensuring users see live progress and results.
- **AI Integration:** Metadata (transcripts, titles, chapters, descriptions, thumbnails) is generated using Gemini via Vertex AI.
- **YouTube Automation:** Processed videos and metadata are uploaded to YouTube automatically.

## Key Design Patterns

- **Containerization:** Docker Compose scripts ensure local development matches production.
- **Hot Reloading:** Both frontend and backend support hot reloading for rapid iteration.
- **API Proxying:** Frontend proxies API requests to backend for seamless local development.
- **Testing Isolation:** Mock GCS and test scripts enable safe, repeatable integration tests.
- **CI/CD:** GitHub Actions automate testing, building, and deployment to Cloud Run and Firebase.

## Component Relationships

- **Frontend UI:** Handles upload, progress tracking, and content management.
- **Backend Processor:** Orchestrates video processing, AI calls, and metadata generation.
- **Storage:** GCS for raw and processed files; Firestore for status and metadata.
- **YouTube Uploader:** Publishes finalized videos with all metadata and captions.

## Critical Implementation Paths

- GCS upload → Eventarc trigger → Cloud Run processing → AI metadata generation → Firestore/GCS update → Frontend UI update → YouTube upload.
