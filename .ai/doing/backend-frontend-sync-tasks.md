# Backend & Frontend Synchronization Tasks - Enhanced with TanStack Documentation

**Updated:** January 2025  
**Objective:** Complete end-to-end type safety and synchronization between Python backend and TypeScript frontend

## 🎯 CURRENT STATUS

**✅ COMPLETED:**
- Database schema migration (3-table structure)
- Python models and enums
- Local Supabase environment setup

**❌ PENDING:**
- Backend async refactoring
- Pydantic schema alignment
- TypeScript type generation
- Frontend code updates
- TanStack Start configuration fixes

## 📚 TanStack Documentation References

### TanStack Start Key Documentation
- **Basic Setup**: Examples > Basic - Complete starter template
- **API Routes**: File-based routing conventions with `/api` prefix and entry handlers
- **SSR Setup**: `app/ssr.tsx` with `createStartHandler` configuration
- **Server Functions**: Creating server functions with validation and context access
- **Path Aliases**: `vite-tsconfig-paths` plugin and `tsconfig.json` configuration
- **React Query Integration**: `createRootRouteWithContext<{ queryClient: QueryClient }>` pattern
- **Supabase Auth Example**: Server function patterns for user authentication
- **Static Prerendering**: Configuration for static site generation

### TanStack Router Key Documentation
- **Route Configuration**: File-based routing with automatic type safety
- **Type Generation**: Automatic TypeScript type generation for routes (`routeTree.gen.ts`)
- **Data Loading**: Loaders, search params, and route context patterns
- **Navigation**: Link components and programmatic navigation
- **Error Handling**: Error boundaries and not found routes
- **Code Splitting**: Route-based lazy loading and dynamic imports
- **Search Params**: Type-safe search parameter validation with Zod
- **Route Context**: Sharing data between parent and child routes

### Integration Patterns
- **React Query + Router**: Context-based integration for data fetching
- **Supabase + Auth**: Server-side authentication with protected routes
- **Error Boundaries**: Comprehensive error handling at route and component levels
- **TypeScript**: Full type safety from routes to components

---

## 📋 PHASE 2: Backend Code Generation (Remaining)

### Task 2.2: Generate & Verify SQLAlchemy ORM Models ❌
**Priority:** HIGH  
**Estimated Time:** 1-2 hours

**Objective:** Ensure ORM models are properly generated and aligned with database schema

**Actions:**
1. Run code generation: `pnpm codegen:db-orm-models`
2. Verify generated models in `apps/core/app/db/models.py`
3. Check relationships and enum usage
4. Ensure models match existing `apps/core/models/` structure

**Verification:**
- [ ] Models generated successfully
- [ ] Relationships properly defined
- [ ] ProcessingStatus enum correctly used
- [ ] No conflicts with existing models

### Task 2.5: Generate Pydantic Models from Supabase ❌
**Priority:** MEDIUM  
**Estimated Time:** 30 minutes

**Objective:** Generate Pydantic models directly from live Supabase schema

**Actions:**
1. Verify environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
2. Run: `pnpm codegen:db-pydantic-models`
3. Review generated `apps/core/app/db_pydantic_models/supabase_models.py`
4. Compare with manual models for consistency

**Verification:**
- [ ] Pydantic models generated
- [ ] Types correctly mapped
- [ ] Enum handling consistent

---

## 📋 PHASE 3: Backend Logic Refactoring

### Task 3.1: Refactor Pydantic API Schemas ❌
**Priority:** HIGH  
**Estimated Time:** 3-4 hours

**Objective:** Update FastAPI schemas for new three-table structure

**File:** `apps/core/api/schemas/video_processing_schemas.py`

**Actions:**
1. Create distinct schemas:
   - `VideoResponseSchema`
   - `VideoJobResponseSchema` 
   - `VideoMetadataResponseSchema`
   - `VideoSummarySchema`
   - `VideoUploadResponseSchema`
   - `VideoMetadataUpdateRequestSchema`

