# LLM Execution Prompt for Echo Project Backend-Frontend Synchronization

## 🎯 PROJECT CONTEXT

You are working on the **Echo** project, a video processing platform with a Python FastAPI backend and TypeScript TanStack Start frontend. The project uses:

- **Backend**: Python 3.13, FastAPI, SQLAlchemy (async), Supabase PostgreSQL
- **Frontend**: TypeScript, TanStack Start, TanStack Router, TanStack Query, React
- **Database**: 3-table structure (videos, video_jobs, video_metadata)
- **Environment**: Local Supabase instance running on ports 54321/54322

## 📋 YOUR MISSION

Complete the backend-frontend synchronization to achieve **end-to-end type safety** between Python Pydantic schemas and TypeScript interfaces. The database schema migration is complete, but the application code needs to be refactored for the new 3-table structure and converted to async patterns.

## 🗂️ PROJECT STRUCTURE

```
echo/
├── apps/
│   ├── core/           # Python FastAPI backend
│   │   ├── api/        # FastAPI endpoints and schemas
│   │   ├── models/     # SQLAlchemy models
│   │   ├── operations/ # Repository layer
│   │   ├── services/   # Business logic
│   │   └── tests/      # Backend tests
│   └── web/            # TypeScript TanStack Start frontend
│       ├── app/        # Frontend application code
│       │   ├── components/
│       │   ├── routes/
│       │   ├── lib/
│       │   └── types/
│       └── package.json
├── packages/
│   └── supabase/       # Database migrations and types
└── scripts/            # Code generation scripts
```

## 📚 CRITICAL DOCUMENTATION REFERENCES

### TanStack Start Patterns
- **API Routes**: File-based routing with `/api` prefix and entry handlers
- **SSR Setup**: `createStartHandler` configuration in `app/ssr.tsx`
- **Server Functions**: Server-side functions with validation and context
- **React Query Integration**: `createRootRouteWithContext<{ queryClient: QueryClient }>` pattern

### TanStack Router Patterns  
- **Type Generation**: Automatic TypeScript generation (`routeTree.gen.ts`)
- **Data Loading**: Route loaders with React Query integration
- **Search Params**: Type-safe validation with Zod schemas
- **Error Handling**: Route-level error boundaries

## 🎯 EXECUTION TASKS

### PHASE 1: Backend Async Refactoring (CRITICAL PATH)

#### Task 1.1: Update Pydantic API Schemas
**File**: `apps/core/api/schemas/video_processing_schemas.py`

**Requirements**:
- Create distinct schemas for 3-table structure:
  - `VideoResponseSchema`
  - `VideoJobResponseSchema` 
  - `VideoMetadataResponseSchema`
  - `VideoSummarySchema`
  - `VideoUploadResponseSchema`
- Use `model_config = ConfigDict(from_attributes=True)`
- Import and use `ProcessingStatus` enum from models
- Ensure proper datetime handling with ISO format

#### Task 1.2: Convert Repository Layer to Async
**Files**: 
- `apps/core/operations/video_repository.py`
- `apps/core/operations/video_job_repository.py`
- `apps/core/operations/video_metadata_repository.py`

**Requirements**:
- Convert ALL methods to `async def`
- Use `AsyncSession` for database operations
- Import models from `apps.core.models`
- Implement eager loading with `joinedload()` for relationships
- Critical method: `VideoJobRepository.get_by_user_id_and_statuses()` (used by frontend)

#### Task 1.3: Update Service Layer
**Files**:
- `apps/core/services/video_processing_service.py`
- `apps/core/services/job_service.py`

**Requirements**:
- Make all service methods `async def`
- Add `await` to all repository calls
- Update background task session management
- Adapt workflow for 3-table structure: video → job → metadata
- Ensure proper error handling and session cleanup

#### Task 1.4: Update API Endpoints
**Files**:
- `apps/core/api/endpoints/video_processing_endpoints.py`
- `apps/core/api/endpoints/jobs_endpoints.py`

**Requirements**:
- Convert endpoints to `async def`
- Use `AsyncSession` dependency
- Update response models to new schemas
- Test all endpoints manually after changes

### PHASE 2: Frontend Type Generation & Updates

#### Task 2.1: Generate TypeScript Types
**Commands to run**:
```bash
cd apps/core && pnpm codegen:api-types
cd apps/web && pnpm build:routes
```

**Verification**:
- Check `apps/web/app/types/api.ts` for generated types
- Verify `apps/web/app/routeTree.gen.ts` exists
- Ensure `ProcessingStatus` enum values match backend

#### Task 2.2: Update Frontend Code
**Files to update**:
- `apps/web/app/lib/api.ts` - API client functions
- `apps/web/app/components/video/` - Video components
- `apps/web/app/hooks/` - React Query hooks
- Route components in `apps/web/app/routes/`

**Requirements**:
- Import types from `@/types`
- Update API calls to match new backend schemas
- Fix TypeScript compilation errors
- Ensure TanStack Router patterns are followed

### PHASE 3: TanStack Start Configuration

#### Task 3.1: Verify API Routes
**Check**: `apps/web/app/routes/api/` directory structure
- Ensure API routes proxy to backend correctly
- Test `/api/videos` and `/api/video-processing-jobs` endpoints
- Verify error handling in API routes

#### Task 3.2: React Query Integration
**Files**:
- `apps/web/app/lib/query-client.ts`
- `apps/web/app/routes/__root.tsx`
- `apps/web/app/router.tsx`

**Requirements**:
- Ensure QueryClient is properly configured in router context
- Verify route loaders work with React Query
- Test query invalidation and caching

## 🔧 DEVELOPMENT COMMANDS

### Backend Development
```bash
cd apps/core
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Frontend Development  
```bash
cd apps/web
npm run dev
```

### Database
```bash
pnpm supabase:start  # Start local Supabase
pnpm supabase:stop   # Stop local Supabase
```

### Code Generation
```bash
cd apps/core && pnpm codegen:api-types      # Generate TS types from Pydantic
cd apps/web && pnpm build:routes            # Generate TanStack Router types
```

## ✅ SUCCESS CRITERIA

1. **Backend**: All endpoints are async and return correct schemas
2. **Types**: TypeScript types generated without errors
3. **Frontend**: Compiles without TypeScript errors
4. **Integration**: End-to-end data flow works (create video → process → display)
5. **Development**: Both dev servers start and hot reload works

## 🚨 CRITICAL NOTES

- **Database is already migrated** - do NOT run migrations
- **Environment is configured** - use existing `.env` file
- **Focus on code refactoring** - not infrastructure changes
- **Test incrementally** - verify each phase before proceeding
- **Maintain type safety** - ensure TypeScript compilation succeeds

## 🔍 DEBUGGING TIPS

- Check `apps/core/app/main.py` for FastAPI app configuration
- Verify imports use `apps.core.models` not relative imports
- Ensure async session handling in repositories
- Check TanStack Router route generation with `pnpm build:routes`
- Use browser dev tools to verify API responses match schemas

## 📞 WHEN TO ASK FOR HELP

- If database connection issues arise
- If code generation scripts fail
- If you encounter unfamiliar TanStack patterns
- If async/await patterns seem incorrect
- If TypeScript errors are unclear

---

**Start with Phase 1 (Backend Async Refactoring) as it's the critical path. Each task should be completed and tested before moving to the next.** 