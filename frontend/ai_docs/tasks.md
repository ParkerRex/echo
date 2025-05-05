
# FRONTEND - PRODUCT REQUIREMENTS DOCUMENT (PRD) - V3

## 1. Overview

This Product Requirements Document (PRD) outlines the specifications for the frontend application of the Video Processing Pipeline system. The frontend provides users (primarily Content Creators) with an interface to authenticate using Google via Supabase, upload videos directly to Google Cloud Storage (GCS), monitor processing progress in real-time via FastAPI WebSockets, review and edit AI-generated metadata (including selecting a final thumbnail from multiple generated options), and manage the video publishing workflow. This document focuses on the core requirements for migrating the frontend to integrate seamlessly with the backend FastAPI API and Supabase (for authentication and non-file metadata persistence), removing legacy Firebase dependencies (e.g., `frontend/firebase.ts`) and unused example code (e.g., various files under `frontend/src/routes/posts*`, `frontend/src/routes/users*`).

## 2. Project goals

### 2.1 Primary goals

-   Provide an intuitive user interface, evolving from existing components (e.g., `frontend/src/components/video/*`, `frontend/src/components/shared/*`) for interacting with the video processing pipeline, authenticated via Supabase Google OAuth.
-   Integrate seamlessly with Supabase for user authentication and session management, utilizing the existing client setup in `db/supabase/clients/client.ts` for browser contexts and `db/supabase/clients/server.ts` for server-side operations.
-   Implement video uploads directly to GCS using signed URLs from the backend, adapting existing upload UI components like `frontend/src/components/ui/dropzone.tsx`.
-   Display real-time updates on video processing status and generated metadata using FastAPI WebSockets, updating components like `frontend/src/components/video/processing-dashboard.tsx` and `frontend/src/components/video/video-detail.tsx`.
-   Allow users to review and edit generated video metadata (fetching/saving via backend API), including selecting a final thumbnail from a gallery (e.g., a new or adapted `frontend/src/components/video/thumbnail-gallery.tsx`), using editor components like `frontend/src/components/video/content-editor.tsx`.
-   Ensure secure communication between the frontend, Supabase (auth), GCS (uploads), and the backend FastAPI API (metadata, job control, signed URLs, WebSocket).
-   Completely remove all Firebase dependencies and listeners (from `frontend/package.json`, `frontend/firebase.ts`, etc.).
-   Remove unused example routes and components related to 'posts' and 'users', moving essential examples to `docs/frontend/examples/`.
-   Maintain a responsive and modern user experience using React (via `frontend/src/client.tsx`), TanStack Router (configured in `frontend/src/router.tsx`), and shadcn/ui components (from `frontend/src/components/ui/*`).

### 2.2 Success metrics

-   Successful user authentication via Supabase Google OAuth flow.
-   Successful video uploads to GCS via signed URLs.
-   Real-time status updates appear within 1 second of backend events via WebSockets.
-   API interactions (metadata fetch/update, signed URL request) complete within 500ms (p95) after authentication, measured using API client (`frontend/src/api.ts` or replacement).
-   User satisfaction score of 4.5/5 or higher for interface usability, authentication, upload, and real-time feedback.
-   Successful implementation and stability of FastAPI WebSocket connection and message handling.
-   Backend API endpoints are correctly protected and accessible using the Supabase JWT passed from the frontend.
-   Zero data inconsistencies reported related to real-time updates vs. API fetches.
-   Complete removal of Firebase SDK and example routes/components confirmed via code review and dependency analysis.

## 3. Frontend architecture

The frontend is built using:

-   **Framework:** React (with Vite, entry point `frontend/src/client.tsx`)
-   **Routing:** TanStack Router (setup in `frontend/src/router.tsx`, routes defined under `frontend/src/routes/`)
-   **UI Components:** shadcn/ui (`frontend/src/components/ui/*`) & custom application components (e.g., `frontend/src/components/video/*`, `frontend/src/components/shared/*`)
-   **Authentication:** Supabase client library (`@supabase/supabase-js`) via `db/supabase/clients/client.ts` for Google OAuth flow and session management in browser contexts, and `db/supabase/clients/server.ts` for server-side operations.
-   **API Communication:** Custom API client wrapper (likely evolving `frontend/src/api.ts`) sending the Supabase JWT to the backend FastAPI API.
-   **Database Interaction (Client-side):** Minimal. Primarily interacts with the backend API. Direct Supabase client interaction via `db/supabase/clients/client.ts` limited to auth state.
-   **File Storage:** Interaction with GCS via signed URLs obtained from the backend API for uploads.
-   **Real-time:** Native WebSocket API connecting to the backend FastAPI WebSocket endpoint, managed via a custom hook (`frontend/src/hooks/use-app-websocket.ts`).
-   **State Management:** TanStack Query for server state caching/synchronization (backend API data) and local component state for UI elements like temporary thumbnail selection.