2. Ensure proper configuration:
   - `model_config = ConfigDict(from_attributes=True)`
   - Use `ProcessingStatus` enum
   - Proper datetime handling
   - Optional nested relationships

**Verification:**
- [ ] All schemas defined
- [ ] Proper enum usage
- [ ] Datetime fields correct
- [ ] Ready for TypeScript generation

### Task 3.2: Update Repository Layer to Async ❌
**Priority:** HIGH  
**Estimated Time:** 4-5 hours

**Objective:** Convert all repository methods to async and update for new models

**Files:**
- `apps/core/operations/video_repository.py`
- `apps/core/operations/video_job_repository.py`
- `apps/core/operations/video_metadata_repository.py`

**Actions:**
1. Convert all methods to `async def`
2. Update imports to use `apps.core.models`
3. Use `AsyncSession` for all database operations
4. Implement eager loading with `joinedload`
5. Update query patterns for three-table structure

**Key Methods to Update:**
- `VideoJobRepository.get_by_user_id_and_statuses` (critical for frontend)
- All CRUD operations
- Relationship loading

**Verification:**
- [ ] All methods async
- [ ] Proper model imports
- [ ] Eager loading implemented
- [ ] Queries optimized

### Task 3.3: Update Service Layer ❌
**Priority:** HIGH  
**Estimated Time:** 3-4 hours

**Objective:** Adapt services for async repositories and new model structure

**Files:**
- `apps/core/services/video_processing_service.py`
- `apps/core/services/job_service.py`

**Actions:**
1. Update all repository calls to `await`
2. Make service methods `async def`
3. Update background task session management
4. Adapt to three-model workflow
5. Ensure proper error handling

**Critical Updates:**
- `initiate_video_processing`: Create video → job → schedule processing
- `_execute_processing_pipeline`: Manage own session, update job + metadata
- `get_job_details`: Use eager loading, check authorization

**Verification:**
- [ ] All async calls properly awaited
- [ ] Background tasks manage sessions
- [ ] Three-model workflow implemented
- [ ] Authorization checks updated

### Task 3.4: Update API Endpoints ❌
**Priority:** HIGH  
**Estimated Time:** 2-3 hours

**Objective:** Update endpoints for async services and new schemas

**Files:**
- `apps/core/api/endpoints/video_processing_endpoints.py`
- `apps/core/api/endpoints/jobs_endpoints.py`

**Actions:**
1. Make all endpoints `async def`
2. Use `AsyncSession` dependency
3. Update response models to new schemas
4. Ensure proper error handling
5. Test endpoint functionality

**Verification:**
- [ ] All endpoints async
- [ ] Correct response schemas
- [ ] Proper session handling
- [ ] Error handling updated

---

## 📋 PHASE 4: Frontend Type Generation & Updates (Enhanced)

### Task 4.1: Generate TypeScript Types ❌
**Priority:** HIGH  
**Estimated Time:** 1-2 hours

**Objective:** Generate TypeScript interfaces from Pydantic schemas and TanStack Router types

**TanStack Documentation References:**
- **Type Generation**: Automatic TypeScript type generation for routes
- **Route Configuration**: File-based routing with type safety

**Implementation Steps:**
1. **Generate API Types from Backend**:
   ```bash
   cd apps/core
   pnpm codegen:api-types
   ```
   - Verify script targets: `apps.core.api.schemas.video_processing_schemas`
   - Check output: `apps/web/app/types/api.ts`

2. **Generate TanStack Router Types**:
   ```bash
   cd apps/web
   pnpm build:routes
   ```
   - Verify output: `apps/web/app/routeTree.gen.ts`
   - Check route type definitions

3. **Create Comprehensive Type Definitions** (`apps/web/app/types/index.ts`):
   ```typescript
   // Re-export API types
   export * from './api'
   
   // TanStack Router types
   export type { RouterContext } from '../routes/__root'
   
   // Custom application types
   export interface VideoWithJobs {
     id: string
     title: string
     description?: string
     file_path: string
     created_at: string
     updated_at: string
     processing_jobs: VideoProcessingJob[]
   }
   
   export interface ProcessingJobWithDetails {
     id: string
     video_id: string
     status: ProcessingStatus
     processing_type: ProcessingType
     created_at: string
     updated_at: string
     video: Video
     metadata?: ProcessingMetadata
   }
   ```

