# Product Requirements Document: Google OAuth Authentication Migration

## Executive Summary

This PRD outlines the migration from email-based authentication to Google OAuth authentication using Supabase Auth. The migration will leverage existing Google Cloud Platform credentials currently used for YouTube API integration and provide a seamless single sign-on experience for users.

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Technical Requirements](#technical-requirements)
3. [Implementation Plan](#implementation-plan)
4. [Database Schema Changes](#database-schema-changes)
5. [Configuration Updates](#configuration-updates)
6. [Migration Strategy](#migration-strategy)
7. [Testing Plan](#testing-plan)
8. [Rollback Plan](#rollback-plan)

## Current State Analysis

### Authentication Implementation

**Frontend (TanStack Start + React)**
- **Location**: `apps/web/app/`
- **Current Flow**: Email/password authentication via Supabase Auth
- **Key Components**:
  - `components/auth/sign-in-form.tsx` - Email/password sign-in form
  - `components/auth/sign-up-form.tsx` - Email/password registration form
  - `components/GoogleLoginButton.tsx` - **Already exists** with Google OAuth implementation
  - `lib/useAuth.ts` - Authentication hook with `signInWithGoogle()` method
  - `routes/auth/callback.tsx` - OAuth callback handler **already implemented**

**Backend (FastAPI + Python)**
- **Location**: `apps/core/`
- **Current Flow**: Custom JWT authentication with SQLAlchemy User model
- **Key Components**:
  - `lib/auth/supabase_auth.py` - Supabase JWT validation
  - `services/auth_service.py` - Legacy username/password authentication
  - `models/user_model.py` - SQLAlchemy User model (legacy)
  - `api/endpoints.py` - Login endpoints

**Database Schema**
- **Supabase Auth**: Uses `auth.users` table (UUID primary keys)
- **Legacy**: Custom `public.users` table (integer primary keys)
- **Current Tables**: `videos`, `video_jobs`, `video_metadata` reference `auth.users(id)`

### Existing Google Integration

**Google Cloud Platform Setup**
- **Project**: `automations-457120`
- **Service Account**: `vps-automations@automations-457120.iam.gserviceaccount.com`
- **Credentials File**: `apps/core/config/secrets/automations-457120-2c820f705e5e.json`
- **Current Usage**: YouTube API integration for video uploads

**Environment Configuration**
- **OAuth Credentials**: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (currently empty)
- **Supabase Config**: Google OAuth already enabled in `packages/supabase/config.toml`

### Current Issues

1. **Dual Authentication Systems**: Both Supabase Auth and legacy custom auth coexist
2. **Missing OAuth Credentials**: Google Client ID/Secret not configured
3. **Inconsistent User Management**: Frontend uses Supabase, backend uses legacy models
4. **Type Mismatches**: UUID vs Integer user IDs across systems

## Technical Requirements

### Functional Requirements

1. **Single Sign-On**: Users authenticate exclusively via Google OAuth
2. **Seamless Migration**: Existing users can link Google accounts to current profiles
3. **Session Management**: Unified session handling across frontend and backend
4. **User Profile Sync**: Google profile data populates user metadata
5. **YouTube Integration**: Leverage same Google credentials for YouTube API access

### Non-Functional Requirements

1. **Security**: OAuth 2.0 with PKCE flow for web applications
2. **Performance**: Sub-2 second authentication flow
3. **Reliability**: 99.9% authentication success rate
4. **Scalability**: Support for 10,000+ concurrent users
5. **Compliance**: GDPR-compliant user data handling

### Technical Constraints

1. **Existing Data**: Must preserve current user data and video associations
2. **API Compatibility**: Maintain backward compatibility for existing API endpoints
3. **Development Environment**: Support local development with localhost OAuth
4. **Production Environment**: Support production domain OAuth configuration

## Implementation Plan

### Phase 1: Google Cloud Platform Configuration

**Objective**: Configure Google OAuth credentials for both development and production

**Tasks**:
1. **Create OAuth 2.0 Client ID**
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Project: `automations-457120`
   - Create Web Application OAuth client
   - Configure authorized origins and redirect URIs

2. **Configure OAuth Scopes**
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `openid`
   - `https://www.googleapis.com/auth/youtube.upload` (for existing YouTube integration)

3. **Update Environment Variables**
   - Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to `.env` files
   - Configure production environment variables

**Deliverables**:
- Google OAuth client configured
- Environment variables populated
- Documentation for credential management

### Phase 2: Supabase Configuration Updates

**Objective**: Configure Supabase Auth for Google OAuth

**Tasks**:
1. **Update Supabase Config**
   - Verify `packages/supabase/config.toml` Google OAuth settings
   - Configure redirect URIs for development and production
   - Test local Supabase instance with Google OAuth

2. **Database Schema Validation**
   - Confirm `auth.users` table structure
   - Verify foreign key relationships in application tables
   - Test user creation flow via OAuth

**Deliverables**:
- Supabase configured for Google OAuth
- Local development environment tested
- Database schema validated

### Phase 3: Frontend Implementation

**Objective**: Update frontend to use Google OAuth exclusively

**Tasks**:
1. **Remove Email/Password Forms**
   - Deprecate `sign-in-form.tsx` and `sign-up-form.tsx`
   - Update routing to redirect to Google OAuth
   - Maintain `GoogleLoginButton.tsx` as primary authentication method

2. **Enhance OAuth Callback Handling**
   - Update `routes/auth/callback.tsx` for improved error handling
   - Add user profile synchronization after OAuth success
   - Implement proper loading states and user feedback

3. **Update Authentication Hook**
   - Simplify `lib/useAuth.ts` to focus on OAuth flow
   - Remove password-based authentication methods
   - Add Google profile data handling

**Deliverables**:
- Google OAuth as sole authentication method
- Enhanced user experience with proper feedback
- Simplified authentication codebase

### Phase 4: Backend Migration

**Objective**: Migrate backend to use Supabase Auth exclusively

**Tasks**:
1. **Remove Legacy Authentication**
   - Deprecate `services/auth_service.py`
   - Remove password-based login endpoints
   - Update all endpoints to use Supabase JWT validation

2. **Update User Management**
   - Migrate from SQLAlchemy User model to Supabase auth.users
   - Update user profile endpoints to use Supabase user metadata
   - Implement Google profile data synchronization

3. **Database Cleanup**
   - Remove legacy `public.users` table
   - Update foreign key references to use `auth.users`
   - Migrate existing user data to Supabase auth system

**Deliverables**:
- Backend exclusively using Supabase Auth
- Legacy authentication system removed
- Database schema simplified and consistent

## Database Schema Changes

### Current Schema Issues

```sql
-- Legacy table (to be removed)
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,  -- Integer ID
    username VARCHAR UNIQUE,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    -- ... other fields
);

-- Current application tables reference auth.users correctly
CREATE TABLE public.videos (
    id SERIAL PRIMARY KEY,
    uploader_user_id UUID REFERENCES auth.users(id), -- Correct reference
    -- ... other fields
);
```

### Required Changes

1. **Remove Legacy User Table**
   ```sql
   -- Migration to remove legacy users table
   DROP TABLE IF EXISTS public.users CASCADE;
   ```

2. **User Metadata in Supabase Auth**
   ```sql
   -- Supabase auth.users already supports user_metadata JSONB field
   -- Store additional profile data:
   {
     "username": "user_chosen_username",
     "full_name": "John Doe",
     "avatar_url": "https://lh3.googleusercontent.com/...",
     "google_id": "1234567890"
   }
   ```

3. **Data Migration Script**
   ```sql
   -- Script to migrate existing users to Supabase auth
   -- (Implementation details in migration strategy section)
   ```

## Configuration Updates

### Environment Variables

**Development (`.env.development`)**
```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_dev_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_dev_client_secret

# Supabase Configuration (existing)
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

**Production (`.env`)**
```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_prod_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_prod_client_secret

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_prod_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_prod_service_role_key
```

### Supabase Configuration

**`packages/supabase/config.toml`**
```toml
[auth.external.google]
enabled = true
client_id = "env(GOOGLE_CLIENT_ID)"
secret = "env(GOOGLE_CLIENT_SECRET)"
redirect_uri = "http://localhost:5173/auth/callback"  # Development
# redirect_uri = "https://echomycontent.com/auth/callback"  # Production
```

### Google Cloud Console Configuration

**Authorized JavaScript Origins**
- Development: `http://localhost:5173`
- Production: `https://echomycontent.com`

**Authorized Redirect URIs**
- Development: `http://localhost:5173/auth/callback`
- Production: `https://echomycontent.com/auth/callback`

## Migration Strategy

### User Data Migration

**Objective**: Migrate existing users from legacy system to Supabase Auth

**Approach**: Manual migration with user consent

1. **Pre-Migration Phase**
   - Identify users in legacy `public.users` table
   - Create mapping between email addresses and user data
   - Backup existing user data

2. **Migration Process**
   - User attempts to sign in with Google OAuth
   - System checks if email exists in legacy data
   - If match found, migrate user data to Supabase auth.users metadata
   - Link existing videos and jobs to new Supabase user ID
   - Mark legacy user record as migrated

3. **Post-Migration Cleanup**
   - After 30 days, remove legacy user table
   - Update all references to use Supabase auth exclusively

### Implementation Steps

```python
# Migration service implementation
async def migrate_legacy_user(google_email: str, supabase_user_id: str):
    """Migrate legacy user data to Supabase auth user metadata"""
    
    # 1. Find legacy user by email
    legacy_user = await get_legacy_user_by_email(google_email)
    if not legacy_user:
        return  # No migration needed
    
    # 2. Update Supabase user metadata
    user_metadata = {
        "username": legacy_user.username,
        "full_name": legacy_user.full_name,
        "migrated_from_legacy": True,
        "migration_date": datetime.utcnow().isoformat()
    }
    await supabase.auth.admin.update_user_by_id(
        supabase_user_id, 
        {"user_metadata": user_metadata}
    )
    
    # 3. Update video ownership
    await update_video_ownership(legacy_user.id, supabase_user_id)
    
    # 4. Mark legacy user as migrated
    await mark_legacy_user_migrated(legacy_user.id)
```

## Testing Plan

### Unit Tests

1. **Authentication Flow Tests**
   - Google OAuth initiation
   - Callback handling and token exchange
   - Session creation and validation
   - Error handling for failed authentication

2. **User Migration Tests**
   - Legacy user data migration
   - Metadata synchronization
   - Video ownership transfer
   - Edge cases (duplicate emails, missing data)

3. **API Integration Tests**
   - Supabase JWT validation
   - Protected endpoint access
   - User profile retrieval
   - YouTube API integration with OAuth tokens

### Integration Tests

1. **End-to-End Authentication**
   - Complete OAuth flow from login button to dashboard
   - Session persistence across browser sessions
   - Logout and re-authentication

2. **Cross-Platform Testing**
   - Desktop browsers (Chrome, Firefox, Safari, Edge)
   - Mobile browsers (iOS Safari, Android Chrome)
   - Different screen sizes and orientations

3. **Environment Testing**
   - Local development environment
   - Staging environment with production-like configuration
   - Production environment validation

### Performance Tests

1. **Authentication Speed**
   - OAuth flow completion time
   - Token validation performance
   - Session initialization speed

2. **Concurrent User Testing**
   - Multiple simultaneous OAuth flows
   - Session management under load
   - Database performance with UUID lookups

## Rollback Plan

### Immediate Rollback (< 24 hours)

**Scenario**: Critical issues discovered immediately after deployment

**Steps**:
1. **Revert Frontend Changes**
   - Deploy previous version with email/password authentication
   - Disable Google OAuth button
   - Restore legacy authentication forms

2. **Revert Backend Changes**
   - Re-enable legacy authentication endpoints
   - Restore SQLAlchemy User model usage
   - Revert to integer user ID system

3. **Database Rollback**
   - Restore legacy `public.users` table from backup
   - Revert foreign key references
   - Restore user sessions

### Extended Rollback (> 24 hours)

**Scenario**: Issues discovered after user migration has begun

**Steps**:
1. **Data Preservation**
   - Export all Supabase auth users created during migration
   - Preserve Google OAuth user metadata
   - Maintain video/job associations

2. **Hybrid System**
   - Support both authentication methods temporarily
   - Allow users to choose authentication method
   - Gradual migration back to legacy system if needed

3. **Communication Plan**
   - Notify users of authentication changes
   - Provide clear instructions for account access
   - Offer support for account recovery

### Prevention Measures

1. **Feature Flags**
   - Implement feature toggles for OAuth authentication
   - Allow gradual rollout to user segments
   - Quick disable capability for emergency situations

2. **Monitoring and Alerts**
   - Authentication success/failure rate monitoring
   - User session creation tracking
   - Error rate alerting for OAuth flows

3. **Backup Strategy**
   - Daily database backups before migration
   - Configuration file versioning
   - Deployment artifact preservation

## Success Criteria

### Technical Metrics

1. **Authentication Success Rate**: > 99%
2. **OAuth Flow Completion Time**: < 3 seconds
3. **User Migration Success Rate**: > 95%
4. **Zero Data Loss**: All existing user data preserved
5. **API Response Time**: < 500ms for authenticated requests

### User Experience Metrics

1. **User Satisfaction**: > 4.5/5 in post-migration survey
2. **Support Ticket Reduction**: < 5% increase in authentication-related tickets
3. **User Retention**: No decrease in daily active users
4. **Onboarding Improvement**: 50% faster new user registration

### Business Metrics

1. **Development Velocity**: 25% reduction in authentication-related development time
2. **Security Posture**: Elimination of password-related security risks
3. **Maintenance Overhead**: 40% reduction in authentication system maintenance
4. **YouTube Integration**: Seamless single sign-on for video upload features

## Timeline

**Total Duration**: 4-6 weeks

- **Week 1**: Google Cloud Platform configuration and Supabase setup
- **Week 2**: Frontend implementation and testing
- **Week 3**: Backend migration and database changes
- **Week 4**: Integration testing and user migration implementation
- **Week 5**: Staging deployment and user acceptance testing
- **Week 6**: Production deployment and monitoring

## Risk Assessment

### High Risk

1. **User Data Loss**: Mitigation through comprehensive backup and testing
2. **Authentication Outage**: Mitigation through rollback plan and monitoring
3. **Google API Rate Limits**: Mitigation through proper quota management

### Medium Risk

1. **User Confusion**: Mitigation through clear communication and documentation
2. **Integration Issues**: Mitigation through thorough testing and staging environment
3. **Performance Degradation**: Mitigation through load testing and optimization

### Low Risk

1. **Browser Compatibility**: Mitigation through cross-browser testing
2. **Mobile Experience**: Mitigation through responsive design testing
3. **Third-party Dependencies**: Mitigation through vendor SLA monitoring

## Conclusion

This migration to Google OAuth authentication will significantly improve user experience, enhance security, and simplify the authentication architecture. The phased approach ensures minimal disruption to existing users while providing a clear path forward for the application's authentication system.

The existing foundation with Supabase Auth and partial Google OAuth implementation provides a strong starting point for this migration. With proper planning, testing, and execution, this migration will deliver substantial benefits to both users and the development team.
