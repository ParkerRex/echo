# Echo Project Frontend Integration - Session 3 Continuation Prompt

## 🎯 PROJECT CONTEXT

You are continuing work on the **Echo** project, a video processing platform with a Python FastAPI backend and TypeScript TanStack Start frontend. **Major progress has been made** - the critical TanStack Start package migration is complete and both backend and frontend servers are now operational.

### Current Status:
- **Backend**: ✅ **FULLY OPERATIONAL** (FastAPI server on port 8000, all async endpoints working)
- **Type Generation**: ✅ **COMPLETE** (14 TypeScript interfaces + 1 enum generated)
- **Frontend Core**: ✅ **WORKING** (TanStack Start migration complete, dev server starts on port 3001)
- **Frontend Auth**: ❌ **BLOCKED** (Supabase client configuration issues)
- **Frontend Integration**: ❌ **PENDING** (Generated types not yet integrated)

## 🚀 MAJOR ACCOMPLISHMENTS (Session 2)

### ✅ TanStack Start Migration - COMPLETE
- **Package Migration**: Successfully migrated from `@tanstack/start` to `@tanstack/react-start`
- **Import Updates**: Fixed all import statements across the codebase
- **SSR Configuration**: Updated `apps/web/app/ssr.tsx` with correct imports
- **Development Server**: Frontend now starts successfully on port 3001
- **Deprecation Warnings**: Eliminated all package deprecation warnings

### ✅ Development Environment - OPERATIONAL
- **Backend Server**: Running on http://localhost:8000 (FastAPI with async endpoints)
- **Frontend Server**: Running on http://localhost:3001 (TanStack Start with SSR)
- **Type Generation**: Working perfectly with `pnpm codegen:api-types`
- **Local Development**: New `scripts/dev-local.sh` script for local development

## 🚨 CURRENT BLOCKERS (HIGH PRIORITY)

### Issue 1: Supabase Client Configuration ⚠️
**Error:** `Module '"@echo/db/clients/ssr"' has no exported member 'getSupabaseServerClient'`  
**Files Affected:**
- `apps/web/app/routes/logout.tsx`
- `apps/web/app/services/auth.api.ts`

**Root Cause:** Missing or incorrect Supabase client exports in shared package

### Issue 2: TanStack Start Middleware API ⚠️
**Error:** `Object literal may only specify known properties, and 'type' does not exist in type`  
**File:** `apps/web/app/services/auth.api.ts`  
**Root Cause:** TanStack Start middleware API has changed, old patterns no longer valid

## 📁 PROJECT STRUCTURE
```
echo/
├── apps/
│   ├── core/           # ✅ Python FastAPI backend (WORKING - Port 8000)
│   │   ├── api/        # ✅ FastAPI endpoints and schemas
│   │   ├── models/     # ✅ SQLAlchemy models
│   │   ├── bin/        # ✅ Custom type generation script
│   │   └── main.py     # ✅ FastAPI app entry point
│   └── web/            # 🟡 TypeScript TanStack Start frontend (PARTIALLY WORKING - Port 3001)
│       ├── app/        # Frontend application code
│       │   ├── components/
│       │   ├── routes/
│       │   ├── services/ # ❌ Auth services have import errors
│       │   ├── types/  # ✅ Generated TypeScript types (api.ts)
│       │   ├── ssr.tsx # ✅ Fixed SSR configuration
│       │   └── router.tsx
│       ├── package.json # ✅ Updated to @tanstack/react-start
│       └── app.config.ts # ✅ Updated configuration
├── packages/
│   └── db/             # ❌ Supabase client exports missing
│       └── clients/    # ❌ SSR client not properly exported
├── scripts/
│   └── dev-local.sh    # ✅ New local development script
└── package.json        # Root package.json
```

## 🎯 IMMEDIATE TASKS (CRITICAL PATH)

### Task 1: Fix Supabase Client Configuration (HIGH)
**Priority:** HIGH  
**Objective:** Resolve missing Supabase client exports and configuration