4. **Verify Type Compatibility**:
   ```typescript
   // Check that generated types match expected structure
   import type { Video, VideoProcessingJob, ProcessingStatus } from '@/types'
   
   // Ensure enum values match backend
   const statusValues: ProcessingStatus[] = [
     'pending', 'processing', 'completed', 'failed'
   ]
   ```

**Validation Criteria:**
- [ ] API types generated successfully from Pydantic schemas
- [ ] TanStack Router types generated correctly
- [ ] ProcessingStatus enum matches backend values
- [ ] All schemas properly represented
- [ ] No TypeScript compilation errors
- [ ] Type imports work with path aliases

### Task 4.2: Update Frontend Code for New Types ❌
**Priority:** HIGH  
**Estimated Time:** 4-6 hours

**Objective:** Update frontend to use new types and TanStack Router patterns

**TanStack Documentation References:**
- **Data Loading**: Loaders, search params, and route context
- **Navigation**: Link components and programmatic navigation
- **Code Splitting**: Route-based lazy loading

**Key Areas to Update:**

1. **API Client Functions** (`apps/web/app/lib/api.ts`):
   ```typescript
   import type { Video, VideoProcessingJob, CreateVideoRequest } from '@/types'
   
   export const api = {
     videos: {
       list: (): Promise<Video[]> => 
         fetch('/api/videos').then(res => res.json()),
       
       get: (id: string): Promise<VideoWithJobs> =>
         fetch(`/api/videos/${id}`).then(res => res.json()),
       
       create: (data: CreateVideoRequest): Promise<Video> =>
         fetch('/api/videos', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(data)
         }).then(res => res.json())
     },
     
     jobs: {
       list: (): Promise<VideoProcessingJob[]> =>
         fetch('/api/video-processing-jobs').then(res => res.json()),
       
       get: (id: string): Promise<ProcessingJobWithDetails> =>
         fetch(`/api/video-processing-jobs/${id}`).then(res => res.json())
     }
   }
   ```

2. **Update Route Components with TanStack Router Patterns**:
   
   **Video List Route** (`apps/web/app/routes/videos/index.tsx`):
   ```typescript
   import { createFileRoute } from '@tanstack/react-router'
   import { useQuery } from '@tanstack/react-query'
   import type { Video } from '@/types'
   
   export const Route = createFileRoute('/videos/')({
     component: VideoListComponent,
     loader: ({ context: { queryClient } }) =>
       queryClient.ensureQueryData({
         queryKey: ['videos'],
         queryFn: () => api.videos.list()
       })
   })
   
   function VideoListComponent() {
     const { data: videos } = useQuery({
       queryKey: ['videos'],
       queryFn: () => api.videos.list()
     })
     
     return (
       <div>
         {videos?.map(video => (
           <VideoCard key={video.id} video={video} />
         ))}
       </div>
     )
   }
   ```

   **Video Detail Route** (`apps/web/app/routes/videos/$videoId.tsx`):
   ```typescript
   import { createFileRoute } from '@tanstack/react-router'
   import { z } from 'zod'
   
   const videoSearchSchema = z.object({
     tab: z.enum(['details', 'processing']).optional()
   })
   
   export const Route = createFileRoute('/videos/$videoId')({
     component: VideoDetailComponent,
     validateSearch: videoSearchSchema,
     loader: ({ params, context: { queryClient } }) =>
       queryClient.ensureQueryData({
         queryKey: ['videos', params.videoId],
         queryFn: () => api.videos.get(params.videoId)
       })
   })
   ```

