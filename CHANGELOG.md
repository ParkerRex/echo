# Changelog

All notable changes to the Echo project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🏗️ Complete Backend Migration to Hono + tRPC - 2025-12-06

**BREAKING CHANGES:**

- Complete migration from Python FastAPI to TypeScript Hono + tRPC
- All API endpoints now use tRPC procedures instead of REST endpoints
- Database access migrated from SQLAlchemy to Drizzle ORM

**Added:**

- **Modern TypeScript Backend**: Complete rewrite using Hono web framework
- **End-to-End Type Safety**: tRPC integration for type-safe API calls
- **Drizzle ORM**: Modern TypeScript ORM with SQL-like syntax
- **Enhanced Middleware**: Request logging, error handling, authentication, and rate limiting
- **Docker Support**: Updated Dockerfile for TypeScript/Bun runtime
- **Comprehensive Testing**: Updated test suite for tRPC procedures

**Technical Improvements:**

- **Performance**: Significantly faster with Bun runtime and optimized TypeScript
- **Developer Experience**: Full type inference from database to frontend
- **Maintainability**: Single language (TypeScript) across the entire stack
- **Modern Tooling**: Drizzle Studio for database exploration
- **Better Error Handling**: Comprehensive error middleware and validation

**Migration Details:**

- Python services → TypeScript services with identical functionality
- SQLAlchemy models → Drizzle schema definitions
- FastAPI dependencies → tRPC context and middleware
- Pydantic validation → Zod schemas with runtime validation
- REST endpoints → Type-safe tRPC procedures

### 🔒 Authentication System Hardening - 2024-12-19

**BREAKING CHANGES:**

- Migrated from client-side to server-side authentication
- Deprecated `useAuth()` hook in favor of server functions
- Updated all authentication flows to use TanStack Start server functions

**Added:**

- **Hardened Server-Side Authentication**: Complete rewrite using TanStack Start server functions
- **Unified Supabase Client**: Auto-detecting client factory with environment validation
- **Comprehensive Route Protection**: Server-side middleware with automatic redirects
- **Enhanced Security**: PKCE OAuth, secure cookies, comprehensive error handling
- **Authentication Documentation**: Complete developer guide (`docs/AUTHENTICATION.md`)

**Security Improvements:**

- HttpOnly cookies with secure flags in production
- SameSite=Lax for CSRF protection
- PKCE (Proof Key for Code Exchange) for OAuth flows
- Comprehensive error logging and timeout protection
- Environment variable validation and proper configuration

**Fixed:**

- **Race Conditions**: Eliminated client-server authentication race conditions
- **Session Synchronization**: Consistent auth state between client and server
- **Cookie Management**: Proper cookie handling for TanStack Start
- **OAuth Redirects**: Robust callback handling with fallback mechanisms

### Planned

- Manual testing implementation
- Additional UI/UX improvements
- Performance optimizations

## [0.3.1] - 2025-01-28 - OAuth Authentication Fix

### Fixed

- **Google OAuth PKCE Flow**: Fixed "invalid flow state, no valid flow state found" error in local development
- **OAuth Redirect Configuration**: Updated Supabase config to use `http://127.0.0.1:54321/auth/v1/callback` for proper PKCE handling
- **Authentication Callback**: Simplified OAuth callback component to work with server-side OAuth processing

### Added

- **OAuth Documentation**: Comprehensive setup guide for Google OAuth configuration
- **Troubleshooting Guide**: Common OAuth issues and solutions in README
- **Configuration Examples**: Clear examples of required redirect URIs for local development

### Changed

- **Supabase OAuth Config**: Updated `redirect_uri` to point to local Supabase API endpoint
- **OAuth Callback Route**: Simplified to rely on Supabase's built-in OAuth handling

### Technical Details

- Root cause: PKCE flow state must be maintained by the same Supabase instance that created it
- Solution: Configure Google OAuth to redirect directly to Supabase API (`http://127.0.0.1:54321/auth/v1/callback`)
- This allows Supabase to handle the OAuth code exchange while maintaining PKCE flow state integrity

## [0.3.0] - 2025-01-15 - TanStack Patterns Implementation

### Added

