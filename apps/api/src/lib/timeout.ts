/**
 * Timeout utilities for preventing hanging operations
 * 
 * Provides consistent timeout handling across the application
 * with configurable timeouts for different operation types.
 */

export class TimeoutError extends Error {
  constructor(message: string, public readonly timeoutMs: number) {
    super(message)
    this.name = 'TimeoutError'
  }
}

export interface TimeoutOptions {
  timeoutMs: number
  timeoutMessage?: string
  abortSignal?: AbortSignal
}

/**
 * Wraps a promise with a timeout
 */
export function withTimeout<T>(
  promise: Promise<T>,
  options: TimeoutOptions
): Promise<T> {
  const { timeoutMs, timeoutMessage, abortSignal } = options

  return new Promise<T>((resolve, reject) => {
    let timeoutId: NodeJS.Timeout | null = null
    let completed = false

    // Handle existing abort signal
    if (abortSignal?.aborted) {
      reject(new Error('Operation was aborted'))
      return
    }

    // Set up timeout
    timeoutId = setTimeout(() => {
      if (!completed) {
        completed = true
        reject(new TimeoutError(
          timeoutMessage || `Operation timed out after ${timeoutMs}ms`,
          timeoutMs
        ))
      }
    }, timeoutMs)

    // Handle abort signal
    const onAbort = () => {
      if (!completed) {
        completed = true
        if (timeoutId) clearTimeout(timeoutId)
        reject(new Error('Operation was aborted'))
      }
    }

    abortSignal?.addEventListener('abort', onAbort)

    // Handle promise resolution/rejection
    promise
      .then((result) => {
        if (!completed) {
          completed = true
          if (timeoutId) clearTimeout(timeoutId)
          abortSignal?.removeEventListener('abort', onAbort)
          resolve(result)
        }
      })
      .catch((error) => {
        if (!completed) {
          completed = true
          if (timeoutId) clearTimeout(timeoutId)
          abortSignal?.removeEventListener('abort', onAbort)
          reject(error)
        }
      })
  })
}

/**
 * Creates a fetch with timeout
 */
export function fetchWithTimeout(
  url: string | URL | Request,
  options: RequestInit & { timeoutMs?: number } = {}
): Promise<Response> {
  const { timeoutMs = 30000, ...fetchOptions } = options

  const controller = new AbortController()
  const fetchPromise = fetch(url, {
    ...fetchOptions,
    signal: controller.signal
  })

  return withTimeout(fetchPromise, {
    timeoutMs,
    timeoutMessage: `Fetch request to ${url} timed out after ${timeoutMs}ms`,
    abortSignal: controller.signal
  })
}

// Predefined timeout configurations
export const timeouts = {
  // Database operations
  database: {
    query: 10000,      // 10 seconds for regular queries
    migration: 300000,  // 5 minutes for migrations
    backup: 1800000,   // 30 minutes for backups
  },

  // External API calls
  api: {
    fast: 5000,        // 5 seconds for fast APIs
    standard: 15000,   // 15 seconds for standard APIs
    slow: 60000,       // 1 minute for slow APIs
    upload: 300000,    // 5 minutes for uploads
  },

  // AI service calls
  ai: {
    quick: 30000,      // 30 seconds for quick AI operations
    standard: 120000,  // 2 minutes for standard operations
    complex: 600000,   // 10 minutes for complex operations
  },

  // File operations
  file: {
    read: 10000,       // 10 seconds for file reads
    write: 30000,      // 30 seconds for file writes
    process: 300000,   // 5 minutes for file processing
  },

  // Video processing
  video: {
    analyze: 120000,   // 2 minutes for video analysis
    process: 600000,   // 10 minutes for video processing
    upload: 1800000,   // 30 minutes for video uploads
  }
}

/**
 * Utility functions for common timeout patterns
 */
export function withDatabaseTimeout<T>(promise: Promise<T>, operation: keyof typeof timeouts.database = 'query'): Promise<T> {
  return withTimeout(promise, {
    timeoutMs: timeouts.database[operation],
    timeoutMessage: `Database ${operation} operation timed out`
  })
}

export function withAPITimeout<T>(promise: Promise<T>, operation: keyof typeof timeouts.api = 'standard'): Promise<T> {
  return withTimeout(promise, {
    timeoutMs: timeouts.api[operation],
    timeoutMessage: `API ${operation} operation timed out`
  })
}

export function withAITimeout<T>(promise: Promise<T>, operation: keyof typeof timeouts.ai = 'standard'): Promise<T> {
  return withTimeout(promise, {
    timeoutMs: timeouts.ai[operation],
    timeoutMessage: `AI ${operation} operation timed out`
  })
}

export function withFileTimeout<T>(promise: Promise<T>, operation: keyof typeof timeouts.file = 'read'): Promise<T> {
  return withTimeout(promise, {
    timeoutMs: timeouts.file[operation],
    timeoutMessage: `File ${operation} operation timed out`
  })
}

export function withVideoTimeout<T>(promise: Promise<T>, operation: keyof typeof timeouts.video = 'analyze'): Promise<T> {
  return withTimeout(promise, {
    timeoutMs: timeouts.video[operation],
    timeoutMessage: `Video ${operation} operation timed out`
  })
}

/**
 * Creates a timeout-aware async function wrapper
 */
export function timeoutWrapper<TArgs extends any[], TReturn>(
  fn: (...args: TArgs) => Promise<TReturn>,
  timeoutMs: number,
  timeoutMessage?: string
) {
  return async (...args: TArgs): Promise<TReturn> => {
    return withTimeout(fn(...args), {
      timeoutMs,
      timeoutMessage: timeoutMessage || `Function ${fn.name} timed out after ${timeoutMs}ms`
    })
  }
}

/**
 * Race multiple promises with a timeout
 */
export function raceWithTimeout<T>(
  promises: Promise<T>[],
  timeoutMs: number,
  timeoutMessage?: string
): Promise<T> {
  const timeoutPromise = new Promise<never>((_, reject) => {
    setTimeout(() => {
      reject(new TimeoutError(
        timeoutMessage || `Race timed out after ${timeoutMs}ms`,
        timeoutMs
      ))
    }, timeoutMs)
  })

  return Promise.race([...promises, timeoutPromise])
}