3. **Update WebSocket Handling** (`apps/web/app/hooks/useJobStatusManager.ts`):
   ```typescript
   import { useCallback, useEffect } from 'react'
   import { useQueryClient } from '@tanstack/react-query'
   import type { VideoProcessingJob, ProcessingStatus } from '@/types'
   
   interface JobStatusUpdate {
     job_id: string
     status: ProcessingStatus
     progress?: number
     error_message?: string
   }
   
   export function useJobStatusManager() {
     const queryClient = useQueryClient()
     
     const handleJobUpdate = useCallback((update: JobStatusUpdate) => {
       // Update specific job query
       queryClient.setQueryData(
         ['jobs', update.job_id],
         (oldData: VideoProcessingJob | undefined) => 
           oldData ? { ...oldData, status: update.status } : undefined
       )
       
       // Invalidate related queries
       queryClient.invalidateQueries({ queryKey: ['jobs'] })
       queryClient.invalidateQueries({ queryKey: ['videos'] })
     }, [queryClient])
     
     return { handleJobUpdate }
   }
   ```

4. **Update Video Components**:
   
   **ProcessingDashboard** (`apps/web/app/components/video/ProcessingDashboard.tsx`):
   ```typescript
   import type { VideoProcessingJob, ProcessingStatus } from '@/types'
   
   interface ProcessingDashboardProps {
     jobs: VideoProcessingJob[]
   }
   
   export function ProcessingDashboard({ jobs }: ProcessingDashboardProps) {
     const pendingJobs = jobs.filter(job => job.status === 'pending')
     const processingJobs = jobs.filter(job => job.status === 'processing')
     const completedJobs = jobs.filter(job => job.status === 'completed')
     const failedJobs = jobs.filter(job => job.status === 'failed')
     
     return (
       <div className="processing-dashboard">
         <JobStatusSection title="Pending" jobs={pendingJobs} />
         <JobStatusSection title="Processing" jobs={processingJobs} />
         <JobStatusSection title="Completed" jobs={completedJobs} />
         <JobStatusSection title="Failed" jobs={failedJobs} />
       </div>
     )
   }
   ```

5. **Update TanStack Query Hooks** (`apps/web/app/hooks/useVideoQueries.ts`):
   ```typescript
   import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
   import type { Video, CreateVideoRequest, VideoWithJobs } from '@/types'
   
   export function useVideos() {
     return useQuery({
       queryKey: ['videos'],
       queryFn: () => api.videos.list()
     })
   }
   
   export function useVideo(videoId: string) {
     return useQuery({
       queryKey: ['videos', videoId],
       queryFn: () => api.videos.get(videoId),
       enabled: !!videoId
     })
   }
   
   export function useCreateVideo() {
     const queryClient = useQueryClient()
     
     return useMutation({
       mutationFn: (data: CreateVideoRequest) => api.videos.create(data),
       onSuccess: () => {
         queryClient.invalidateQueries({ queryKey: ['videos'] })
       }
     })
   }
   ```

**Validation Criteria:**
- [ ] All TypeScript errors resolved
- [ ] Components render correctly with new types
- [ ] Data fetching works with updated API client
- [ ] WebSocket updates function properly
- [ ] TanStack Router navigation works
- [ ] Query invalidation and caching work correctly
- [ ] Route loaders and search params function
- [ ] Error boundaries handle type-related errors

---

## 📋 PHASE 5: TanStack Start Configuration (Enhanced)

### Task 5.1: Verify and Configure TanStack Start Setup ❌
**Priority:** HIGH  
**Estimated Time:** 2-3 hours

**Objective:** Comprehensive verification and configuration of TanStack Start setup

**TanStack Documentation References:**
- **Basic Setup**: Examples > Basic
- **API Routes**: File-based routing conventions with `/api` prefix
- **SSR**: `app/ssr.tsx` with `createStartHandler` configuration
- **Path Aliases**: `vite-tsconfig-paths` plugin setup

**Current Status:** ✅ Basic setup appears correct
- `app/api.ts` exists and configured
- `app/ssr.tsx` exists and configured
- `app.config.ts` has Netlify preset