## 4. Key features & requirements

### 4.1 Core user interface & functionality

**REQ-FE-001: User Authentication via Supabase**
-   **Priority:** High - Foundational for application access.
-   Adapt existing login UI to provide a "Login with Google" button by creating a dedicated component (`frontend/src/components/auth/GoogleLoginButton.tsx`).
-   Initiate the Supabase Google OAuth flow using the Supabase client configured in `db/supabase/clients/client.ts`.
-   Handle the OAuth callback and manage the Supabase session.
-   Obtain the Supabase JWT upon successful login.
-   Implement logic (within API client `frontend/src/api.ts`) to attach the Supabase JWT to authenticated requests made to the backend FastAPI API.
-   Implement logout functionality (in navbar component `frontend/src/components/shared/navbar.tsx`) using `supabase.auth.signOut()`, clearing local session state and redirecting.
-   Protect routes requiring authentication using TanStack Router features by creating a dedicated layout component (`frontend/src/routes/_authenticated.tsx`), checking for an active Supabase session.
-   Handle Supabase session changes globally (in `frontend/src/routes/__root.tsx`) using `supabase.auth.onAuthStateChange`.

**REQ-FE-002: Video Upload Interface (Direct GCS)**
-   Adapt `frontend/src/components/ui/dropzone.tsx` within an authenticated view (e.g., `frontend/src/routes/dashboard.tsx`) for users to select video files.
-   Implement client-side validation for file type and size.
-   Request a GCS signed upload URL from the backend API.
-   Perform a PUT request directly to the GCS signed URL, displaying upload progress using `frontend/src/components/ui/progress.tsx`.
-   Upon successful GCS upload, notify the backend API to initiate processing.
-   Implement standardized error handling for upload failures.
-   Display success/error messages using `frontend/src/components/ui/use-toast.ts`.

**REQ-FE-003: Processing Dashboard**
-   Refactor the existing dashboard route (`frontend/src/routes/dashboard.tsx`) and the component (`frontend/src/components/video/processing-dashboard.tsx`).
-   Fetch and display a list/grid of the authenticated user's video processing jobs via the backend API using TanStack Query.
-   Use card components (`frontend/src/components/video/video-progress-card.tsx`) to show key information: thumbnail, title, status, timestamp.
-   Establish a WebSocket connection upon dashboard load via the `use-app-websocket.ts` hook.
-   Update job statuses and potentially thumbnails/titles in real-time via WebSocket messages, synchronizing with TanStack Query cache through cache updates or invalidation.
-   Handle loading states with `frontend/src/components/ui/skeleton.tsx` and empty states.
-   Allow navigation to detail view (`frontend/src/routes/video.$videoId.tsx`).
-   Implement pagination (`frontend/src/components/ui/pagination.tsx`) for large job lists.

**REQ-FE-004: Video Detail View**
-   Refactor the existing video detail route (`frontend/src/routes/video.$videoId.tsx`) and component (`frontend/src/components/video/video-detail.tsx`).
-   Fetch detailed job information via the backend API using TanStack Query.
-   Display video details and overall job status.
-   Display detailed processing stage statuses using appropriate UI components, aligning with backend processing stages.
-   Subscribe to WebSocket updates for this `job_id` using the `use-app-websocket.ts` hook.
-   Process incoming WebSocket messages and update the TanStack Query cache accordingly.
-   Display generated metadata as available.
-   Display a gallery of *all* generated thumbnail URLs.
-   Provide navigation/links to the metadata editor section (within the same component or separate).
-   Display error messages clearly with standardized error handling.

