# Frontend (Live-Tracking UI)

This directory contains the React (Vite) app for the live-tracking, metadata-rich UI for the Video Upload + AI Metadata Pipeline.

---

## UI Goals

- **Live dashboard:** Real-time status for each video as it moves through pipeline stages
- **Drag-and-drop upload:** Users can drag and drop videos to initiate processing
- **Editable metadata:** Inline editing for all YouTube metadata (title, description, tags, chapters, scheduled time, privacy, etc.)
- **Thumbnail gallery:** View, edit prompts, and regenerate thumbnails (10 per video, generated via Gemini + Imagen3 + Pillow)
- **Scheduling controls:** Set scheduled publish time for each video
- **Channel selection:** Choose which YouTube channel to upload to
- **Error/status display:** Show errors, warnings, and progress for each stage
- **No authentication required** for initial local use

---

## Tech Stack

- **React** (Vite)
- **TanStack Router** (`@tanstack/react-router`)
- **TanStack Query** (`@tanstack/react-query`)
- **Firebase JS SDK** (for direct Firestore integration, to be added)
- **TypeScript** (optional, recommended for future maintainability)

---

## Setup Instructions

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm run dev
   ```

3. **Open the app**
   - Visit [http://localhost:5173](http://localhost:5173) in your browser.

---

## Next Steps

- Scaffold the main dashboard and routes using TanStack Router
- Integrate Firestore for real-time data
- Build out UI components for video list, metadata editing, thumbnail gallery, and upload
- Connect UI actions to backend pipeline via Firestore triggers

---
