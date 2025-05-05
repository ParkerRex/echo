# Active Context

## Current Work Focus

The frontend is currently undergoing a significant migration with three main focus areas:

1. **Authentication Migration**: Replacing Firebase authentication with Supabase Google OAuth, including:
   - Creating a `GoogleLoginButton` component
   - Setting up Supabase client integration
   - Implementing authentication state management
   - Creating a protected route layout

2. **Real-time Updates**: Implementing WebSocket-based real-time updates to replace Firebase listeners, including:
   - Creating a `use-app-websocket` hook
   - Handling WebSocket connection lifecycle
   - Integrating WebSocket updates with TanStack Query cache
   - Updating components to handle WebSocket messages

3. **Cleanup & Refactoring**: Removing Firebase dependencies and unused example code, including:
   - Removing `firebase.ts` and related imports
   - Cleaning up unused routes and components
   - Refactoring dashboard and video detail views
   - Implementing proper error handling

## Recent Changes

- Identified Firebase dependencies and usage patterns throughout the codebase
- Created PRD and implementation plan for the migration
- Documented WebSocket message format expectations
- Defined standardized error handling patterns
- Outlined component structure for the refactored application

## Next Steps

1. **Initial Authentication Setup**:
   - Implement `GoogleLoginButton` component
   - Create `_authenticated.tsx` layout for protected routes
   - Set up Supabase session listener in `__root.tsx`
   - Update API client to include JWT in requests

2. **Core WebSocket Implementation**:
   - Create `use-app-websocket.ts` hook
   - Implement connection management and message handling
   - Define integration with TanStack Query

3. **Dashboard Refactoring**:
   - Update `dashboard.tsx` to fetch via API instead of Firebase
   - Integrate WebSocket updates for real-time status changes
   - Implement loading and error states

4. **Video Detail View Refactoring**:
   - Update `video.$videoId.tsx` to fetch from API
   - Implement or adapt thumbnail gallery
   - Create metadata editor with save functionality

5. **Removal of Firebase**:
   - Remove Firebase SDK from `package.json`
   - Clean up Firebase initialization and imports
   - Verify application functions without Firebase dependencies

## Active Decisions and Considerations

1. **WebSocket Message Handling**: Currently deciding between two approaches:
   - Direct TanStack Query cache manipulation based on message type
   - Query invalidation triggering refetch from API
   - Leaning toward a hybrid approach based on message type

2. **Authentication Flow**:
   - Considering best approach for handling authentication redirects
   - Evaluating use of TanStack Router's capabilities for route protection
   - Need to ensure Supabase session persistence works correctly

3. **Error Handling**:
   - Defining standardized error handling patterns
   - Creating appropriate error types for different failure scenarios
   - Determining retry strategies for network failures

4. **Thumbnail Gallery**:
   - Deciding between creating a new component or adapting existing UI
   - Considering interaction patterns for thumbnail selection
   - Planning for efficient rendering of potentially many thumbnails

## Important Patterns and Preferences

1. **Component Structure**:
   - Feature components (`/components/video/*`) should compose UI components (`/components/ui/*`)
   - Route components should primarily handle data fetching and composition
   - Common functionality should be extracted to hooks

2. **State Management**:
   - Server state should be managed with TanStack Query
   - Authentication state should be global using Supabase's auth state listener
   - UI-specific state should use local component state
   - WebSocket updates should integrate with the TanStack Query cache

3. **Code Organization**:
   - Group related components in folders
   - Keep routes flat and aligned with URL structure
   - Extract reusable logic to hooks
   - Use consistent naming patterns

## Learnings and Project Insights

1. **Transition Complexity**: Migration from Firebase to Supabase is more than just swapping libraries - it requires rethinking authentication flow, real-time updates, and error handling.

2. **WebSocket Integration**: Handling WebSocket messages efficiently requires careful integration with the application's state management strategy.

3. **Authentication Flow**: OAuth flows require careful handling of redirects and session management to ensure a smooth user experience.

4. **Real-time UX**: Users expect immediate feedback on long-running processes like video processing, making real-time updates critical to the experience. 