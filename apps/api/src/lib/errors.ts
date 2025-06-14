import { TRPCError } from '@trpc/server'

export class ApiError extends TRPCError {
  constructor(code: TRPCError['code'], message: string, cause?: unknown) {
    super({ code, message, cause })
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, cause?: unknown) {
    super('BAD_REQUEST', message, cause)
  }
}

export class AuthenticationError extends ApiError {
  constructor(message = 'Authentication required', cause?: unknown) {
    super('UNAUTHORIZED', message, cause)
  }
}

export class AuthorizationError extends ApiError {
  constructor(message = 'Insufficient permissions', cause?: unknown) {
    super('FORBIDDEN', message, cause)
  }
}

export class NotFoundError extends ApiError {
  constructor(resource: string, id?: string, cause?: unknown) {
    const message = id ? `${resource} with id ${id} not found` : `${resource} not found`
    super('NOT_FOUND', message, cause)
  }
}

export class ConflictError extends ApiError {
  constructor(message: string, cause?: unknown) {
    super('CONFLICT', message, cause)
  }
}

export class RateLimitError extends ApiError {
  constructor(message = 'Rate limit exceeded', cause?: unknown) {
    super('TOO_MANY_REQUESTS', message, cause)
  }
}

export class PayloadTooLargeError extends ApiError {
  constructor(message = 'Payload too large', cause?: unknown) {
    super('PAYLOAD_TOO_LARGE', message, cause)
  }
}

export class ExternalServiceError extends ApiError {
  constructor(service: string, message?: string, cause?: unknown) {
    super('INTERNAL_SERVER_ERROR', message || `External service error: ${service}`, cause)
  }
}

/**
 * Type guard to check if an error is a TRPCError
 */
export function isTRPCError(error: unknown): error is TRPCError {
  return error instanceof TRPCError
}

/**
 * Type guard to check if an error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

/**
 * Safe error message extraction
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'An unknown error occurred'
}

/**
 * Handle async errors in a type-safe way
 */
export async function handleAsync<T>(promise: Promise<T>): Promise<[T, null] | [null, Error]> {
  try {
    const data = await promise
    return [data, null]
  } catch (error) {
    if (error instanceof Error) {
      return [null, error]
    }
    return [null, new Error(getErrorMessage(error))]
  }
}
