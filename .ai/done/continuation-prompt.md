# Echo Project Frontend Migration - Continuation Prompt

## 🎯 PROJECT CONTEXT

You are continuing work on the **Echo** project, a video processing platform with a Python FastAPI backend and TypeScript TanStack Start frontend. The backend is **fully operational** and type generation is working perfectly. The critical blocker is migrating the frontend from the deprecated `@tanstack/start` package to the new `@tanstack/react-start` package.

### Current Status:
- **Backend**: ✅ **FULLY OPERATIONAL** (FastAPI server on port 8000, all async endpoints working)
- **Type Generation**: ✅ **COMPLETE** (14 TypeScript interfaces + 1 enum generated)
- **Frontend**: ❌ **BLOCKED** (Cannot start due to package migration needed)

## 🚨 CRITICAL ISSUE

**Error:** `Cannot find module '@tanstack/react-start/router-manifest'`  
**Root Cause:** TanStack Start has moved from `@tanstack/start` to `@tanstack/react-start`  
**Impact:** Frontend development server fails to start with 500 SSR error  
**Priority:** CRITICAL - Blocks all frontend development

## 📁 PROJECT STRUCTURE

```
echo/
├── apps/
│   ├── core/           # ✅ Python FastAPI backend (WORKING)
│   │   ├── api/        # ✅ FastAPI endpoints and schemas
│   │   ├── models/     # ✅ SQLAlchemy models
│   │   ├── bin/        # ✅ Custom type generation script
│   │   └── main.py     # ✅ FastAPI app entry point
│   └── web/            # ❌ TypeScript TanStack Start frontend (BLOCKED)
│       ├── app/        # Frontend application code
│       │   ├── components/
│       │   ├── routes/
│       │   ├── types/  # ✅ Generated TypeScript types (api.ts)
│       │   ├── ssr.tsx # ❌ NEEDS PACKAGE MIGRATION
│       │   └── router.tsx
│       ├── package.json # ❌ NEEDS DEPENDENCY UPDATE
│       └── vite.config.ts
├── package.json        # Root package.json
└── pnpm-workspace.yaml
```

## 🎯 IMMEDIATE TASKS (CRITICAL PATH)

### Task 1: Migrate TanStack Start Package (CRITICAL)
**Priority:** CRITICAL  
**Estimated Time:** 1-2 hours  
**Objective:** Update frontend to use new `@tanstack/react-start` package

**Current Error Log:**
```
[@tanstack/start] Warning: This package has moved to @tanstack/react-start. Please switch to the new package, as this package will be dropped soon.
Cannot find module '@tanstack/react-start/router-manifest' imported from '/Users/parkerrex/Developer/echo/apps/web/app/ssr.tsx'
```

**Actions Required:**
1. **Update `apps/web/package.json` dependencies:**
   ```json
   {
     "dependencies": {
       "@tanstack/react-start": "^1.111.7",  // Replace @tanstack/start
       "@tanstack/react-router": "^1.111.7",
       "@tanstack/react-query": "^5.66.9"
     }
   }
   ```

2. **Update import statements in these files:**
   - `apps/web/app/ssr.tsx` - SSR configuration
   - `apps/web/app/router.tsx` - Router setup
   - `apps/web/vite.config.ts` - Vite configuration
   - `apps/web/app.config.ts` - App configuration (if exists)

3. **Search for all imports from `@tanstack/start` and update to `@tanstack/react-start`**

**Verification Steps:**
- [ ] Package.json updated with new dependencies
- [ ] All import statements updated
- [ ] `pnpm install` runs successfully
- [ ] Frontend server starts: `cd apps/web && pnpm dev`
- [ ] No module resolution errors
- [ ] SSR functionality works

### Task 2: Fix Frontend SSR Configuration (HIGH)
**Priority:** HIGH  
**Estimated Time:** 1-2 hours  
**Objective:** Resolve SSR module resolution issues after package migration