**Current Errors:**
```typescript
// apps/web/app/routes/logout.tsx
import { getSupabaseServerClient } from "@echo/db/clients/ssr";
// Error: Module has no exported member 'getSupabaseServerClient'

// apps/web/app/services/auth.api.ts  
import { getSupabaseServerClient } from "~/lib/supabase"
// Error: Cannot find module '~/lib/supabase'
```

**Actions Required:**
1. **Investigate Supabase client package structure:**
   ```bash
   ls -la packages/db/clients/
   cat packages/db/clients/ssr.ts  # Check exports
   ```

2. **Fix or create missing exports:**
   - Verify `packages/db/clients/ssr.ts` exports `getSupabaseServerClient`
   - If missing, create the export function
   - Ensure proper TypeScript types

3. **Create local Supabase client:**
   - Create `apps/web/app/lib/supabase.ts` with proper client setup
   - Update import paths in auth services
   - Use environment variables for configuration

4. **Update auth service imports:**
   - Fix `apps/web/app/services/auth.api.ts`
   - Fix `apps/web/app/routes/logout.tsx`
   - Ensure consistent import patterns

**Verification Steps:**
- [ ] Supabase client imports resolve correctly
- [ ] Auth services compile without errors
- [ ] Server functions can access Supabase client
- [ ] TypeScript compilation succeeds

### Task 2: Fix TanStack Start Middleware API (HIGH)
**Priority:** HIGH  
**Estimated Time:** 1-2 hours  
**Objective:** Update middleware to use current TanStack Start API

**Current Error:**
```typescript
// apps/web/app/services/auth.api.ts
export const userMiddleware = createMiddleware({ type: "function" }).server(
// Error: 'type' does not exist in type
```

**Actions Required:**
1. **Research current TanStack Start middleware API:**
   - Check latest TanStack Start documentation
   - Look for `createMiddleware` usage examples
   - Identify correct parameter structure

2. **Update middleware configuration:**
   - Remove deprecated `type: "function"` parameter
   - Use correct middleware configuration syntax
   - Update server function patterns

3. **Fix auth middleware in `apps/web/app/services/auth.api.ts`:**
   - Update `userMiddleware` configuration
   - Update `userRequiredMiddleware` configuration
   - Ensure middleware chaining works correctly

4. **Test middleware functionality:**
   - Verify user authentication works
   - Test protected route access
   - Check middleware context passing

**Verification Steps:**
- [ ] Middleware compiles without errors
- [ ] Authentication flow works correctly
- [ ] Protected routes function properly
- [ ] Middleware context is accessible

### Task 3: Integrate Generated TypeScript Types (MEDIUM)
**Priority:** MEDIUM  
**Estimated Time:** 2-3 hours  
**Objective:** Use generated TypeScript types throughout frontend

**Generated Types Available:**
- **File:** `apps/web/app/types/api.ts`
- **Contains:** 14 interfaces + 1 enum (ProcessingStatus)
- **Generated from:** Backend Pydantic schemas

**Actions Required:**
1. **Create API client with typed functions:**
   ```typescript
   // apps/web/app/lib/api.ts
   import type { Video, VideoProcessingJob, CreateVideoRequest } from '@/types/api'
   
   export const api = {
     videos: {
       list: (): Promise<Video[]> => 
         fetch('/api/videos').then(res => res.json()),
       get: (id: string): Promise<Video> =>
         fetch(`/api/videos/${id}`).then(res => res.json()),
       create: (data: CreateVideoRequest): Promise<Video> =>
         fetch('/api/videos', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(data)
         }).then(res => res.json())
     }
   }
   ```

2. **Update component props and state:**
   - Import types from `@/types/api`
   - Update component interfaces
   - Fix TypeScript compilation errors

