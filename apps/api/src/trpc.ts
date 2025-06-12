import { initTRPC, TRPCError } from '@trpc/server'
import type { Context } from './context'
import { ZodError } from 'zod'

/**
 * Initialization of tRPC backend
 * Should be done only once per backend!
 */
const t = initTRPC.context<Context>().create({
  /**
   * Custom error formatting
   */
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError
            ? error.cause.flatten()
            : null,
      },
    }
  },
})

/**
 * Export reusable router and procedure helpers
 * that can be used throughout the router
 */
export const router = t.router
export const middleware = t.middleware

/**
 * Public (unauthenticated) procedure
 */
export const publicProcedure = t.procedure

/**
 * Reusable middleware that enforces users are logged in before running the procedure
 */
const enforceUserIsAuthed = middleware(async ({ ctx, next }) => {
  if (!ctx.user) {
    throw new TRPCError({ 
      code: 'UNAUTHORIZED',
      message: 'Not authenticated',
    })
  }
  
  return next({
    ctx: {
      // infers the `user` as non-nullable
      user: ctx.user,
    },
  })
})

/**
 * Protected (authenticated) procedure
 */
export const protectedProcedure = t.procedure.use(enforceUserIsAuthed)

/**
 * Admin procedure - requires admin role
 */
const enforceUserIsAdmin = enforceUserIsAuthed.unstable_pipe(
  async ({ ctx, next }) => {
    // You can add admin check logic here
    // For now, we'll just pass through
    // if (ctx.user.role !== 'admin') {
    //   throw new TRPCError({ code: 'FORBIDDEN' })
    // }
    
    return next({ ctx })
  }
)

export const adminProcedure = t.procedure.use(enforceUserIsAdmin)