# Frontend Integration Plan: `apps/web` with Backend & Supabase

---

**Project Goal:** Integrate the `apps/web` frontend with the `apps/core` backend API and Supabase for authentication, video upload (direct-to-cloud), real-time processing status tracking (via WebSockets), and video management. Ensure a seamless, responsive user experience and robust error handling.

---

## Phase 1: Core Setup & Authentication Foundation

1.  **Environment Configuration (`apps/web`)**
    *   [ ] Task 1.1: **Verify and Complete Frontend Environment File**
        *   **File(s) to Check/Modify:** `apps/web/.env` (Create if not present, otherwise verify).
        *   **Key Actions:**
            *   Ensure `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` variables are present and correctly populated using your Supabase project credentials.
            *   Add/Verify the `VITE_API_BASE_URL` variable, pointing to the deployed backend API (e.g., `http://localhost:8000/api/v1` for local development).
        *   **Acceptance Criteria:** Environment variables are correctly loaded and accessible within the frontend application via `import.meta.env.VITE_SUPABASE_URL`, etc.

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
    *   [ ] Task 1.3: **Develop a Typed API Client Service for REST Endpoints**
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
        *   **Acceptance Criteria:** The `apps/web/src/lib/api.ts` module provides strongly-typed functions for all backend video processing interactions, with automated JWT handling and comprehensive error management.

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
        *   **Acceptance Criteria:** OAuth callbacks (Google login, email confirmation link) are processed smoothly, sessions are established, and users are redirected correctly. Error scenarios are handled.

8.  **Protected Route Implementation (`apps/web/src`)**
    *   [ ] Task 2.4: **Verify and Solidify Protected Route Mechanism**
        *   **File(s) to Check/Modify:**
            *   `apps/web/src/routes/_authed.tsx` (Review as the primary protected route layout).
            *   `apps/web/src/components/ProtectedLayout.tsx` (Review its role, possibly used by `_authed.tsx`).
            *   Any route intended to be private, ensuring it's nested under or uses the `_authed.tsx` layout (e.g., `apps/web/src/routes/dashboard.tsx`).
        *   **Key Actions:**
            *   Confirm that `_authed.tsx` (or `ProtectedLayout.tsx` if it's the core logic provider) effectively uses the `useAuth()` hook to check the user's authentication status.
            *   Verify that unauthenticated users attempting to access protected routes are redirected to `/login`.
            *   Test that authenticated users can access these routes without issue.
            *   Consider displaying a global loading indicator or skeleton layout while authentication status is being initially determined.
        *   **Acceptance Criteria:** All routes designated as protected are inaccessible to unauthenticated users, with proper redirection to the login page. Authenticated users have seamless access.

## Phase 3: Video Upload & Real-Time Processing Flow (Direct-to-Cloud & WebSockets)

9.  **Direct-to-Cloud Video Upload Component (`apps/web/src`)**
    *   [ ] Task 3.1: **Implement Direct-to-Cloud Upload in `VideoUploadDropzone.tsx`**
        *   **File(s) to Check/Modify:** `apps/web/src/components/video/VideoUploadDropzone.tsx`, `apps/web/src/lib/api.ts`.
        *   **Backend Prerequisite Notes:** Endpoints `POST /api/v1/videos/signed-upload-url` and `POST /api/v1/videos/upload-complete` must be available.
        *   **Key Actions:**
            1.  On file selection, call `api.getSignedUploadUrl()` from `lib/api.ts` with filename and content type.
            2.  Receive `uploadUrl` and `videoId` (or correlation ID).
            3.  Perform a direct `PUT` request to the `uploadUrl` (GCS) with the file content. Implement progress display using XHR/fetch `ReadableStream` if possible, or a simpler "uploading..." state.
            4.  On successful upload to GCS, call `api.notifyUploadComplete()` with `videoId`, original filename, actual storage path (if known, or backend infers), content type, and size.
            5.  Handle errors from all three steps (getting URL, GCS upload, notifying completion) using `Sonner` toasts or `Alert`.
            6.  On final success, navigate to job status page or update UI.
        *   **Acceptance Criteria:** Users can upload videos directly to cloud storage. UI shows progress/status. Backend is correctly notified to start processing. Errors are handled gracefully.

10. **WebSocket Client for Real-Time Updates (`apps/web/src`)**
    *   [ ] Task 3.2: **Implement WebSocket Hook (`useAppWebSocket.ts`)**
        *   **File(s) to Create:** `apps/web/src/hooks/useAppWebSocket.ts`.
        *   **Backend Prerequisite Note:** WebSocket endpoint (e.g., `WS /ws/jobs/status/{user_id}`) must be available.
        *   **Key Actions:**
            *   Establish WebSocket connection upon user login (or when hook is mounted in an authenticated context).
            *   Handle connection lifecycle (connect, disconnect, errors, reconnect attempts).
            *   Provide methods to send messages (if needed) and subscribe to incoming message types.
            *   Expose connection status and received messages reactively.
        *   **Acceptance Criteria:** A reusable hook manages WebSocket connectivity and message flow.

11. **Job Status Display with WebSockets & Polling Fallback (`apps/web/src`)**
    *   [ ] Task 3.3: **Implement Job Status Page with Real-time Updates & Polling Fallback**
        *   **File(s) to Check/Modify:** `apps/web/src/routes/jobs/[jobId].tsx` (Create/Adapt), `apps/web/src/hooks/useJobStatus.ts` (Create/Refactor), `apps/web/src/lib/api.ts`.
        *   **Key Actions:**
            *   In `hooks/useJobStatus.ts`:
                *   Accept `jobId`.
                *   Use `TanStack Query` to fetch initial job status via `api.getJobStatus(jobId)`.
                *   Use `useAppWebSocket.ts` to listen for messages related to this `jobId` (or all user jobs).
                *   On receiving a WebSocket update for the job, update the `TanStack Query` cache for that job using `queryClient.setQueryData`.
                *   Implement polling via `refetchInterval` in `useQuery` as a fallback if WebSocket is disconnected or for periodic consistency checks.
            *   In `jobs/[jobId].tsx` page: Use `useJobStatus(jobId)` to display job data, which will now update in real-time via WebSockets primarily.
        *   **Acceptance Criteria:** Job status page displays data that updates in real-time via WebSockets. Polling acts as a reliable fallback.

## Phase 4: Video Management & Viewing

12. **Video List Display on Dashboard (with Pagination)**
    *   [ ] Task 4.1: **Enhance Dashboard to List User's Videos with Pagination**
        *   **File(s) to Check/Modify:** `apps/web/src/routes/dashboard.tsx`, `apps/web/src/components/video/VideoList.tsx`, `apps/web/src/components/video/VideoListItem.tsx`, `apps/web/src/lib/api.ts`.
        *   **Backend Prerequisite Notes:** Endpoint `GET /api/v1/videos` (or `/users/me/videos`) must support pagination (e.g., `limit`, `offset`).
        *   **Key Actions:**
            *   Modify `api.getMyVideos` in `lib/api.ts` to accept pagination parameters.
            *   In `dashboard.tsx` / `VideoList.tsx`:
                *   Use `TanStack Query`'s `useInfiniteQuery` or manage pagination state manually for `getMyVideos`.
                *   Implement UI for pagination (e.g., "Load More" button, page numbers using `shadcn/ui Pagination`).
                *   Fetch initial list on component mount.
        *   **Acceptance Criteria:** Dashboard displays a paginated list of user's videos. Users can navigate through pages/load more videos.

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