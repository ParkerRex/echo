# Tech Context

## Technologies Used

- **Backend:** Python (Flask/FastAPI), ffmpeg for audio extraction, Google Cloud Run for containerized deployment.
- **AI Integration:** Gemini via Vertex AI for transcript, title, chapter, description, and thumbnail generation.
- **Storage & Events:** Google Cloud Storage (GCS) for video and metadata files, Eventarc for event-driven triggers, Firestore for real-time status and metadata.
- **Frontend:** React (Remix), Tailwind CSS, real-time updates via Firestore, API proxying for local development.
- **Containerization:** Docker and Docker Compose for local development and production parity.
- **CI/CD:** GitHub Actions for automated testing, building, and deployment.
- **Testing:** Integration and unit tests, mock GCS for isolated test runs.

## Development Setup

- **Docker-first workflow:** Scripts for starting, stopping, logging, and testing all services.
- **Hot reloading:** Enabled for both frontend and backend.
- **API proxying:** Frontend proxies requests to backend for seamless local development.
- **Service account management:** Credentials stored in `credentials/service_account.json`.

## Technical Constraints

- Must support both daily and main channel content workflows.
- All metadata generation must be automated and scalable.
- Real-time feedback and status updates are required for user experience.
- System must be cloud-native and support horizontal scaling.

## Dependencies

- Python, Flask/FastAPI, ffmpeg, Google Cloud SDK, Vertex AI, React, Remix, Tailwind CSS, Docker, Docker Compose, GitHub Actions.
- Google Cloud services: GCS, Eventarc, Cloud Run, Firestore.
