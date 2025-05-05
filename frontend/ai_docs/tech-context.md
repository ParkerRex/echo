# Technical Context

## Core Technologies

### Frontend Framework
- **React**: The application is built with React, providing component-based architecture and efficient rendering.
- **TypeScript**: Used throughout for type safety and better developer experience.
- **Vite**: Used as the build tool and development server for fast refresh and optimized builds.

### Routing
- **TanStack Router**: Handles application routing with file-based route definitions and type-safe route params.

### UI Components
- **shadcn/ui**: Provides a set of accessible, customizable UI components built on Radix UI.
- **Tailwind CSS**: Used for styling through shadcn/ui components and custom styling.

### Authentication
- **Supabase Auth**: Handles Google OAuth authentication, JWT management, and session persistence.
- **JWT**: Used for securing API requests to the backend.

### State Management
- **TanStack Query**: Manages server state with caching, background updates, and optimistic UI.
- **React Context**: Used where global state needs to be shared (like authentication state).
- **Local Component State**: Handles UI-specific state that doesn't need to be shared.

### API Communication
- **Fetch API**: Wrapped in a custom API client for backend communication.
- **WebSocket API**: For real-time updates during video processing.

### Storage
- **Google Cloud Storage**: For video file and thumbnail storage, accessed via signed URLs.

### Development Tooling
- **Biome**: Modern JavaScript/TypeScript toolchain for linting and formatting.
- **Vitest**: Used for unit and integration testing.
- **pnpm**: Fast, disk space efficient package manager.

## Development Setup

### Environment Setup
1. Node.js and pnpm installed locally
2. Supabase project with Google OAuth configured
3. Google Cloud Storage bucket access
4. FastAPI backend running locally or accessible via URL

### Local Development
1. Clone the repository
2. Create `.env` file with required environment variables:
   ```
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   VITE_API_URL=http://localhost:8000
   VITE_WEBSOCKET_URL=ws://localhost:8000/ws
   ```
3. Run `pnpm install` to install dependencies
4. Run `pnpm dev` to start the development server

### Build Process
1. Run `pnpm build` to create an optimized production build
2. The built files are output to the `/dist` directory

## Technical Constraints

### Browser Support
- Modern evergreen browsers (Chrome, Firefox, Safari, Edge)
- No IE11 support required

### Performance Targets
- Initial page load under 2 seconds
- Time to interactive under 3 seconds
- Real-time updates displayed within 1 second of backend events

### API Dependencies
- Backend FastAPI endpoints for authentication, video processing, and metadata management
- Supabase project for authentication
- GCS buckets for storage

### Security Requirements
- All API requests must include valid Supabase JWT
- Direct user access to GCS must be via signed URLs only
- WebSocket connections must be secured (wss://)

## Integration Points

### Backend API Integration
- RESTful API endpoints for CRUD operations on videos and metadata
- Authentication via Supabase JWT in Authorization header
- Custom error handling and retry logic

### Supabase Integration
- Authentication flow using Supabase client from `db/supabase/clients/client.ts`
- Session management and JWT handling

### WebSocket Integration
- Connection to FastAPI WebSocket endpoint
- Handling of connection lifecycle (connect, disconnect, reconnect)
- Message parsing and integration with UI state

### GCS Integration
- Direct uploads to GCS using signed URLs
- Retrieval of video and thumbnail assets from GCS URLs

## Tool Usage Patterns

### State Management Pattern
```tsx
// Using TanStack Query for server state
const { data, isLoading, error } = useQuery({
  queryKey: ['videos'],
  queryFn: () => api.getVideos()
});

// Using local state for UI-specific state
const [selectedThumbnail, setSelectedThumbnail] = useState<string | null>(null);
```

### API Client Pattern
```tsx
// api.ts
const api = {
  async getVideos() {
    const response = await fetch('/api/videos', {
      headers: {
        'Authorization': `Bearer ${getSupabaseToken()}`
      }
    });
    if (!response.ok) throw new ApiError(response.statusText);
    return response.json();
  }
};
```

### WebSocket Pattern
```tsx
// Using custom WebSocket hook
const { messages, connectionStatus } = useAppWebSocket();

// React to new messages
useEffect(() => {
  if (messages.length > 0) {
    const latestMessage = messages[messages.length - 1];
    if (latestMessage.type === 'JOB_UPDATE') {
      // Update UI or invalidate queries
    }
  }
}, [messages]);
``` 