import { middleware } from '../trpc'
import { RateLimitError } from '../lib/errors'
import { createHash } from 'crypto'

interface RateLimitConfig {
  windowMs: number // Time window in milliseconds
  max: number // Max requests per window
  keyGenerator?: (ctx: any) => string // Custom key generator
}

// In-memory store for rate limiting (use Redis in production)
const rateLimitStore = new Map<string, { count: number; resetAt: number }>()

/**
 * Clean up expired entries periodically
 */
setInterval(() => {
  const now = Date.now()
  for (const [key, value] of rateLimitStore.entries()) {
    if (value.resetAt <= now) {
      rateLimitStore.delete(key)
    }
  }
}, 60000) // Clean up every minute

/**
 * Rate limiting middleware factory
 */
export function createRateLimiter(config: RateLimitConfig) {
  return middleware(async ({ ctx, next, path }) => {
    const {
      windowMs = 15 * 60 * 1000, // 15 minutes default
      max = 100, // 100 requests per window default
      keyGenerator,
    } = config

    // Generate rate limit key
    const key = keyGenerator
      ? keyGenerator(ctx)
      : ctx.user
        ? `user:${ctx.user.id}:${path}`
        : `ip:${ctx.req?.header('x-forwarded-for') || 'unknown'}:${path}`

    const now = Date.now()
    const record = rateLimitStore.get(key)

    if (!record || record.resetAt <= now) {
      // Create new record
      rateLimitStore.set(key, {
        count: 1,
        resetAt: now + windowMs,
      })
    } else {
      // Increment counter
      record.count++

      if (record.count > max) {
        const retryAfter = Math.ceil((record.resetAt - now) / 1000)

        throw new RateLimitError(`Rate limit exceeded. Try again in ${retryAfter} seconds`)
      }
    }

    return next()
  })
}

/**
 * Pre-configured rate limiters
 */
export const rateLimiters = {
  // Strict rate limit for authentication endpoints
  auth: createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 attempts per window
  }),

  // Standard rate limit for API endpoints
  api: createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // 100 requests per window
  }),

  // Relaxed rate limit for read operations
  read: createRateLimiter({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 60, // 60 requests per minute
  }),

  // Strict rate limit for write operations
  write: createRateLimiter({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 20, // 20 requests per minute
  }),

  // Very strict rate limit for expensive operations
  expensive: createRateLimiter({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 10, // 10 requests per hour
  }),

  // Custom rate limit based on operation cost
  cost: (cost: number) =>
    createRateLimiter({
      windowMs: 60 * 60 * 1000, // 1 hour
      max: Math.floor(1000 / cost), // Adjust max based on cost
    }),
}

/**
 * Hash IP address for privacy
 */
export function hashIp(ip: string): string {
  return createHash('sha256').update(ip).digest('hex').substring(0, 16)
}
