# Authentication System Documentation

## Overview

Echo uses a hardened server-side authentication system built on TanStack Start and Supabase. This system eliminates client-server race conditions and provides a single source of truth for authentication state.

## Architecture

### Core Components

1. **Server-Side Authentication** (`src/services/auth.api.ts`)

   - Single source of truth for auth state
   - Server functions for all auth operations
   - Comprehensive error handling and logging

2. **Supabase Client Configuration** (`packages/supabase/clients/index.ts`)

   - Unified client factory with auto-detection
   - Proper cookie handling for TanStack Start
   - Environment variable validation

3. **Route Protection** (`src/routes/_authed.tsx`)
   - Server-side middleware for protected routes
   - Automatic redirects with return URLs
   - Consistent error handling

## Authentication Flow

### Google OAuth Sign In

1. User clicks "Sign in with Google" button
2. `signInWithGoogle()` server function initiates OAuth flow
3. User is redirected to Google OAuth consent screen
4. Google redirects back to `/auth/callback`
5. Callback page processes OAuth response
6. Server verifies authentication state
7. User is redirected to intended destination

### Route Protection

Protected routes use the `_authed` layout which:

1. Runs `userRequiredPageMiddleware` in `beforeLoad`
2. Checks authentication on the server
3. Redirects to login if not authenticated
4. Passes user context to child routes

### Session Management

- Sessions are managed entirely by Supabase
- Cookies are handled server-side with proper security settings
- Automatic session refresh when needed
- Consistent session state between client and server

## API Reference

### Server Functions

#### `getUser()`

Returns current authentication state.

```typescript
const authState = await getUser();
if (authState.isAuthenticated) {
  console.log("User:", authState.user);
}
```

#### `signInWithGoogle()`

Initiates Google OAuth sign in.

```typescript
const result = await signInWithGoogle();
if (result.success) {
  window.location.href = result.url;
}
```

#### `signOut()`

Signs out the current user.

```typescript
await signOut();
// User will be redirected to home page
```

#### `updateUser(data)`

Updates user profile metadata.

```typescript
await updateUser({
  username: "newusername",
  full_name: "New Name",
});
```

### Middleware

#### `userMiddleware`

Core middleware that extracts user from session.

#### `userRequiredMiddleware`

For API endpoints that require authentication.

#### `userRequiredPageMiddleware`

For page routes that require authentication.

## Environment Variables

### Required Variables

```bash
# Server-side (process.env)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Client-side (VITE_ prefixed)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_BASE_URL=http://localhost:3000
```

### OAuth Configuration

```bash
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## Security Features

### Cookie Security

- HttpOnly cookies for session storage
- Secure flag in production
- SameSite=Lax for CSRF protection
- 7-day expiration

### PKCE Flow

- Uses PKCE (Proof Key for Code Exchange) for OAuth
- Prevents authorization code interception attacks

### Error Handling

- Comprehensive error logging
- User-friendly error messages
- Automatic fallback behaviors
- Timeout protection

## Migration from Client-Side Auth

The old `useAuth()` hook is deprecated. Replace usage as follows:

### Before (Client-Side)

```typescript
const { user, signOut } = useAuth();
```

### After (Server-Side)

```typescript
const getUserFn = useServerFn(getUser);
const signOutFn = useServerFn(signOut);

const authState = await getUserFn();
if (authState.isAuthenticated) {
  // Use authState.user
}

await signOutFn();
```

## Troubleshooting

### Common Issues

1. **Environment Variables Not Loading**

   - Ensure TanStack Start config includes `envDir: '../..'`
   - Check that both server and client variables are set

2. **OAuth Redirect Issues**

   - Verify `VITE_BASE_URL` matches your domain
   - Check Supabase OAuth settings

3. **Session Not Persisting**
   - Ensure cookies are properly configured
   - Check browser cookie settings

### Debug Mode

Enable debug logging by setting:

```bash
DEBUG=true
```

This will log all authentication operations and state changes.

## Best Practices

1. **Always use server functions** for auth operations
2. **Use middleware** for route protection
3. **Handle errors gracefully** with user-friendly messages
4. **Test auth flows** in both development and production
5. **Monitor auth logs** for security issues

## Future Enhancements

- Multi-factor authentication (MFA)
- Additional OAuth providers (GitHub, Discord)
- Role-based access control (RBAC)
- Session analytics and monitoring