**REQ-FE-005: Metadata Editor & Thumbnail Selection**
-   Integrate editing capabilities within the detail view by adapting `frontend/src/components/video/content-editor.tsx`.
-   Provide UI sections using standard inputs (`frontend/src/components/ui/input.tsx`, `frontend/src/components/ui/textarea.tsx`, etc.) for editing title, description, tags.
-   Provide sections for viewing/copying transcript, subtitles, chapters.
-   Implement or adapt a thumbnail gallery component (`frontend/src/components/video/thumbnail-gallery.tsx`) to display all generated thumbnails (URLs from GCS via backend). Hold these URLs in local component state during editing.
-   Allow selection of one thumbnail from the gallery with clear visual indication of selection.
-   Implement a "Save" button using `frontend/src/components/ui/button.tsx`.
-   On save, send edited metadata and the *selected* thumbnail GCS URL to the backend API.
-   Provide feedback on save success/error using toast notifications.
-   Ensure editor reflects latest data after saving.

**REQ-FE-006: Publishing Interface** (Optional - Depends on backend readiness)
-   Add a "Publish" button to the detail view/editor.
-   Enable button only when processing is complete and required metadata is saved.
-   Click triggers backend API call.
-   Display feedback on initiation/status.
-   Handle potential publishing errors with standardized error messages.

### 4.2 Technical requirements

**REQ-FE-TECH-001: Supabase Client Integration**
-   **Priority:** High.
-   Use existing Supabase client configuration from `db/supabase/clients/client.ts` for browser contexts and `db/supabase/clients/server.ts` for server-side operations.
-   Implement Google OAuth flow and session management.
-   Implement retrieval/handling of the Supabase JWT.
-   Remove client-side Firebase initialization (`frontend/firebase.ts`) and related utilities.

**REQ-FE-TECH-002: WebSocket Client Implementation**
-   Implement a reusable hook `frontend/src/hooks/use-app-websocket.ts`.
-   Handle connection lifecycle (connection, disconnection, reconnection with exponential backoff).
-   Implement message parsing with appropriate typing.
-   Integrate with TanStack Query cache through direct cache updates or invalidation.
-   Ensure secure WebSocket connections (`wss://`).
-   Define message handling patterns for different update types (job updates, metadata updates, thumbnail generation).

**REQ-FE-TECH-003: Complete Firebase Removal**
-   Identify and refactor all code using Firebase services.
-   Replace Firebase Auth with Supabase Auth flow (adapting authentication components).
-   Replace Firestore interactions with backend API calls.
-   Remove Firebase SDK from `frontend/package.json` and config files.
-   Verify removal through dependency analysis.

**REQ-FE-TECH-004: API Client Configuration**
-   Refactor `frontend/src/api.ts` to create a reusable client wrapper.
-   Configure client to automatically include the Supabase JWT in all backend API requests.
-   Implement standardized error handling with appropriate error types.
-   Integrate with TanStack Query for data fetching and caching.

**REQ-FE-TECH-005: State Management Strategy**
-   Utilize TanStack Query for all backend API server state.
-   Use WebSocket messages to trigger cache updates or invalidation for real-time data changes.
-   Use local React component state for UI-specific state (e.g., form inputs, selected thumbnail).
-   Establish clear patterns for when to use each approach.

**REQ-FE-TECH-006: Responsive Design**
-   Ensure UI adapts gracefully using existing structure (`frontend/src/styles/app.css`, shadcn components).
-   Test layout and usability on desktop, tablet, and mobile viewports.
-   Focus on usability of critical features (upload, dashboard, editing) on mobile.

**REQ-FE-TECH-007: Testing**
-   Implement basic unit tests for critical utility functions and hooks.
-   Create integration tests for key components mocking backend/Supabase interactions.
-   Write end-to-end tests for core user flows: authentication, upload, editing metadata.
-   Utilize Vitest setup in `frontend/vitest.config.ts` for test implementation.

**REQ-FE-TECH-008: Cleanup Unused Routes/Components**
-   Identify and remove unused routes (`frontend/src/routes/posts.*`, `frontend/src/routes/users.*`, etc.) and associated components/utils.
-   Move necessary examples to `docs/frontend/examples/` for reference.
-   Update route configuration in `frontend/src/router.tsx`.
-   Regenerate route definitions using TanStack Router's generator.

**REQ-FE-TECH-009: Error Handling Standards**
-   Implement consistent error handling patterns across the application.
-   Define standard error types for different categories: API errors, validation errors, authentication errors.
-   Use toast notifications (`frontend/src/components/ui/use-toast.ts`) for user-facing error messages.
-   Log technical errors for debugging.
-   Implement appropriate retry logic for network operations where applicable.

