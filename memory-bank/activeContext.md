# Active Context

**Current Work Focus:**  
- All main frontend routes (Dashboard, Video Detail, Upload, Settings) have been systematically audited and updated for:
  - Firestore integration with real-time updates (`onSnapshot`)
  - Inline editing and thumbnail management (Video Detail)
  - Consistent use of shadcn UI components and Tailwind styling
  - Robust upload flow using GCS signed URLs and Firestore doc creation (Upload)
  - Settings page structure for future extensibility
- The frontend now provides a robust, maintainable, and user-friendly foundation for further testing and enhancements.
- Backend Firestore trigger integration remains operational and ready for UI-driven updates.
- All tasks tracked in progress.md, including YouTube uploader subtasks.
- **FIXED: Frontend-backend API proxy/routing for `/api/gcs-upload-url` now properly forwards requests to the backend Flask app.**
- **ADDED: `start-services.sh` and `stop-services.sh` scripts to easily manage development environment.**

**Recent Changes:**  
- Audited and polished all main frontend routes for Firestore integration, real-time updates, and UI/UX consistency:
  - Dashboard: Real-time video list, navigation, shadcn Card components
  - Video Detail: Inline metadata editing, thumbnail prompt editing/regeneration, real-time updates, shadcn UI
  - Upload: Drop zone, GCS signed URL upload, Firestore doc creation, shadcn Card UI
  - Settings: Now uses shadcn Card and Tailwind, structured for future settings
- Fixed missing imports and TypeScript errors in Upload route after UI update
- No changes to backend or architecture; frontend implementation patterns are now fully aligned with project standards
- **Added Vite server proxy configuration to app.config.ts to properly forward `/api/*` requests to the backend Flask app running on port 8080, fixing the upload functionality.**
- **Created development scripts for improved workflow:**
  - `start-services.sh`: Activates Python venv, starts backend Flask app, then starts frontend dev server
  - `stop-services.sh`: Gracefully stops both backend and frontend servers

**Next Steps:**  
- ~~**URGENT:** Fix frontend-backend API proxy/routing for `/api/gcs-upload-url` so the upload page can reach the backend Flask app (currently running on port 8080).~~ **FIXED**
- Begin E2E and integration test implementation for all main user flows (upload, edit, thumbnail regeneration, real-time updates)
  - Use test GCS bucket and Firestore collection for E2E tests
  - Add cleanup logic for test data after E2E runs
  - Document and automate E2E test flow (local and CI)
- Continue TypeScript migration for any remaining JS files
- Add/verify component tests for upload, metadata editing, thumbnail regeneration
- Track progress in progress.md and update memory bank as needed

**Active Decisions and Considerations:**  
- GCS is the canonical storage for video files.
- Frontend uploads directly to GCS using signed URLs for production.
- Firebase Storage is NOT used for video files in production (local/dev only if needed).
- Firestore (GCP-native) is the source of truth for all video status and metadata.
- All main UI routes now use Firestore `onSnapshot` for real-time updates, supporting a true event-driven workflow.
- All tasks tracked at a granular level in progress.md.
- Adopted clear frontend/backend split for maintainability and clarity.
- Vite + React + TanStack stack for fast, modern, client-side UI.
- No authentication required for initial local use.
- Prioritize features by impact and ease (see ROADMAP.md ICE scores).
- Maintain high test coverage and modularity.
- **Use Vite server proxy for frontend-backend API communication in development.**
- **Streamlined development workflow with scripts to manage services consistently.**

**Learnings and Project Insights:**  
- Storage architecture clarified: GCS for video files, Firestore for metadata/status, Firebase Storage not used for video in production.
- Signed URL pattern enables secure, direct uploads from frontend to GCS without exposing credentials.
- Backend-driven canonical URLs: Returning the canonical GCS URL from the backend eliminates frontend config drift and ensures all Firestore records are valid and production-ready.
- Real-time UI: Using Firestore `onSnapshot` for all main routes ensures the UI is always in sync with backend and pipeline changes, supporting a true event-driven workflow.
- Modular, event-driven design enables easy extension and robust automation.
- Comprehensive testing is critical for reliability in a cloud-native pipeline.
- TypeScript type safety: Even with a JS-based Firebase config, a dedicated `.d.ts` file ensures type safety and prevents integration errors.
- **Vite development server proxying is essential for local development when frontend needs to communicate with a separate backend service.**
- **Running the backend requires properly activating the Python virtual environment from the right directory.**

---