**Detailed Implementation Steps:**
1. **Verify Dependencies** (`apps/web/package.json`):
   ```json
   {
     "@tanstack/start": "^1.x.x",
     "@tanstack/router": "^1.x.x", 
     "@tanstack/react-query": "^5.x.x",
     "vite-tsconfig-paths": "^4.x.x"
   }
   ```

2. **Check Vite Configuration** (`apps/web/vite.config.ts`):
   ```typescript
   import { defineConfig } from '@tanstack/start/config'
   import tsConfigPaths from 'vite-tsconfig-paths'
   
   export default defineConfig({
     plugins: [tsConfigPaths()],
     ssr: { noExternal: ['@tanstack/start'] }
   })
   ```

3. **Verify Router Setup** (`apps/web/app/router.tsx`):
   ```typescript
   import { createRouter } from '@tanstack/react-router'
   import { routeTree } from './routeTree.gen'
   
   export const router = createRouter({ routeTree })
   ```

**Validation Criteria:**
- [ ] Development server starts: `npm run dev`
- [ ] Route generation works: `routeTree.gen.ts` exists
- [ ] TypeScript compilation succeeds
- [ ] Hot reload functions correctly
- [ ] API routes accessible at `/api/*`

### Task 5.2: Configure API Routes with TanStack Start ❌
**Priority:** HIGH  
**Estimated Time:** 2-3 hours

**Objective:** Set up API routes following TanStack Start conventions

**TanStack Documentation Reference:** API Routes documentation

**Implementation Steps:**
1. **Create API Route Structure**:
   ```
   apps/web/app/routes/api/
   ├── users.ts
   ├── videos.ts
   └── video-processing-jobs.ts
   ```

2. **Implement API Route Pattern** (`apps/web/app/routes/api/users.ts`):
   ```typescript
   import { createAPIFileRoute } from '@tanstack/start/api'
   import { z } from 'zod'
   
   const userSchema = z.object({
     id: z.string(),
     email: z.string().email(),
     created_at: z.string(),
     updated_at: z.string()
   })
   
   export const Route = createAPIFileRoute('/api/users')({
     GET: async ({ request }) => {
       const response = await fetch('http://localhost:8000/api/users')
       const users = await response.json()
       return Response.json(users)
     },
     POST: async ({ request }) => {
       const body = await request.json()
       const validatedData = userSchema.parse(body)
       const response = await fetch('http://localhost:8000/api/users', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(validatedData)
       })
       return Response.json(await response.json())
     }
   })
   ```