**REQ-FE-TECH-010: Documentation**
-   Document key components and hooks within the frontend directory.
-   Create usage examples for reusable components.
-   Document WebSocket message formats and handling patterns.
-   Include setup instructions for development environment.
-   Maintain TypeScript types for all APIs and data structures.

## 5. User stories

**US-FE-001: User Authentication with Google via Supabase**
-   As a user, I want to log in securely using my Google account via Supabase, so that I can access the video processing application.
-   *Acceptance Criteria:*
    -   The login page displays a prominent "Login with Google" button.
    -   Clicking the button initiates the Supabase Google OAuth flow.
    -   After successful authentication, I am redirected to the dashboard page.
    -   My session persists across page reloads until I explicitly log out.
    -   I can log out by clicking a logout button in the navigation bar.
    -   After logging out, I am redirected to the login page.
    -   Attempting to access protected routes without authentication redirects me to the login page.

**US-FE-002: Video Upload Initiation (Direct GCS)**
-   As a content creator, I want to select and upload my video file directly to GCS, so that I can begin the processing workflow.
-   *Acceptance Criteria:*
    -   The dashboard provides a clear upload area with drag-and-drop functionality.
    -   I can browse and select a video file from my device.
    -   Invalid file types are rejected with clear error messages.
    -   I can see upload progress in real-time.
    -   After successful upload, I receive confirmation that processing has started.
    -   The newly uploaded video appears in my dashboard with a "processing" status.
    -   If an error occurs during upload, I receive a clear error message explaining the issue.

**US-FE-003: Real-time Dashboard Monitoring**
-   As a content creator, I want my dashboard to show my videos and their current processing status, updating automatically via WebSockets.
-   *Acceptance Criteria:*
    -   The dashboard displays a grid/list of my video processing jobs.
    -   Each video card shows a thumbnail (if available), title, status, and timestamp.
    -   Video status updates appear in real-time without page refresh.
    -   Videos in different states (processing, completed, error) are visually distinct.
    -   I can click on a video card to navigate to its detailed view.
    -   The dashboard displays an appropriate loading state while fetching initial data.
    -   The dashboard shows an appropriate empty state when I have no videos.
    -   The dashboard handles WebSocket connection issues gracefully without disrupting the UI.

**US-FE-004: Real-time Detail View Monitoring & Thumbnail Gallery**
-   As a content creator viewing a specific video's details, I want to see individual processing steps update their status in real-time, and view all generated thumbnails in a gallery.
-   *Acceptance Criteria:*
    -   The detail view shows basic video information (title, overall status, duration).
    -   Individual processing stages are displayed with their current status.
    -   Processing stage statuses update in real-time via WebSocket.
    -   As thumbnails are generated, they appear in a gallery without page refresh.
    -   The detail view handles WebSocket connection issues gracefully.
    -   Error states for failed processing are clearly indicated.
    -   Navigation back to the dashboard is easily accessible.

**US-FE-005: Metadata Review Interface**
-   As a content creator, I want to review all AI-generated metadata for my video, so that I can ensure it's accurate before publishing.
-   *Acceptance Criteria:*
    -   The detail view or a dedicated section displays all generated metadata.
    -   Metadata categories (title suggestions, description, tags, transcript, chapters) are clearly organized.
    -   Long-form content (transcript, chapters) is displayed in a readable format.
    -   I can easily navigate between different metadata sections.
    -   Metadata updates via WebSocket appear without page refresh.
    -   The interface handles incomplete or missing metadata gracefully.
    -   The interface is responsive and readable on different device sizes.

**US-FE-006: Metadata Editing and Thumbnail Selection/Saving**
-   As a content creator, I want to edit generated metadata, select my preferred thumbnail from the gallery, and save these choices via the backend API.
-   *Acceptance Criteria:*
    -   I can edit the title, description, and tags in form fields.
    -   I can view and potentially copy/download transcript and subtitles.
    -   The thumbnail gallery displays all generated thumbnail options.
    -   I can select a thumbnail with a clear visual indication of my selection.
    -   A prominent "Save" button is available to submit my changes.
    -   After saving, I receive confirmation that my changes were saved successfully.
    -   If save fails, I receive a clear error message without losing my edits.
    -   After saving, the interface reflects my saved choices.

