# System Patterns

## Architecture Overview

The frontend application follows a modern React single-page application architecture with a focus on real-time updates and state management.

```
┌─────────────────────────────────────┐
│            React Frontend           │
├─────────────┬───────────┬───────────┤
│  TanStack   │  shadcn/  │  Custom   │
│   Router    │    UI     │Components │
├─────────────┴───────────┴───────────┤
│       State Management Layer        │
│  (TanStack Query + Local State)     │
├─────────────┬───────────┬───────────┤
│  API Client │ WebSocket │ Supabase  │
│   (HTTP)    │  Client   │  Auth     │
├─────────────┴───────────┴───────────┤
│         External Services           │
│  FastAPI Backend  │  GCS Storage    │
└─────────────────────────────────────┘
```

## Key Technical Decisions

1. **Authentication**: Supabase Google OAuth integration replaces Firebase for both simplicity and alignment with the backend authentication strategy.

2. **Real-time Updates**: FastAPI WebSockets provide real-time processing updates, replacing Firebase listeners. This creates a direct connection to our own backend.

3. **State Management**: TanStack Query handles server state and caching, with WebSocket updates triggering cache invalidation or updates. Local component state handles UI-specific state.

4. **Uploads**: Direct-to-GCS uploads via signed URLs reduce backend load and improve scalability for large video files.

5. **Component Structure**: Modular component design with separation between UI components (shadcn/ui), feature components, and route components.

## Component Relationships

- **Routes (`/routes`)**: Route components handle data fetching, URL parameters, and compose feature components.
  
- **Feature Components (`/components/video`, etc.)**: Implement specific application features combining UI components and business logic.
  
- **UI Components (`/components/ui`)**: Reusable, presentational components from shadcn/ui providing consistent styling.

- **Shared Components (`/components/shared`)**: Cross-cutting components like navbar, containers used across multiple routes.

- **Hooks (`/hooks`)**: Custom React hooks encapsulating reusable logic, such as WebSocket connection management.

## Critical Implementation Paths

1. **Authentication Flow**:
   ```
   Login Page → Supabase OAuth → JWT Token → Protected Routes
   ```

2. **Video Upload Flow**:
   ```
   Dropzone → API request for signed URL → Direct GCS upload → 
   API notification → WebSocket status updates
   ```

3. **Real-time Updates Flow**:
   ```
   WebSocket connection → Message parsing → TanStack Query cache update → 
   Component re-render
   ```

4. **Metadata Editing Flow**:
   ```
   Fetch metadata → Display in editor → User edits → 
   Save via API → Update local state
   ```

## Current File Structure

The frontend application is currently undergoing migration from Firebase to Supabase and cleanup of example code. The proposed file structure after refactoring:

```
frontend
├── app.config.ts
├── biome.json
├── components.json
├── Dockerfile
├── docs                          
│   └── examples                  # Archived example files
├── package.json                  # Firebase removed from deps
├── public
│   ├── fonts
│   └── vite.svg
├── src
│   ├── api.ts                    # Refactored for JWT handling
│   ├── client.tsx                # Application entry point
│   ├── components
│   │   ├── auth                  # Supabase auth components
│   │   │   └── GoogleLoginButton.tsx
│   │   ├── shared
│   │   │   ├── container.tsx
│   │   │   └── navbar.tsx        # With Supabase logout
│   │   ├── ui                    # shadcn/ui components
│   │   └── video                 # Core video components
│   │       ├── content-editor.tsx
│   │       ├── processing-dashboard.tsx 
│   │       ├── thumbnail-gallery.tsx
│   │       ├── video-detail.tsx    
│   │       └── video-progress-card.tsx
│   ├── hooks
│   │   ├── use-app-websocket.ts  # WebSocket connection management
│   │   └── use-mobile.ts
│   ├── lib
│   │   └── utils.ts
│   ├── router.tsx                # TanStack Router setup
│   ├── routes
│   │   ├── __root.tsx            # With Supabase auth listener
│   │   ├── _authenticated.tsx    # Auth guard
│   │   ├── dashboard.tsx         # Video listing
│   │   ├── index.tsx             # Home page
│   │   ├── login.tsx             # OAuth trigger
│   │   └── video.$videoId.tsx    # Video details
│   ├── routeTree.gen.ts          # Auto-generated
│   ├── styles
│   │   └── app.css
│   └── utils
│       └── seo.ts
└── tsconfig.json
``` 