3. **Create typed React Query hooks:**
   ```typescript
   // apps/web/app/hooks/useVideoQueries.ts
   import { useQuery } from '@tanstack/react-query'
   import type { Video } from '@/types/api'
   
   export function useVideos() {
     return useQuery({
       queryKey: ['videos'],
       queryFn: () => api.videos.list()
     })
   }
   ```

**Verification Steps:**
- [ ] TypeScript compilation succeeds
- [ ] API calls use correct types
- [ ] Components render without errors
- [ ] Type safety maintained throughout

### Task 4: Development Environment Consolidation (MEDIUM)
**Priority:** MEDIUM  
**Objective:** Ensure consistent development environment setup

**Actions Required:**
1. **Test the new local development script:**
   ```bash
   # Use the new local development approach
   pnpm dev  # Should use scripts/dev-local.sh
   ```

2. **Verify both servers start correctly:**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3001

3. **Update documentation:**
   - Update README.md with new development commands
   - Document the local vs Docker development approaches

## 🔧 DEVELOPMENT COMMANDS

### Current Working Commands:
```bash
# Backend (already working)
cd apps/core && bash bin/dev.sh  # Runs on http://localhost:8000

# Frontend (now working)
cd apps/web && pnpm dev  # Runs on http://localhost:3001

# Type generation (working)
pnpm codegen:api-types  # Generates TypeScript types
```

### Environment Status:
- **Backend Server**: ✅ Running on http://localhost:8000
- **Frontend Server**: ✅ Running on http://localhost:3001  
- **Supabase Local**: ✅ Running on http://localhost:54321
- **Type Generation**: ✅ Working perfectly

## 📚 REFERENCE DOCUMENTATION

### Key Files to Reference:
- `apps/web/app/types/api.ts` - Generated TypeScript types (ready to use)
- `apps/core/api/schemas/video_processing_schemas.py` - Source Pydantic schemas
- `packages/db/clients/` - Supabase client configuration
- `.ai/doing/backend-frontend-sync-tasks.md` - Updated task list

### TanStack Start Resources:
- **Middleware Documentation**: Check latest TanStack Start docs for `createMiddleware`
- **Server Functions**: Current patterns for server-side functions
- **Auth Integration**: Examples of authentication middleware

## 🚀 SUCCESS CRITERIA

1. **Auth Services Work**: Supabase client imports resolve and auth functions compile
2. **Middleware Functions**: TanStack Start middleware works without errors
3. **Type Integration**: Generated types are used throughout frontend
4. **Full Compilation**: No TypeScript errors in frontend
5. **Basic Functionality**: Can navigate routes and make API calls
6. **Development Environment**: Consistent and reliable startup process

## 🔍 DEBUGGING TIPS

- **Check Package Structure**: Use `ls -la packages/db/clients/` to verify exports
- **Test Incrementally**: Fix Supabase client first, then middleware, then types
- **Use TypeScript Compiler**: Run `tsc --noEmit` to check for type errors
- **Check Network Tab**: Verify API calls to backend work (http://localhost:8000)
- **Console Logs**: Monitor browser console for runtime errors

## 📊 CURRENT ENVIRONMENT

- **Backend Server**: ✅ Running on http://localhost:8000
- **Frontend Server**: ✅ Running on http://localhost:3001
- **API Documentation**: ✅ Available at http://localhost:8000/docs
- **Generated Types**: ✅ Available in `apps/web/app/types/api.ts`
- **Supabase Local**: ✅ Running on http://localhost:54321

## 🎯 EXECUTION STRATEGY

1. **Start with Task 1** (Supabase Client) - This blocks authentication
2. **Move to Task 2** (Middleware API) - This enables auth functionality  
3. **Complete Task 3** (Type Integration) - This provides full type safety
4. **Finish with Task 4** (Environment) - This ensures consistent development

**Remember**: The major blockers (TanStack Start migration) are resolved. Focus on the remaining integration issues to achieve full functionality.

---

**The foundation is solid - now let's complete the integration!** 🚀 
