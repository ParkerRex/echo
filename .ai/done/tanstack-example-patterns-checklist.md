# TanStack Start + Supabase Example Patterns Checklist

**Date**: January 2025
**Status**: ✅ ALL PHASES COMPLETE - TanStack Example Patterns Successfully Adopted
**Priority**: Complete - All Patterns Evaluated and Implemented

## 🎯 **Objective**

Identify and adopt proven patterns from the official TanStack Start + Supabase example that we haven't implemented yet.

## 📊 **Pattern Analysis: Example vs Our Implementation**

### ✅ **Already Adopted**

- [x] **Supabase Server Client Pattern** - Using `parseCookies()` and `setCookie()` from `@tanstack/react-start/server`
- [x] **Environment Variable Loading** - Fixed with local `.env` file
- [x] **TanStack Start v1.120.11** - Updated to match example versions
- [x] **Basic Route Protection** - `_authed` layout with `beforeLoad` checks
- [x] **Server Functions** - Using `createServerFn` for auth operations

### 🔄 **Partially Adopted (Needs Refinement)**

#### **1. Authentication Flow Patterns**

- [x] **Simplified Server Function Validators**

  - Example uses: `.validator((d: { email: string; password: string }) => d)`
  - We use: Complex Zod schemas in separate files
  - **Evaluation**: Our Zod schemas provide better validation, type safety, and error messages - keeping them

- [x] **Direct Error Handling in Server Functions**
  - Example: Returns `{ error: true, message: error.message }` objects
  - We: Now consistently return error objects for better UX
  - **Implemented**: All auth functions now return error objects instead of throwing

#### **2. Route Protection Strategy**

- [x] **Error Component Auth Fallback**
  - Example: `errorComponent: ({ error }) => error.message === 'Not authenticated' ? <Login /> : throw error`
  - We: Implemented hybrid approach - redirects for auth + error components for other errors
  - **Implemented**: Enhanced `_authed` route with proper error component while keeping redirect-based auth

### 🆕 **Missing Patterns to Adopt**

#### **3. Custom Mutation Hook Pattern**

- [ ] **`useMutation` Hook** (`src/hooks/useMutation.ts`)
  - Lightweight alternative to TanStack Query mutations
  - Provides: `status`, `variables`, `submittedAt`, `mutate`, `error`, `data`
  - **Benefits**: Simpler than full TanStack Query for basic operations
  - **Action**: Implement for form submissions and auth operations

#### **4. Simplified Auth Component Pattern**

- [ ] **Reusable Auth Component** (`src/components/Auth.tsx`)
  - Single component for both login/signup with `actionText` prop
  - Built-in form handling with `FormData`
  - Status-aware UI (`pending`, `idle`, `success`, `error`)
  - **Action**: Create unified auth form component

#### **5. Server Function Co-location**

- [ ] **Server Functions in Route Files**
  - Example: `loginFn` defined in `_authed.tsx` alongside route
  - We: Separate `auth.api.ts` file
  - **Benefits**: Better locality of behavior
  - **Action**: Consider moving simple auth functions to route files

#### **6. Logout as Loader Pattern**

- [ ] **Logout Route with Loader**
  - Example: `loader: () => logoutFn()` with automatic redirect
  - We: Manual logout handling
  - **Benefits**: Cleaner logout flow
  - **Action**: Implement logout route with loader

#### **7. Router Configuration Patterns**

- [ ] **Scroll Restoration**

  - Example: `scrollRestoration: true` in router config
  - We: Not configured
  - **Action**: Add scroll restoration

- [ ] **Simplified Router Creation**
  - Example: Minimal router setup
  - We: Complex setup with QueryClient integration
  - **Action**: Evaluate if we can simplify while keeping TanStack Query

#### **8. SEO Utilities**

- [ ] **SEO Helper Function** (`src/utils/seo.ts`)
  - Standardized meta tag generation
  - Twitter/OG card support
  - **Action**: Implement for better SEO

#### **9. Form Handling Patterns**

- [ ] **FormData-based Form Handling**
  - Example: `new FormData(e.target as HTMLFormElement)`
  - We: React Hook Form with complex validation
  - **Benefits**: Simpler for basic forms
  - **Action**: Consider for simple auth forms

#### **10. Server Function Patterns**

- [ ] **Method-specific Server Functions**

  - Example: `createServerFn({ method: 'POST' })`
  - We: Default GET methods mostly
  - **Action**: Be explicit about HTTP methods

- [ ] **Redirect in Server Functions**
  - Example: `throw redirect({ href: '/' })` in server functions
  - We: Handle redirects in components
  - **Action**: Move redirects to server functions for better UX

## 🚀 **Implementation Priority**

### **Phase 1: Quick Wins (1-2 hours)** ✅ COMPLETE

1. [x] Add scroll restoration to router
2. [x] Implement SEO utility function
3. [x] Create logout route with loader pattern (already implemented)
4. [x] Add method specifications to server functions

### **Phase 2: Component Improvements (2-4 hours)**

5. [x] Implement custom `useMutation` hook
6. [x] Create unified Auth component
7. [x] Simplify form handling for auth operations

### **Phase 3: Architecture Refinements (4-6 hours)**

8. [x] Evaluate server function co-location
9. [x] Implement hybrid error/redirect auth pattern
10. [x] Simplify router configuration (if possible)

## 📝 **Notes**

- **Keep our strengths**: Type safety, Zod validation, TanStack Query integration
- **Adopt their simplicity**: Where it doesn't compromise our architecture
- **Hybrid approach**: Combine best of both patterns
- **Gradual migration**: Implement incrementally without breaking existing functionality

## 🎯 **Success Criteria**

- [x] Improved developer experience with simpler patterns
- [x] Better user experience with optimized auth flows
- [x] Maintained type safety and validation
- [x] Cleaner, more maintainable code structure

---

**Next Session**: Implement Phase 1 quick wins to improve UX and DX
