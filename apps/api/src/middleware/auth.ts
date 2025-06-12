import { middleware } from '../trpc'
import { AuthenticationError, AuthorizationError } from '../lib/errors'
import { validateJWT } from '../lib/auth/supabase'
import type { User } from '../context'

interface AuthOptions {
  requireVerified?: boolean
  allowedRoles?: string[]
  sessionMaxAge?: number // in seconds
}

/**
 * Enhanced authentication middleware
 */
export function createAuthMiddleware(options: AuthOptions = {}) {
  return middleware(async ({ ctx, next }) => {
    const {
      requireVerified = false,
      allowedRoles = [],
      sessionMaxAge = 24 * 60 * 60, // 24 hours default
    } = options

    // Check if user is authenticated
    if (!ctx.user) {
      throw new AuthenticationError('Authentication required')
    }

    // Check session age if configured
    if (sessionMaxAge && ctx.user.sessionCreatedAt) {
      const sessionAge = Date.now() - ctx.user.sessionCreatedAt.getTime()
      if (sessionAge > sessionMaxAge * 1000) {
        throw new AuthenticationError('Session expired')
      }
    }

    // Check if email is verified (if required)
    if (requireVerified && !ctx.user.emailVerified) {
      throw new AuthorizationError('Email verification required')
    }

    // Check role-based access (if configured)
    if (allowedRoles.length > 0 && ctx.user.role) {
      if (!allowedRoles.includes(ctx.user.role)) {
        throw new AuthorizationError(`Required role: ${allowedRoles.join(' or ')}`)
      }
    }

    return next({
      ctx: {
        ...ctx,
        user: ctx.user as User, // Type assertion since we know user exists
      },
    })
  })
}

/**
 * Pre-configured authentication middlewares
 */
export const auth = {
  // Basic authentication - just checks if user is logged in
  required: createAuthMiddleware(),

  // Requires verified email
  verified: createAuthMiddleware({
    requireVerified: true,
  }),

  // Admin only
  admin: createAuthMiddleware({
    allowedRoles: ['admin'],
  }),

  // Moderator or admin
  moderator: createAuthMiddleware({
    allowedRoles: ['moderator', 'admin'],
  }),

  // Fresh session required (e.g., for sensitive operations)
  fresh: createAuthMiddleware({
    sessionMaxAge: 15 * 60, // 15 minutes
  }),

  // Custom role check
  role: (roles: string[]) => createAuthMiddleware({
    allowedRoles: roles,
  }),
}

/**
 * Optional authentication middleware - doesn't throw if user is not authenticated
 */
export const optionalAuth = middleware(async ({ ctx, next }) => {
  // Just pass through - user might or might not be authenticated
  return next()
})

/**
 * API key authentication middleware for service-to-service communication
 */
export function createApiKeyMiddleware(validKeys: Set<string>) {
  return middleware(async ({ ctx, next }) => {
    const apiKey = ctx.req?.headers.get('x-api-key')

    if (!apiKey || !validKeys.has(apiKey)) {
      throw new AuthenticationError('Invalid API key')
    }

    // You could also look up the service associated with this API key
    // and add it to the context
    return next({
      ctx: {
        ...ctx,
        apiKey,
        isServiceRequest: true,
      },
    })
  })
}