**US-FE-007: Publishing Trigger**
-   As a content creator, I want to initiate the publishing process for my processed video, so that it can be distributed to its intended platform.
-   *Acceptance Criteria:*
    -   A "Publish" button is visible when video processing is complete and required metadata is saved.
    -   The button is disabled with explanation if prerequisites aren't met.
    -   Clicking the button triggers the publishing process via the backend API.
    -   I receive confirmation that publishing has started.
    -   The interface reflects the current publishing status.
    -   If publishing fails, I receive a clear error message with potential remediation steps.

## 6. Backend dependencies / assumptions

-   **Authentication:** Backend API endpoints requiring authentication can verify a Supabase JWT sent by the frontend.
-   **Signed URLs:** A backend API endpoint (e.g., `POST /api/videos/upload-url`) exists to provide GCS signed URLs for video uploads.
-   **Job Initiation:** A backend API endpoint (e.g., `POST /api/videos`) exists to notify the backend after a GCS upload is complete, triggering the processing pipeline.
-   **Data Fetching:** Backend API endpoints (e.g., `GET /api/videos`, `GET /api/videos/{job_id}`) exist to provide job lists and detailed job information, including status, generated metadata, and GCS URLs for *all* generated thumbnails.
-   **Metadata Update:** A backend API endpoint (e.g., `PUT /api/videos/{job_id}/metadata`) exists to receive and persist edited metadata, including the *selected* thumbnail GCS URL.
-   **Publishing:** (Optional) A backend API endpoint (e.g., `POST /api/videos/{job_id}/publish`) exists to trigger the publishing workflow.
-   **WebSockets:** A backend WebSocket endpoint exists, capable of broadcasting or sending targeted updates regarding job status, stage progress, and newly generated metadata/thumbnail URLs.
-   **Database Schema:** The Supabase database schema (managed by backend/DB team) supports storing user information, job details (including status, stages), GCS URL references for the original video and the *selected* thumbnail, and potentially other generated metadata.
-   **GCS Storage:** A GCS bucket is configured for video uploads and thumbnail storage. Generated thumbnails (selected and unselected) persist in GCS for retrieval during the editing phase.

## 7. WebSocket message format

The frontend will expect WebSocket messages from the backend in the following JSON format:

```json
{
  "type": "JOB_UPDATE" | "STAGE_UPDATE" | "METADATA_UPDATE" | "THUMBNAIL_GENERATED" | "ERROR",
  "job_id": "string",
  "data": {
    // Type-specific payload
  },
  "timestamp": "ISO-8601 string"
}
```

Specific message types will contain:

**JOB_UPDATE**
```json
{
  "type": "JOB_UPDATE",
  "job_id": "123",
  "data": {
    "status": "PROCESSING" | "COMPLETED" | "FAILED",
    "progress_percent": 75,
    "error_message": "Optional error details if status is FAILED"
  },
  "timestamp": "2023-04-15T12:34:56Z"
}
```

**STAGE_UPDATE**
```json
{
  "type": "STAGE_UPDATE",
  "job_id": "123",
  "data": {
    "stage_id": "THUMBNAIL_GENERATION",
    "status": "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED",
    "progress_percent": 50,
    "error_message": "Optional error details if status is FAILED"
  },
  "timestamp": "2023-04-15T12:34:56Z"
}
```

**METADATA_UPDATE**
```json
{
  "type": "METADATA_UPDATE",
  "job_id": "123",
  "data": {
    "metadata_type": "TITLE" | "DESCRIPTION" | "TAGS" | "TRANSCRIPT" | "CHAPTERS",
    "content": "The actual metadata content"
  },
  "timestamp": "2023-04-15T12:34:56Z"
}
```

**THUMBNAIL_GENERATED**
```json
{
  "type": "THUMBNAIL_GENERATED",
  "job_id": "123",
  "data": {
    "thumbnail_url": "https://storage.googleapis.com/bucket/path/to/thumbnail.jpg",
    "thumbnail_id": "unique_id",
    "width": 1280,
    "height": 720
  },
  "timestamp": "2023-04-15T12:34:56Z"
}
```

