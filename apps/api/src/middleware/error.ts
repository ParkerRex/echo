import { Context, Next } from 'hono'
import { HTTPException } from 'hono/http-exception'
import { ZodError } from 'zod'
import { TRPCError } from '@trpc/server'

export interface ErrorResponse {
  error: string
  message: string
  details?: any
  requestId?: string
}

export async function errorMiddleware(c: Context, next: Next) {
  try {
    await next()
  } catch (error) {
    console.error('Error in request:', error)
    
    const requestId = c.req.header('X-Request-ID') || crypto.randomUUID()
    
    // Handle different error types
    if (error instanceof HTTPException) {
      return c.json<ErrorResponse>(
        {
          error: 'HTTP_EXCEPTION',
          message: error.message,
          requestId,
        },
        error.status
      )
    }
    
    if (error instanceof ZodError) {
      return c.json<ErrorResponse>(
        {
          error: 'VALIDATION_ERROR',
          message: 'Invalid input',
          details: error.errors,
          requestId,
        },
        400
      )
    }
    
    if (error instanceof TRPCError) {
      const statusMap: Record<string, number> = {
        UNAUTHORIZED: 401,
        FORBIDDEN: 403,
        NOT_FOUND: 404,
        BAD_REQUEST: 400,
        INTERNAL_SERVER_ERROR: 500,
        PRECONDITION_FAILED: 412,
        CONFLICT: 409,
        UNPROCESSABLE_CONTENT: 422,
        TOO_MANY_REQUESTS: 429,
      }
      
      return c.json<ErrorResponse>(
        {
          error: error.code,
          message: error.message,
          requestId,
        },
        statusMap[error.code] || 500
      )
    }
    
    // Generic error
    const message = error instanceof Error ? error.message : 'An unexpected error occurred'
    
    return c.json<ErrorResponse>(
      {
        error: 'INTERNAL_SERVER_ERROR',
        message: process.env.NODE_ENV === 'development' ? message : 'Something went wrong',
        requestId,
      },
      500
    )
  }
}