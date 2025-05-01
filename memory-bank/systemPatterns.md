# System Patterns

**System Architecture:**  
- **Google Cloud Storage (GCS) is the canonical storage for all video files.**
- **Firestore is used for real-time status and metadata for each video.**
- **Frontend uploads video files directly to GCS using signed URLs for production.**
- **Firebase Storage is NOT used for video files in production.** (Firebase Storage may be used for convenience in local/dev only.)
- Event-driven pipeline using GCS, Eventarc, Cloud Run, and Vertex AI (Gemini)
- Firestore-triggered backend listener for UI-driven updates (metadata edits, thumbnail regeneration)
- Modular video processor for handling uploads, processing, and metadata generation
- Integration with YouTube API for automated uploads

**Key Technical Decisions:**  
- Use of Google Cloud services for scalability and reliability
- Modular design for video processing and uploader components
- Robust error handling and retry logic for API calls
- Test-driven development with comprehensive test suite
- **Adopted a unified, E2E-first testing strategy ([testing-strategy.md](./testing-strategy.md)) to ensure all critical paths are validated in real-world scenarios**
- Firestore as the real-time source of truth for video status and metadata
- Single firebase.js at the root of the frontend for all Firestore config/imports (deduplication, avoids confusion)
- **Adopted signed URL pattern for secure, direct uploads from frontend to GCS.**

**Design Patterns in Use:**  
- Event-driven triggers (GCS upload → Eventarc → Cloud Run)
- Firestore-triggered backend listener (UI action → Firestore → backend listener → pipeline)
- Modular processing (separate modules for audio extraction, AI metadata generation, YouTube upload)
- Integration with external APIs (Gemini, YouTube)
- Use of marker files to prevent duplicate uploads
- All new frontend UI uses shadcn components styled with Tailwind for consistency and rapid development

**Component Relationships:**  
- **Frontend requests a signed URL from the backend and uploads video files directly to GCS (canonical storage for all video files)**
- Eventarc triggers Cloud Run service
- Cloud Run runs video_processor/app.py, which:
  - Extracts audio via ffmpeg
  - Sends audio to Gemini API for metadata generation
  - Writes output files (transcript, chapters, etc.) to GCS
  - Triggers YouTube uploader for final upload
- Firestore "videos" collection stores all video status and metadata
- Frontend UI updates Firestore documents (metadata edits, thumbnail prompts)
- Backend listener (firestore_trigger_listener.py) detects Firestore changes and triggers pipeline stages as needed
- **Firebase Storage is NOT used for video files in production.**

**Critical Implementation Paths:**  
- Video upload (frontend → signed URL → GCS) → Eventarc → Cloud Run → Video Processor → Gemini AI → Output files → YouTube Uploader
- UI action → Firestore document update → Backend listener → Pipeline stage → Firestore update → UI

---

**Architecture Overview (Mermaid):**

```mermaid
flowchart TD
    subgraph User-Driven Path
        A[User edits metadata or thumbnail in UI]
        B[Frontend updates Firestore (metadata/status)]
        C[Backend listener detects change]
        D[Pipeline processes update]
        E[Firestore updated with results]
        F[Frontend receives real-time update]
        G[User sees new status/metadata]
        A --> B --> C --> D --> E --> F --> G
    end

    subgraph Upload Pipeline
        H[Frontend requests signed URL from backend]
        I[Frontend uploads video to GCS (canonical storage) via signed URL]
        J[Eventarc triggers Cloud Run]
        K[Cloud Run runs video_processor]
        L[Gemini AI for metadata]
        M[Output files to GCS]
        N[YouTube uploader]
        H --> I --> J --> K --> L --> M --> N
    end

    %% Explicitly show that Firebase Storage is NOT used for video files
    X[Firebase Storage (not used for video files)]:::disabled

    B -.-> K
    E -.-> F

    classDef disabled fill:#eee,stroke:#aaa,color:#aaa;
```

**Note:**  
- The frontend now uploads videos directly to GCS using signed URLs for production.  
- For local/dev, Firebase Storage may be used for convenience if needed.  
- Firestore is used for status/metadata only.  
- Firebase Storage is not part of the production video pipeline.

**Recent Regression & Restoration:**  
- A recent regression ("video123 header changes") broke Firestore integration and backend triggers. This has been fully restored: frontend now uses a single firebase.js, and backend triggers again respond to UI-driven changes.

**Source:**  
- [README.md](../README.md) (System Architecture, Project Structure)  
- [ROADMAP.md](../ROADMAP.md) (Technical Improvements)
