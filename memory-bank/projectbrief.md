# Project Brief

**Project Name:** Video Upload + AI Metadata Pipeline

---

## Description

Automates uploading `.mp4` files to YouTube with AI-generated transcripts, titles, chapters, descriptions, and thumbnails using Google Cloud Run, Gemini (Vertex AI), and Imagen3+Pillow. Provides a live-tracking, metadata-rich, and extensible workflow with a powerful, lightweight front end.

---

## Core Goals & Requirements

- **Automate video processing and metadata generation** (transcripts, titles, chapters, descriptions, thumbnails)
- **Integrate with YouTube** for seamless uploads (supporting multiple channels)
- **Live tracking:** Real-time, up-to-date status for each video as it moves through multiple pipeline stages
- **Editable metadata:** Users can edit all YouTube metadata (title, description, tags, chapters, scheduled time, privacy, etc.) and thumbnail prompts before upload
- **Thumbnail generation:** Generate 10 thumbnails per video using Gemini 2.5 Pro (prompted from transcript) + Imagen3 + Pillow; allow user to edit prompts and regenerate
- **Scheduling:** Users can set scheduled publish time for each video
- **Drag-and-drop UI:** Users can drag and drop content to initiate processing
- **No authentication required** for initial local use
- **Scalable, modular, and test-driven architecture**
- **Future enhancements:** Custom thumbnails, tags, Skool post generator, daily AI news generator, etc.

---

## Architecture Overview

- **Backend:**
  - **Google Cloud-native:** Uses Firestore (GCP) for per-video status, metadata, and user-editable fields
  - **Pipeline stages:** Each stage (processing, AI, thumbnail generation, upload, etc.) updates Firestore
  - **Thumbnail generation:** Gemini 2.5 Pro generates prompts from transcript; Imagen3+Pillow generates images; thumbnails stored in GCS, metadata in Firestore
  - **Editable triggers:** User edits in UI update Firestore, triggering pipeline re-runs as needed

- **Frontend:**
  - **React (Vite + TanStack Start):** Fast, client-side UI
  - **Firebase JS SDK:** Direct connection to Firestore for real-time updates and editing
  - **Features:** Drag-and-drop upload, live dashboard, inline metadata editing, thumbnail gallery with prompt editing/regeneration, scheduling controls, channel selection, error/status display
  - **No backend server required for UI** (unless needed for future security/logic)

---

## Example: Firestore Document Structure

```json
{
  "video_id": "abc123",
  "filename": "myvideo.mp4",
  "channel": "Main",
  "current_stage": "Thumbnail Generation",
  "stages_completed": ["Upload", "Transcription", "Metadata"],
  "time_estimates": { "total": "15m", "remaining": "5m" },
  "error": null,
  "metadata": {
    "title": "...",
    "description": "...",
    "tags": ["..."],
    "chapters": [...],
    "scheduled_time": "2025-05-01T10:00:00Z"
  },
  "thumbnails": [
    { "prompt": "...", "url": "...", "status": "complete" }
  ],
  "editable_fields": {
    "description": "...",
    "thumbnail_prompt": "...",
    "scheduled_time": "..."
  }
}
```

---

## Development Phases

1. **Reorganize file tree:** Separate frontend and backend code for clarity and maintainability
2. **Scaffold the React UI:** Vite + TanStack Start, with mock data for all required features
3. **Set up Firestore:** In GCP, configure for real-time status/metadata storage
4. **Connect UI to Firestore:** Use Firebase JS SDK for live updates and editing
5. **Update pipeline:** Write all status/metadata to Firestore at each stage
6. **Integrate thumbnail generation:** Gemini 2.5 Pro for prompt generation, Imagen3+Pillow for image creation
7. **Implement editing triggers:** Backend listens for Firestore changes and triggers pipeline stages as needed
8. **Polish & extend:** Add error handling, multi-channel support, additional metadata fields

---

## File Tree Reorganization (Next Step)

- **Goal:** Organize codebase into clear `frontend/` and `backend/` directories before starting UI work
- **Current:** All backend code in `video_processor/`, no dedicated frontend directory
- **Target:**  
  ```
  /frontend      # React (Vite) app
  /backend       # Python, GCP pipeline, video_processor, etc.
  /docs
  /memory-bank
  /scripts
  /test_data
  ...
  ```

---

**Source:**  
- [README.md](../README.md) (Project Overview, Key Features)  
- [ROADMAP.md](../ROADMAP.md) (Vision, Features)