- **Unified Auth Components**: Implemented single Auth component for both sign-in and sign-up flows
- **Custom Mutation Hook**: Added `useMutation` hook for consistent form submission handling
- **FormData-based Form Handling**: Simplified form submission without complex state management
- **Enhanced Error Handling**: Hybrid approach with redirects for auth failures and error components for other errors
- **Consistent Server Function Error Handling**: All auth server functions now return error objects instead of throwing

### Changed

- **SignInForm and SignUpForm**: Converted to use unified Auth component with FormData handling
- **Server Function Validators**: Evaluated and kept superior Zod schemas for better validation and type safety
- **Auth Error Patterns**: Enhanced `_authed` route with proper error component while maintaining redirect-based auth
- **Router Configuration**: Evaluated and confirmed optimal configuration for our application needs

### Improved

- **Developer Experience**: Simplified patterns while maintaining robust architecture
- **User Experience**: Better inline error handling and consistent auth flows
- **Type Safety**: Maintained end-to-end type safety with database-driven type generation
- **Code Consistency**: Unified patterns across all auth-related components and server functions

### Technical Details

- Adopted patterns from official TanStack Start + Supabase example where beneficial
- Maintained complex Zod validation schemas for production-ready security
- Implemented hybrid server function organization (co-located simple functions, separated complex ones)
- Enhanced error boundaries for better error handling throughout the application

### Files Modified

- `apps/web/app/components/auth/sign-in-form.tsx` - Converted to use unified Auth component
- `apps/web/app/components/auth/sign-up-form.tsx` - Converted to use unified Auth component
- `apps/web/app/services/auth.api.ts` - Updated server functions to return error objects consistently
- `apps/web/app/routes/_authed.tsx` - Added error component for non-auth errors
- `README.md` - Added comprehensive website section
- `CHANGELOG.md` - Created project changelog

## [0.2.0] - 2025-01-XX - Environment Configuration & Type System

### Added

- **Environment Configuration System**: Standardized `.env` and `.env.development` pattern
- **Database-First Type Generation**: Automated TypeScript and Python type generation from Supabase schema
- **End-to-End Type Safety**: Complete type safety from database to frontend and backend
- **Comprehensive Documentation**: Detailed guides for type safety workflow and development patterns

### Changed

- **Environment Files**: Simplified to `.env` (production) and `.env.development` (local) pattern
- **Type System**: Database schema as single source of truth for all types
- **Development Workflow**: Database-first approach for adding new features

### Improved

- **Developer Experience**: Fantastic DX with automatic type generation and validation
- **Type Safety**: Catch errors at compile time across the entire stack
- **Documentation**: Clear guides for the type system and development workflow

## [0.1.0] - 2025-01-XX - Initial Release

### Added

- **Core Application**: AI-powered YouTube video metadata generation
- **Backend**: FastAPI with Python 3.10+ and uv package management
- **Frontend**: React with TanStack Router for type-safe routing
- **Database**: PostgreSQL via Supabase with Row Level Security
- **Authentication**: Supabase Auth with user data isolation
- **AI Integration**: Google Gemini for video transcription and content analysis
- **Storage**: Google Cloud Storage for video files
- **Development Environment**: Complete local development setup with Docker

### Features

- **Video Upload & Processing**: Upload videos and get AI-generated metadata
- **AI-Powered Analysis**: Automatic generation of titles, descriptions, transcripts, and chapters
- **Secure Authentication**: User accounts with data isolation
- **Modern UI**: Responsive React frontend with Tailwind CSS
- **Type Safety**: End-to-end TypeScript integration

### Technical Foundation

- **Monorepo Structure**: Organized with apps/ and packages/ structure
- **Database Migrations**: Supabase migration system with strict development rules
- **Row Level Security**: Comprehensive RLS policies for data protection
- **Package Management**: uv for Python, pnpm for Node.js
- **Quality Tooling**: ESLint, Prettier, mypy, and comprehensive type checking

---

## Release Notes

### Version Numbering

- **Major (X.0.0)**: Breaking changes or major feature releases
- **Minor (0.X.0)**: New features, improvements, and significant updates
- **Patch (0.0.X)**: Bug fixes, small improvements, and maintenance updates

### Development Workflow

All changes follow our database-first development workflow:

1. Design database schema changes
2. Create and apply migrations
3. Generate types across the stack
4. Implement features using generated types
5. Test end-to-end functionality

### Contributing

See [Contributing Guidelines](README.md#contributing) for information on how to contribute to this project.