**ERROR**
```json
{
  "type": "ERROR",
  "job_id": "123",
  "data": {
    "error_code": "PROCESSING_ERROR",
    "error_message": "Detailed error message",
    "recoverable": false
  },
  "timestamp": "2023-04-15T12:34:56Z"
}
```

## 8. Error handling standards

The frontend will implement the following error handling patterns:

**API Request Errors**
- All API requests will use the API client wrapper that includes error handling.
- Errors will be categorized as:
  - `AuthenticationError`: For 401/403 responses (invalid or expired JWT)
  - `NetworkError`: For connection issues
  - `ValidationError`: For 400 responses (invalid input)
  - `ServerError`: For 500 responses (backend failures)
  - `UnknownError`: For uncategorized errors

**User-Facing Error Messages**
- Use toast notifications for transient errors
- Display inline error messages for form validation errors
- Show error states for failed operations directly in the UI
- Use friendly, actionable error messages that suggest next steps

**Error Recovery**
- Implement automatic retry (with exponential backoff) for network errors
- Redirect to login page for authentication errors
- Preserve user input when form submission fails
- Include refresh/retry actions for failed data loading

**WebSocket Connection Errors**
- Implement reconnection with exponential backoff
- Provide visual indication of connection status
- Fall back to polling API if WebSocket connection fails repeatedly

## 9. Migration plan

**Priority:** Focus initially on setting up Supabase client and authentication (REQ-FE-001, REQ-FE-TECH-001) before tackling other features.

1.  **Setup Supabase Auth & Route Protection:** Utilize existing client from `db/supabase/clients/client.ts`. Implement OAuth flow and session management. Create protected route layout with `_authenticated.tsx`.
2.  **Refactor Auth Screens:** Create `GoogleLoginButton.tsx` component for the login page.
3.  **Configure API Client:** Update `api.ts` to automatically include Supabase JWT with requests.
4.  **Implement Upload Flow:** Adapt `dropzone.tsx` for GCS Signed URL flow.
5.  **Implement WebSocket Hook:** Create `use-app-websocket.ts` with connection management and message handling.
6.  **Refactor Dashboard:** Update dashboard to fetch data via API and handle WebSocket updates.
7.  **Refactor Detail View:** Update video detail page to fetch data via API and handle WebSocket updates.
8.  **Implement Thumbnail Gallery & Editor:** Create or adapt thumbnail gallery and metadata editor components.
9.  **Implement Save/Publish:** Add functionality to save metadata and trigger publishing.
10. **Testing:** Implement basic tests for critical functionality.
11. **Cleanup:** Remove Firebase and unused example code.

## 10. Risks and mitigations

**Risk: Backend API Authentication Strategy Implementation**
-   *Impact:* Frontend unable to securely call backend API.
-   *Mitigation:* Close collaboration with backend team to ensure Supabase JWT verification is correctly implemented on the backend. Thorough integration testing.

**Risk: GCS Signed URL Generation/Handling**
-   *Impact:* Uploads fail due to incorrect URL generation, permissions, or expiry.
-   *Mitigation:* Backend provides correctly configured URLs. Frontend handles potential errors during the PUT request to GCS. Implement clear error messages for users.

**Risk: WebSocket Connection Instability**
-   *Impact:* Real-time updates fail to reach the frontend.
-   *Mitigation:* Robust client reconnection logic with exponential backoff. Clear indication of connection status. Fallback to polling API endpoints if necessary.

**Risk: State Synchronization Complexity (API/WebSockets)**
-   *Impact:* Inconsistent UI state, especially with temporary thumbnail URLs.
-   *Mitigation:* Clear approach to TanStack Query cache updates from WebSocket messages. Thorough testing of real-time update scenarios.

**Risk: Backend API / WebSocket Contract Changes**
-   *Impact:* Frontend breaks due to unexpected message formats or endpoint changes.
-   *Mitigation:* Define clear contracts for WebSocket message formats. Implement defensive parsing of incoming messages. Regular communication with backend team.

**Risk: Supabase Rate Limiting/Quotas**
-   *Impact:* Authentication failures due to service limitations.
-   *Mitigation:* Monitor Supabase usage. Implement appropriate error handling and user feedback for rate limit situations.

**Risk: Google OAuth Configuration Issues**
-   *Impact:* Users cannot log in.
-   *Mitigation:* Double-check OAuth configurations. Provide clear troubleshooting guidance in documentation.
