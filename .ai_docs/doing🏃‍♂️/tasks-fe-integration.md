# Frontend Integration Plan: `apps/web` with Backend & Supabase

---
**Status Update (As of 2025-05-18):**
*   **API Client Service (`apps/web/src/lib/api.ts`):**
    *   [X] Updated with new backend REST endpoints (`getSignedUploadUrl`, `notifyUploadComplete`, `getMyVideos`, `getVideoDetails`, `updateVideoMetadata`, `getJobDetails`).
    *   [X] Created `apps/web/src/types/api.ts` for all API client TypeScript types.
    *   [X] Implemented a generic `handleApiResponse` for consistent error handling.
*   **Video Upload Feature (`apps/web/src/components/video/VideoUploadDropzone.tsx`):**
    *   [X] Modified to implement the 3-step direct-to-cloud upload using the new API client functions.
    *   [X] Type `UploadCompleteRequest` in `types/api.ts` updated to make `storagePath` optional.
*   **Real-time Job Status Hooks (`apps/web/src/hooks/`):**
    *   [X] Created `useAppWebSocket.ts` to manage WebSocket connection for job status updates.
    *   [X] Created `useJobStatus.ts` to consume WebSocket updates (via `useAppWebSocket`) and update TanStack Query cache.
    *   [X] Addressed module resolution for `@echo/db` by adding `exports` to `supabase/package.json`.
*   **Workspace Configuration:** Previous fixes for pnpm workspace setup, TypeScript path aliases for `@echo/db`, and unified monorepo scripts remain in place, unblocking further development.

---

**Project Goal:** Integrate the `apps/web` frontend with the `apps/core` backend API and Supabase for authentication, video upload (direct-to-cloud), real-time processing status tracking (via WebSockets), and video management. Ensure a seamless, responsive user experience and robust error handling.

---

## Phase 1: Core Setup & Authentication Foundation

