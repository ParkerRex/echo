/**
 * Retry mechanism with exponential backoff and jitter
 * 
 * Automatically retries failed operations with configurable
 * retry strategies and backoff algorithms.
 */

export interface RetryOptions {
  maxAttempts: number
  baseDelay: number          // Base delay in milliseconds
  maxDelay: number           // Maximum delay in milliseconds
  backoffFactor: number      // Multiplier for exponential backoff
  jitter: boolean           // Add randomness to prevent thundering herd
  retryCondition?: (error: any) => boolean  // Custom condition for when to retry
  onRetry?: (attempt: number, error: any) => void  // Callback on retry
}

export interface RetryStats {
  attempts: number
  totalDelay: number
  success: boolean
  finalError?: any
}

export class RetryError extends Error {
  constructor(
    message: string,
    public readonly attempts: number,
    public readonly finalError: any
  ) {
    super(message)
    this.name = 'RetryError'
  }
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: Partial<RetryOptions> = {}
): Promise<T> {
  const opts: RetryOptions = {
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 30000,
    backoffFactor: 2,
    jitter: true,
    retryCondition: (error) => {
      // Default: retry on network errors, timeouts, and 5xx errors
      if (error?.code === 'ECONNRESET' || error?.code === 'ETIMEDOUT') return true
      if (error?.response?.status >= 500) return true
      if (error?.name === 'TimeoutError') return true
      if (error?.message?.includes('timeout')) return true
      if (error?.message?.includes('connection')) return true
      return false
    },
    ...options
  }

  let lastError: any
  let totalDelay = 0

  for (let attempt = 1; attempt <= opts.maxAttempts; attempt++) {
    try {
      const result = await fn()
      return result
    } catch (error) {
      lastError = error

      // Don't retry if we've reached max attempts
      if (attempt === opts.maxAttempts) {
        break
      }

      // Check if we should retry this error
      if (opts.retryCondition && !opts.retryCondition(error)) {
        break
      }

      // Calculate delay with exponential backoff
      let delay = Math.min(
        opts.baseDelay * Math.pow(opts.backoffFactor, attempt - 1),
        opts.maxDelay
      )

      // Add jitter to prevent thundering herd
      if (opts.jitter) {
        delay = delay * (0.5 + Math.random() * 0.5)
      }

      totalDelay += delay

      // Call retry callback if provided
      if (opts.onRetry) {
        opts.onRetry(attempt, error)
      }

      console.warn(`[RETRY] Attempt ${attempt} failed, retrying in ${Math.round(delay)}ms:`, {
        error: error instanceof Error ? error.message : String(error),
        nextDelay: Math.round(delay)
      })

      // Wait before retrying
      await sleep(delay)
    }
  }

  throw new RetryError(
    `Operation failed after ${opts.maxAttempts} attempts`,
    opts.maxAttempts,
    lastError
  )
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// Pre-configured retry strategies
export const retryStrategies = {
  // For external API calls
  externalAPI: {
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffFactor: 2,
    jitter: true,
    retryCondition: (error: any) => {
      // Retry on network errors and 5xx errors
      if (error?.code === 'ECONNRESET' || error?.code === 'ETIMEDOUT') return true
      if (error?.code === 'ENOTFOUND' || error?.code === 'ECONNREFUSED') return true
      if (error?.response?.status >= 500) return true
      if (error?.response?.status === 429) return true // Rate limit
      return false
    }
  },

  // For database operations
  database: {
    maxAttempts: 5,
    baseDelay: 100,
    maxDelay: 5000,
    backoffFactor: 1.5,
    jitter: true,
    retryCondition: (error: any) => {
      // Retry on connection errors and timeouts
      if (error?.code === 'ECONNRESET') return true
      if (error?.code === 'ETIMEDOUT') return true
      if (error?.message?.includes('connection')) return true
      if (error?.message?.includes('timeout')) return true
      return false
    }
  },

  // For file operations
  fileSystem: {
    maxAttempts: 3,
    baseDelay: 500,
    maxDelay: 2000,
    backoffFactor: 1.5,
    jitter: false,
    retryCondition: (error: any) => {
      // Retry on temporary file system errors
      if (error?.code === 'EBUSY') return true
      if (error?.code === 'EMFILE') return true
      if (error?.code === 'ENFILE') return true
      return false
    }
  },

  // For critical operations that should not fail
  critical: {
    maxAttempts: 5,
    baseDelay: 2000,
    maxDelay: 30000,
    backoffFactor: 2,
    jitter: true,
    retryCondition: () => true // Retry all errors
  },

  // Quick retries for fast operations
  quick: {
    maxAttempts: 2,
    baseDelay: 200,
    maxDelay: 1000,
    backoffFactor: 2,
    jitter: true
  }
}

// Utility functions for common retry patterns
export function retryExternalAPI<T>(fn: () => Promise<T>): Promise<T> {
  return withRetry(fn, retryStrategies.externalAPI)
}

export function retryDatabase<T>(fn: () => Promise<T>): Promise<T> {
  return withRetry(fn, retryStrategies.database)
}

export function retryFileSystem<T>(fn: () => Promise<T>): Promise<T> {
  return withRetry(fn, retryStrategies.fileSystem)
}

export function retryCritical<T>(fn: () => Promise<T>): Promise<T> {
  return withRetry(fn, retryStrategies.critical)
}

export function retryQuick<T>(fn: () => Promise<T>): Promise<T> {
  return withRetry(fn, retryStrategies.quick)
}