**Files to Check:**
- `apps/web/app/ssr.tsx` - Main SSR configuration
- `apps/web/app/router.tsx` - Router setup
- `apps/web/vite.config.ts` - Vite configuration

**Actions:**
1. Update SSR imports to use new package structure
2. Verify router manifest configuration
3. Check for any deprecated API usage in TanStack Start
4. Test SSR functionality

**Verification:**
- [ ] SSR module loads without errors
- [ ] Router manifest resolves correctly
- [ ] Frontend serves pages successfully at http://localhost:3000

### Task 3: Update Frontend Code for Generated Types (MEDIUM)
**Priority:** MEDIUM  
**Estimated Time:** 2-3 hours  
**Objective:** Use generated TypeScript types in frontend components

**Generated Types Available:**
- File: `apps/web/app/types/api.ts`
- Contains: 14 interfaces + 1 enum (ProcessingStatus)
- Generated from: Backend Pydantic schemas

**Files to Update:**
- `apps/web/app/lib/api.ts` - API client functions
- `apps/web/app/components/video/` - Video components
- `apps/web/app/routes/` - Route components

**Actions:**
1. Import types from `@/types/api`
2. Update API calls to match new backend schemas
3. Fix TypeScript compilation errors
4. Update component props and state types

## 🔧 DEVELOPMENT COMMANDS

### Backend (Already Working):
```bash
# Start backend server (already working)
pnpm dev:api  # Runs on http://localhost:8000

# Generate TypeScript types (already working)
pnpm codegen:api-types
```

### Frontend (Currently Broken):
```bash
# Install dependencies (after package.json update)
cd apps/web && pnpm install

# Start frontend server (currently fails)
cd apps/web && pnpm dev  # Should run on http://localhost:3000
```

## 📚 REFERENCE DOCUMENTATION

### TanStack Start Migration Guide
- **Package Migration**: `@tanstack/start` → `@tanstack/react-start`
- **Import Changes**: Update all imports to new package
- **API Compatibility**: Most APIs should remain the same
- **SSR Configuration**: `createStartHandler` should work with new package

### Key Files to Reference:
- `apps/web/app/types/api.ts` - Generated TypeScript types (ready to use)
- `apps/core/api/schemas/video_processing_schemas.py` - Source Pydantic schemas
- `.ai/done/session-2-backend-completion.md` - Summary of completed backend work

## 🚀 SUCCESS CRITERIA

1. **Frontend Server Starts**: `cd apps/web && pnpm dev` runs without errors
2. **No Module Errors**: All `@tanstack/react-start` imports resolve correctly
3. **SSR Works**: Pages render server-side without errors
4. **TypeScript Compiles**: No compilation errors in frontend
5. **Basic Navigation**: Can navigate between routes
6. **API Integration**: Can make calls to backend (http://localhost:8000)

## 🔍 DEBUGGING TIPS

- **Check Package Versions**: Ensure compatible versions of TanStack packages
- **Verify Imports**: Search for any remaining `@tanstack/start` imports
- **Test Incrementally**: Fix package migration first, then SSR, then types
- **Use Browser DevTools**: Check for runtime errors after server starts
- **Check Network Tab**: Verify API calls to backend work

## 📊 CURRENT ENVIRONMENT

- **Backend Server**: ✅ Running on http://localhost:8000
- **API Documentation**: ✅ Available at http://localhost:8000/docs
- **Generated Types**: ✅ Available in `apps/web/app/types/api.ts`
- **Frontend Server**: ❌ Blocked by package migration

## 🎯 EXECUTION STRATEGY

1. **Start with Task 1** (Package Migration) - This is the critical blocker
2. **Test after each change** - Verify frontend server starts
3. **Move to Task 2** (SSR Configuration) - Only after Task 1 is complete
4. **Complete Task 3** (Type Integration) - Final step for full functionality

**Remember**: The backend is fully operational and type generation is working perfectly. The only blocker is the frontend package migration. Once that's resolved, the project should be fully functional end-to-end.

---

**Start with updating the package.json dependencies and imports. The backend is ready and waiting!** 🚀 