3. **Configure Dynamic Routes** (`apps/web/app/routes/api/videos/$videoId.ts`):
   ```typescript
   export const Route = createAPIFileRoute('/api/videos/$videoId')({
     GET: async ({ params }) => {
       const { videoId } = params
       const response = await fetch(`http://localhost:8000/api/videos/${videoId}`)
       return Response.json(await response.json())
     }
   })
   ```

**Validation Criteria:**
- [ ] API routes accessible at `/api/*` endpoints
- [ ] JSON responses work correctly
- [ ] Dynamic parameters function properly
- [ ] Error handling works for invalid requests
- [ ] Backend integration successful

### Task 5.3: Setup React Query Integration ❌
**Priority:** HIGH  
**Estimated Time:** 2-3 hours

**Objective:** Integrate React Query with TanStack Router context

**TanStack Documentation Reference:** React Query integration examples

**Implementation Steps:**
1. **Create Query Client** (`apps/web/app/lib/query-client.ts`):
   ```typescript
   import { QueryClient } from '@tanstack/react-query'
   
   export const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 1000 * 60 * 5, // 5 minutes
         retry: 3,
       },
     },
   })
   ```

2. **Update Root Route** (`apps/web/app/routes/__root.tsx`):
   ```typescript
   import { createRootRouteWithContext } from '@tanstack/react-router'
   import { QueryClient } from '@tanstack/react-query'
   
   interface RouterContext {
     queryClient: QueryClient
   }
   
   export const Route = createRootRouteWithContext<RouterContext>()({
     component: RootComponent,
   })
   ```

3. **Configure Router with Context** (`apps/web/app/router.tsx`):
   ```typescript
   import { createRouter } from '@tanstack/react-router'
   import { queryClient } from './lib/query-client'
   
   export const router = createRouter({
     routeTree,
     context: { queryClient },
   })
   ```

4. **Create API Hooks** (`apps/web/app/lib/api-hooks.ts`):
   ```typescript
   import { useQuery, useMutation } from '@tanstack/react-query'
   
   export const useUsers = () => {
     return useQuery({
       queryKey: ['users'],
       queryFn: () => fetch('/api/users').then(res => res.json())
     })
   }
   
   export const useVideos = () => {
     return useQuery({
       queryKey: ['videos'],
       queryFn: () => fetch('/api/videos').then(res => res.json())
     })
   }
   
   export const useCreateVideo = () => {
     return useMutation({
       mutationFn: (videoData: any) => 
         fetch('/api/videos', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(videoData)
         }).then(res => res.json())
     })
   }
   ```

**Validation Criteria:**
- [ ] React Query DevTools work in development
- [ ] Queries and mutations function correctly
- [ ] Context is available in all route components
- [ ] Caching and invalidation work as expected

### Task 5.4: Configure Supabase Auth Integration ❌
**Priority:** HIGH  
**Estimated Time:** 3-4 hours

**Objective:** Integrate Supabase authentication with TanStack Start

**TanStack Documentation Reference:** Supabase Auth example

**Implementation Steps:**
1. **Create Supabase Client** (`apps/web/app/lib/supabase.ts`):
   ```typescript
   import { createClient } from '@supabase/supabase-js'
   
   const supabaseUrl = process.env.SUPABASE_URL!
   const supabaseAnonKey = process.env.SUPABASE_ANON_KEY!
   
   export const supabase = createClient(supabaseUrl, supabaseAnonKey)
   ```

2. **Create Auth Server Functions** (`apps/web/app/lib/auth.server.ts`):
   ```typescript
   import { createServerFn } from '@tanstack/start'
   import { supabase } from './supabase'
   
   export const getUser = createServerFn('GET', async () => {
     const { data: { user } } = await supabase.auth.getUser()
     return user
   })
   
   export const signIn = createServerFn('POST', async (credentials: {
     email: string
     password: string
   }) => {
     const { data, error } = await supabase.auth.signInWithPassword(credentials)
     if (error) throw error
     return data
   })
   
   export const signOut = createServerFn('POST', async () => {
     const { error } = await supabase.auth.signOut()
     if (error) throw error
     return { success: true }
   })
   ```

3. **Create Protected Route Pattern** (`apps/web/app/routes/_authenticated.tsx`):
   ```typescript
   import { createFileRoute, redirect } from '@tanstack/react-router'
   import { getUser } from '@/lib/auth.server'
   
   export const Route = createFileRoute('/_authenticated')({
     beforeLoad: async () => {
       const user = await getUser()
       if (!user) {
         throw redirect({ to: '/login' })
       }
       return { user }
     },
   })
   ```

**Validation Criteria:**
- [ ] User authentication works correctly
- [ ] Protected routes redirect unauthenticated users
- [ ] Auth state persists across page refreshes
- [ ] Server functions handle auth correctly

### Task 5.5: Setup Error Boundaries and Route Handling ❌
**Priority:** MEDIUM  
**Estimated Time:** 1-2 hours

**Objective:** Implement comprehensive error handling

**TanStack Documentation Reference:** Error Handling documentation

**Implementation Steps:**
1. **Create Error Component** (`apps/web/app/components/error-boundary.tsx`):
   ```typescript
   import { ErrorComponent } from '@tanstack/react-router'
   
   export function DefaultErrorComponent({ error }: { error: Error }) {
     return (
       <div className="error-boundary">
         <h2>Something went wrong</h2>
         <p>{error.message}</p>
         <button onClick={() => window.location.reload()}>
           Reload Page
         </button>
       </div>
     )
   }
   ```

2. **Configure Root Error Handling** (`apps/web/app/routes/__root.tsx`):
   ```typescript
   export const Route = createRootRouteWithContext<RouterContext>()({
     component: RootComponent,
     errorComponent: DefaultErrorComponent,
     notFoundComponent: () => <div>Page not found</div>,
   })
   ```

3. **Create Route-Specific Error Handling**:
   ```typescript
   export const Route = createFileRoute('/videos')({
     component: VideosComponent,
     errorComponent: ({ error }) => (
       <div>Error loading videos: {error.message}</div>
     ),
   })
   ```

**Validation Criteria:**
- [ ] Error boundaries catch and display errors gracefully
- [ ] 404 pages show for non-existent routes
- [ ] Route-specific errors don't crash the entire app
- [ ] Error messages are user-friendly

### Task 5.6: Configure Path Aliases ❌
**Priority:** MEDIUM  
**Estimated Time:** 30 minutes

**Objective:** Set up path aliases for clean imports

**TanStack Documentation Reference:** Path Aliases documentation

**Implementation Steps:**
1. **Update TypeScript Config** (`apps/web/tsconfig.json`):
   ```json
   {
     "compilerOptions": {
       "baseUrl": ".",
       "paths": {
         "@/*": ["./app/*"],
         "@/components/*": ["./app/components/*"],
         "@/lib/*": ["./app/lib/*"],
         "@/services/*": ["./app/services/*"],
         "@/types/*": ["./app/types/*"]
       }
     }
   }
   ```

2. **Verify Vite Plugin** (`vite.config.ts`):
   ```typescript
   import tsConfigPaths from 'vite-tsconfig-paths'
   
   export default defineConfig({
     plugins: [tsConfigPaths()]
   })
   ```

**Validation Criteria:**
- [ ] Import statements work with aliases
- [ ] TypeScript recognizes aliases without errors
- [ ] Build process resolves aliases correctly

---

## 📋 PHASE 6: Testing & Validation

### Task 6.1: Update Backend Tests ❌
**Priority:** MEDIUM  
**Estimated Time:** 3-4 hours

**Objective:** Ensure all backend tests pass with new async structure

**Files:** All test files in `apps/core/tests/`

**Actions:**
1. Update repository tests for async methods
2. Update service tests for async calls
3. Update API tests for new schemas
4. Fix test fixtures for new models
5. Ensure async session usage in tests

**Verification:**
- [ ] All tests pass
- [ ] Coverage maintained
- [ ] Async patterns tested

### Task 6.2: Frontend Testing ❌
**Priority:** LOW  
**Estimated Time:** 2-3 hours

**Objective:** Update frontend tests for new types and components

**Actions:**
1. Update component tests
2. Fix type-related test issues
3. Test API integration
4. Verify WebSocket functionality

---

## 🚀 EXECUTION STRATEGY

### Recommended Order:
1. **Phase 2 Remaining** (2.2, 2.5) - Complete code generation
2. **Phase 3** (3.1-3.4) - Backend refactoring (critical path)
3. **Phase 4** (4.1-4.2) - Frontend updates
4. **Phase 5** (5.1-5.2) - TanStack Start fixes
5. **Phase 6** (6.1-6.2) - Testing

### Critical Dependencies:
- Phase 3 must complete before Phase 4.1
- Phase 4.1 must complete before Phase 4.2
- Backend testing (6.1) should follow Phase 3
- Frontend testing (6.2) should follow Phase 4

### Risk Mitigation:
- Test each phase thoroughly before proceeding
- Keep database backup before major changes
- Use feature branches for large refactors
- Verify type generation at each step

---

## 📊 SUCCESS METRICS

- [ ] All backend endpoints async and functional
- [ ] TypeScript types generated and accurate
- [ ] Frontend compiles without errors
- [ ] End-to-end data flow working
- [ ] TanStack Start development environment stable
- [ ] All tests passing
- [ ] Type safety maintained throughout stack 