1.  **Environment Configuration (`apps/web` and `apps/core`)**
    *   [X] Task 1.1: **Standardize and Consolidate Environment Files**
        *   **File(s) Modified:**
            *   `apps/web/.env.development` (Created/Updated with local dev values)
            *   `apps/web/.env.production` (Created/Updated with production placeholders)
            *   `apps/web/.env.example` (Created with placeholders)
            *   `apps/web/.gitignore` (Updated to correctly ignore/include .env files)
            *   `apps/core/.env.development` (Created with local dev values)
            *   `apps/core/.env.production` (Created with production values)
            *   `apps/core/.env.example` (Reviewed and confirmed)
            *   Deleted `apps/web/.env`, `apps/core/.env`, and root `.env` after consolidation.
        *   **Key Actions:**
            *   Consolidated various `.env` files into a standardized structure: `.env.development`, `.env.production`, and `.env.example` for both `apps/web` and `apps/core`.
            *   Ensured `apps/web/.env.development` and `apps/web/.env.production` contain `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, and `VITE_API_BASE_URL`.
            *   Verified `apps/core` environment files are structured for development and production, separating local and hosted service configurations.
        *   **Acceptance Criteria:** Environment variables are correctly structured for different environments (development, production) for both frontend and backend. Frontend variables are accessible via `import.meta.env.*`. `.gitignore` handles these files appropriately.

2.  **Supabase Client & Authentication Hooks (`apps/web/src` & `supabase/`)**
    *   [ ] Task 1.2: **Standardize Supabase Client and Authentication Logic**
        *   **File(s) to Check/Modify:**
            *   `supabase/clients/client.ts`: Review this shared client. Confirm its configuration is suitable for client-side usage in `apps/web`.
            *   `apps/web/src/utils/supabase.ts`: Currently contains `getSupabaseServerClient`. Evaluate if a client-side utility/hook here should wrap `supabase/clients/client.ts` or if direct import is preferred.
            *   `apps/web/src/hooks/useAuth.ts` (Create, or verify and refactor if similar logic exists elsewhere).
            *   `apps/web/src/router.tsx` or `apps/web/src/client.tsx` or `apps/web/src/routes/__root.tsx`: Ensure any global AuthProvider wraps the application.
        *   **Key Actions:**
            *   **Client-Side Supabase Access:** Establish a clear and consistent method for accessing the Supabase client instance throughout the frontend (likely importing from `supabase/clients/client.ts`).
            *   **Develop `useAuth.ts` Hook:**
                *   Provide reactive state: `user`, `session`, `isLoading`, `error`.
                *   Expose authentication methods: `loginWithPassword(email, password)`, `signUpWithEmailPassword(email, password)`, `signOut()`, `signInWithGoogle()`.
                *   These methods should internally call the Supabase client (e.g., `supabase.auth.signInWithPassword()`).
                *   Subscribe to `supabase.auth.onAuthStateChange` to update and reflect auth state changes application-wide.
        *   **Acceptance Criteria:** A `useAuth()` hook is available, providing reactive authentication state (user, session, loading status) and all necessary authentication functions. The Supabase client configuration is verified.

3.  **API Client Service for Backend Communication (`apps/web/src/lib`)**
    *   [X] Task 1.3: **Develop a Typed API Client Service for REST Endpoints**
        *   **File(s) to Check/Modify:**
            *   `apps/web/src/lib/api.ts`: Review and enhance this existing file to serve as the central API client.
            *   `apps/web/src/types/api.ts` (Create, or identify existing location for shared types).
        *   **Key Actions:**
            *   In `apps/web/src/lib/api.ts`:
                *   Implement a base `fetch` wrapper or utilize `axios` (if already a project dependency and preferred for features like interceptors).
                *   Integrate dynamic fetching of the Supabase JWT: `const token = (await supabase.auth.getSession())?.data.session?.access_token;`.
                *   Automatically include the `Authorization: Bearer ${token}` header in requests to protected backend endpoints.
                *   Default `Content-Type: application/json` for `POST`/`PUT` requests.
                *   Construct full request URLs using `VITE_API_BASE_URL`.
                *   Implement robust error handling: parse JSON error responses from the backend, handle network errors, and specific HTTP status codes (401, 403, 404, 500).
            *   In `apps/web/src/types/api.ts`:
                *   Define TypeScript interfaces for all backend API request bodies and response payloads relevant to video processing (e.g., `VideoUploadResponseSchema`, `VideoJobSchema`, `VideoSchema`, `VideoMetadataSchema` as defined in `apps/core/api/schemas/video_processing_schemas.py`).
        *   **Acceptance Criteria:** The `apps/web/src/lib/api.ts` module provides strongly-typed functions for all backend video processing interactions, with (manual JWT handling for now - to be reviewed in Task 1.3 if auto-injection is needed) and comprehensive error management.

4.  **Type Sharing/Generation Strategy**
    *   [ ] Task 1.4: **Investigate and Implement Type Sharing/Generation**
        *   **Key Actions:** Decide on a strategy to keep frontend TypeScript types (`apps/web/src/types/api.ts`) synchronized with backend Pydantic models. Options:
            *   Manual synchronization (prone to error).
            *   Codegen tool (e.g., `pydantic-to-typescript`).
            *   Shared monorepo package (if feasible for Pydantic models & TS types).
        *   Implement the chosen strategy.
        *   **Acceptance Criteria:** A maintainable process for type consistency between frontend and backend is established.

## Phase 2: User Authentication Flow Implementation

5.  **Login Page and Components (`apps/web/src`)**
    *   [ ] Task 2.1: **Verify and Enhance Login Functionality**
        *   **File(s) to Check/Modify:**
            *   `apps/web/src/routes/login.tsx` (Verify route setup).
            *   `apps/web/src/components/login.tsx` (Verify form component, or `apps/web/src/components/auth.tsx`).
            *   `apps/web/src/components/GoogleLoginButton.tsx` (Verify Google OAuth integration).
        *   **Key Actions:**
            *   Ensure the login form component (e.g., `login.tsx`) correctly calls `useAuth().loginWithPassword()` upon submission.
            *   Verify `GoogleLoginButton.tsx` correctly calls `useAuth().signInWithGoogle()`.
            *   Integrate with `shadcn/ui Form` components and a library like `react-hook-form` with `zod` for validation, if consistent with project patterns.
            *   Clearly display loading states (e.g., button disabled, spinner) and error messages sourced from the `useAuth()` hook.
            *   Confirm successful login navigates to the `/dashboard` route (TanStack Router's `navigate` function).
            *   Ensure "Sign up" link navigates to the signup page.
        *   **Acceptance Criteria:** Users can successfully log in using email/password and Google OAuth. Form validation, loading states, error display, and redirection are correctly implemented.

6.  **Signup Page and Components (`apps/web/src`)**
    *   [ ] Task 2.2: **Verify and Enhance Signup Functionality**
        *   **File(s) to Check/Modify:**
            *   `apps/web/src/routes/signup.tsx` (Verify route setup).
            *   A dedicated signup form component e.g., `apps/web/src/components/auth/SignupForm.tsx` (Create if `login.tsx` or `auth.tsx` isn't adaptable, otherwise verify existing).
        *   **Key Actions:**
            *   Ensure the signup form component calls `useAuth().signUpWithEmailPassword()` on submission.
            *   Utilize `shadcn/ui Form` components for structure and validation (e.g. password confirmation).
            *   Display loading states and relevant error messages (e.g., "Email already in use", "Passwords do not match").
            *   Provide clear user feedback upon successful signup (e.g., "Please check your email to confirm your account.").
            *   Ensure "Login" link navigates to the login page.
        *   **Acceptance Criteria:** Users can create new accounts. Form validation, loading/error states, and user feedback mechanisms are robust.

7.  **Authentication Callback Handling (`apps/web/src`)**
    *   [ ] Task 2.3: **Ensure OAuth Callback Route Works Correctly**
        *   **File(s) to Check/Modify:** `apps/web/src/routes/auth/callback.tsx` (Verify existing functionality).
        *   **Key Actions:**
            *   Confirm that this route correctly handles the session establishment after OAuth providers (like Google) redirect back to the application.
            *   Verify it redirects users to the appropriate page (e.g., `/dashboard`) post-authentication.
            *   Implement a user-friendly loading message during processing.
            *   Ensure any potential errors during the callback (e.g., state mismatch, provider error) are gracefully handled and displayed to the user.
        *   **Acceptance Criteria:** OAuth callbacks (Google login, email confirmation link) are processed smoothly, sessions are established, and users are redirected correctly. Error scenarios are handled. (Met)

8.  **Protected Route Implementation (`apps/web/src`)**
    *   [X] Task 2.4: **Verify and Solidify Protected Route Mechanism**
        *   **File(s) to Check/Modify:**
            *   `apps/web/src/routes/_authed.tsx` (Reviewed and refactored to use client-side session check with `supabase.auth.getSession()` in `beforeLoad`, redirecting to `/login` if unauthenticated. Added loading state and Outlet.)
            *   `apps/web/src/components/ProtectedLayout.tsx` (Reviewed. Contains older, redundant server-side auth check. Not directly used by the new `_authed.tsx` logic. Its direct usage should be phased out or refactored if its layout structure is needed.)
            *   Any route intended to be private, ensuring it's nested under or uses the `_authed.tsx` layout (e.g., `apps/web/src/routes/dashboard.tsx`). (Mechanism in place via `_authed.tsx` for routes like `_authed/dashboard.tsx` or `_authed.dashboard.tsx`)
        *   **Key Actions:**
            *   Confirm that `_authed.tsx` effectively uses `supabase.auth.getSession()` (or `useAuth()` if applicable in `beforeLoad`) to check authentication. (Implemented using `supabase.auth.getSession()` in `beforeLoad`.)
            *   Verify that unauthenticated users attempting to access protected routes are redirected to `/login`. (Implemented via `redirect` in `beforeLoad`.)
            *   Test that authenticated users can access these routes without issue. (Mechanism in place.)
            *   Consider displaying a global loading indicator or skeleton layout while authentication status is being initially determined. (Implemented `pendingComponent` in `_authed.tsx`.)
        *   **Acceptance Criteria:** All routes designated as protected are inaccessible to unauthenticated users, with proper redirection to the login page. Authenticated users have seamless access. (Met)

## Phase 3: Video Upload & Real-Time Processing Flow (Direct-to-Cloud & WebSockets)

9.  **Direct-to-Cloud Video Upload Component (`apps/web/src`)**
    *   [X] Task 3.1: **Implement Direct-to-Cloud Upload in `VideoUploadDropzone.tsx`**
        *   **File(s) to Check/Modify:** `apps/web/src/components/video/VideoUploadDropzone.tsx`, `apps/web/src/lib/api.ts`.
        *   **Backend Prerequisite Notes:** Endpoints `POST /api/v1/videos/signed-upload-url` and `POST /api/v1/videos/upload-complete` must be available.
        *   **Key Actions:**
            1.  On file selection, call `api.getSignedUploadUrl()` from `lib/api.ts` with filename and content type. (Verified, uses `content_type`)
            2.  Receive `upload_url` and `video_id` (or correlation ID). (Verified, destructured to camelCase `uploadUrl`, `videoId` for internal use)
            3.  Perform a direct `PUT` request to the `uploadUrl` (GCS) with the file content. Implement progress display using XHR/fetch `ReadableStream` if possible, or a simpler "uploading..." state. (Verified, uses XHR with progress)
            4.  On successful upload to GCS, call `api.notifyUploadComplete()` with `video_id`, `original_filename`, `content_type`, and `size_bytes`. (Verified, uses snake_case for request object)
            5.  Handle errors from all three steps (getting URL, GCS upload, notifying completion) using `Sonner` toasts or `Alert`. (Implemented using `toast.error()`)
            6.  On final success, navigate to job status page or update UI. (Handled via `onUploadComplete` prop callback)
        *   **Additional Steps Taken:**
            *   Refactored `lib/api.ts` to use Supabase JWT for authorization in API calls instead of `credentials: "include"`.
            *   Added missing Pydantic models to `apps/core/api/schemas/video_processing_schemas.py` for types required by `lib/api.ts` and `VideoUploadDropzone.tsx` (e.g., `SignedUploadUrlRequest`, `SignedUploadUrlResponse`, `UploadCompleteRequest`, `ApiErrorResponse`, `VideoSummary`, `VideoDetailsResponse`, `VideoMetadataUpdateRequest`).
            *   Regenerated TypeScript types in `apps/web/src/types/api.ts` using `pnpm run generate:api-types`.
            *   Updated `VideoUploadDropzone.tsx` to use `snake_case` properties when interacting with these generated types to resolve linter errors.
        *   **Acceptance Criteria:** Users can upload videos directly to cloud storage. UI shows progress/status. Backend is correctly notified to start processing. Errors are handled gracefully. (Met)

10. **WebSocket Client for Real-Time Updates (`apps/web/src`)**
    *   [X] Task 3.2: **Implement WebSocket Hook (`useAppWebSocket.ts`)**
        *   **File(s) to Create:** `apps/web/src/hooks/useAppWebSocket.ts`. (Created)
        *   **Backend Prerequisite Note:** WebSocket endpoint (e.g., `WS /ws/jobs/status/{user_id}`) must be available.
        *   **Key Actions:**
            *   Establish WebSocket connection upon user login using JWT and user ID from `useAuth()`. (Implemented)
            *   Handle connection lifecycle (connect, disconnect, errors, basic reconnect attempts). (Implemented)
            *   Provide methods to send messages (`sendJsonMessage`) and expose received messages (`lastJsonMessage`) reactively. (Implemented)
            *   Expose connection status (`connectionStatus`, `isConnected`) reactively. (Implemented)
        *   **Acceptance Criteria:** A reusable hook manages WebSocket connectivity and message flow. (Met)

11. **Job Status Display with WebSockets & Polling Fallback (`apps/web/src`)**
    *   [X] Task 3.3: **Implement Job Status Management Hook (`useJobStatusManager.ts`) with TanStack Cache Updates** (UI Page for Job Status still pending)
        *   **File(s) to Check/Modify:** `apps/web/src/hooks/useJobStatusManager.ts` (Created/Refactored from `useJobStatus.ts`).
        *   **Backend Prerequisite Notes:** `api.getJobDetails(jobId)` endpoint for initial fetch and polling fallback if WS fails.
        *   **Key Actions:**
            *   In `hooks/useJobStatusManager.ts`:
                *   Does not accept `jobId` directly; manages user-level job updates.
                *   Uses `useAppWebSocket.ts` to listen for messages for the authenticated user.
                *   On receiving a WebSocket update (`lastJsonMessage`), attempts to parse it as `WebSocketJobUpdate` (locally defined type `Partial<VideoJobSchema> & { job_id: number; video_id?: number }`).
                *   Updates `TanStack Query` cache for specific jobs (`['jobDetails', String(job_id)]`) and video lists (`['myVideos']`) using `queryClient.setQueryData`.
            *   (Polling fallback via `refetchInterval` in `useQuery` for individual job pages is not yet implemented as part of this hook, but could be added to the page component that uses `useQuery(['jobDetails', jobId], ...)`).
            *   (The page `jobs/[jobId].tsx` is not yet implemented, only the hook logic for cache updates based on WebSocket messages.)
        *   **Acceptance Criteria:** `useJobStatusManager.ts` hook correctly processes WebSocket messages and updates TanStack Query cache for relevant job and video list data. (Met for WS part; polling and specific job page UI are separate concerns).

## Phase 4: Video Management & Viewing

12. **Video List Display on Dashboard (with Pagination)**
    *   [X] Task 4.1: **Enhance Dashboard to List User's Videos with Pagination** (Met)
        *   **File(s) to Check/Modify:** `apps/web/src/routes/dashboard.tsx`, `apps/web/src/components/video/VideoList.tsx` (Created), `apps/web/src/components/video/VideoListItem.tsx` (Created), `apps/web/src/lib/api.ts`.
        *   **Backend Prerequisite Notes:** Endpoint `GET /api/v1/videos` (or `/users/me/videos`) must support pagination (e.g., `limit`, `offset`). (Verified: `users/me/videos` with `limit` and `offset` is used)
        *   **Key Actions:**
            *   Modified `api.fetchMyVideos` in `lib/api.ts` to accept optional `limit` and `offset` pagination parameters and include them in the API request. Defined `PaginationParams` interface.
            *   Refactored `dashboard.tsx`:
                *   Removed `ProtectedLayout` wrapper.
                *   Changed `useQuery` to `useInfiniteQuery` for `fetchMyVideos`, including `queryFn`, `initialPageParam`, and `getNextPageParam`.
                *   Corrected `thumbnail_url` to `thumbnail_file_url` usage.
            *   Created `apps/web/src/components/video/VideoListItem.tsx` to display a single video item with link to its detail page.
            *   Created `apps/web/src/components/video/VideoList.tsx` to:
                *   Display a list of videos using `VideoListItem.tsx`.
                *   Handle loading (with skeletons), empty, and error states.
                *   Include a "Load More" button connected to `fetchNextPage` from `useInfiniteQuery`.
            *   Refactored `dashboard.tsx` to use the new `VideoList.tsx` component, passing necessary props from `useInfiniteQuery` results and a callback to trigger the upload dialog.
        *   **Acceptance Criteria:** Dashboard displays a paginated list of user's videos. Users can navigate through pages/load more videos. (Met)

13. **Video Detail and Playback Page (`apps/web/src`)**
    *   [ ] Task 4.2: **Implement Full Video Detail and Playback Functionality**
        *   **File(s) to Check/Modify:** `apps/web/src/routes/video/[videoId].tsx`, `apps/web/src/components/video/video-detail.tsx`, `apps/web/src/components/video/MediaPlayer.tsx`, `apps/web/src/lib/api.ts`, `apps/web/src/components/video/content-editor.tsx`.
        *   **Backend Prerequisite Notes:** 
            *   Endpoint `GET /api/v1/videos/{videoId}/details` must be available.
            *   Strategy for video playback source: Backend provides a `playbackUrl` (e.g., GCS signed URL) via the details endpoint, or a streaming endpoint `GET /api/v1/stream/video/{videoId}` must be available.
            *   Endpoint `PUT /api/v1/videos/{videoId}/metadata` for editing.
        *   **Key Actions:** (Largely same as previous, but ensure API calls match new structure)
            *   Fetch data using `api.getVideoDetails(videoId)`.
            *   Implement `MediaPlayer.tsx` using the `playbackUrl` or streaming URL.
            *   Display metadata, transcript, subtitles (`<track>`).
            *   Implement metadata editing via `content-editor.tsx` and `api.updateVideoMetadata()`.
        *   **Acceptance Criteria:** Users can view videos with playback, subtitles, all metadata. Editing (if implemented) saves changes.

## Phase 5: UI/UX Polish & Finalization

14. **Consistent Loading Skeletons and Empty States**
    *   [ ] Task 5.1: **Implement UI Placeholders**
        *   **File(s) to Check/Modify:** All pages and components that involve asynchronous data fetching (e.g., `dashboard.tsx`, `jobs/[jobId].tsx`, `video/[videoId].tsx`).
        *   **Key Actions:**
            *   Utilize the `shadcn/ui Skeleton` component (from `apps/web/src/components/ui/skeleton.tsx`) to create loading placeholders for content areas while `useQuery` is in its `isLoading` state.
            *   Design and implement clear and user-friendly "empty state" messages for situations where no data is available (e.g., "You haven't uploaded any videos yet." on the dashboard, or "Video data is not yet available." if metadata is still being processed).
        *   **Acceptance Criteria:** The application provides smooth visual feedback during data loading phases using skeleton screens, and presents informative messages when content areas are empty.

15. **Standardized Error Handling and Notifications**
    *   [ ] Task 5.2: **Unify Error Display** (Emphasize contextual errors for new flows).
        *   **File(s) to Check/Modify:** All components that handle API calls or user input leading to potential errors. Revisit `useAuth.ts`, `lib/api.ts`, and form components.
            *   `apps/web/src/components/ui/sonner.tsx` (or `toaster.tsx` / `use-toast.tsx` if that's the active toast system).
        *   **Key Actions:**
            *   Consistently use `sonner` (or the project's chosen toast component) for non-modal error notifications arising from API interactions (e.g., "Failed to upload video: Server error").
            *   Employ `shadcn/ui Alert` with `variant="destructive"` for more prominent, inline error messages within forms or specific content sections (e.g., "Invalid email address" below an input field).
            *   Ensure error messages are user-friendly and, where appropriate, suggest corrective actions.
        *   **Acceptance Criteria:** Errors are communicated to the user in a consistent, clear, and non-disruptive manner across the application.

16. **Responsive Design Review and Adjustments**
    *   [ ] Task 5.3: **Ensure Mobile and Tablet Usability**
        *   **File(s) to Check/Modify:** Key layout files (`__root.tsx`, `_authed.tsx`) and primary view components (`dashboard.tsx`, `login.tsx`, `video/[videoId].tsx`, `jobs/[jobId].tsx`). Also, `apps/web/src/styles/app.css` or any global style sheets.
        *   **Key Actions:**
            *   Thoroughly test all primary application flows and pages on various screen sizes (desktop, tablet, mobile).
            *   Use browser developer tools to emulate different devices.
            *   Adjust layouts, font sizes, component visibility, and interaction patterns as needed using Tailwind CSS's responsive utility classes (e.g., `sm:`, `md:`, `lg:`).
            *   Pay special attention to navigation, forms, and data tables/lists on smaller screens.
        *   **Acceptance Criteria:** The core application is fully responsive, providing a good user experience across common device types and screen resolutions. 