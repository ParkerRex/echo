/**
 * Circuit Breaker Pattern Implementation
 * 
 * Prevents cascading failures by monitoring external service calls
 * and failing fast when a service is unavailable.
 */

export enum CircuitState {
  CLOSED = 'CLOSED',     // Normal operation
  OPEN = 'OPEN',         // Circuit is open, failing fast
  HALF_OPEN = 'HALF_OPEN' // Testing if service is back up
}

export interface CircuitBreakerOptions {
  failureThreshold: number    // Number of failures before opening circuit
  successThreshold: number    // Number of successes needed to close circuit (from half-open)
  timeout: number            // Time to wait before moving from open to half-open (ms)
  resetTimeout: number       // Time to reset failure count (ms)
  onStateChange?: (state: CircuitState) => void
}

export interface CircuitBreakerStats {
  state: CircuitState
  failures: number
  successes: number
  lastFailureTime: number | null
  lastSuccessTime: number | null
  totalRequests: number
  totalFailures: number
  totalSuccesses: number
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED
  private failures = 0
  private successes = 0
  private lastFailureTime: number | null = null
  private lastSuccessTime: number | null = null
  private totalRequests = 0
  private totalFailures = 0
  private totalSuccesses = 0

  constructor(private options: CircuitBreakerOptions) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    this.totalRequests++

    if (this.state === CircuitState.OPEN) {
      if (this.shouldAttemptReset()) {
        this.state = CircuitState.HALF_OPEN
        this.notifyStateChange()
      } else {
        throw new CircuitBreakerError('Circuit breaker is OPEN')
      }
    }

    try {
      const result = await fn()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  private onSuccess(): void {
    this.successes++
    this.totalSuccesses++
    this.lastSuccessTime = Date.now()

    if (this.state === CircuitState.HALF_OPEN) {
      if (this.successes >= this.options.successThreshold) {
        this.reset()
      }
    } else {
      this.failures = 0 // Reset failure count on success
    }
  }

  private onFailure(): void {
    this.failures++
    this.totalFailures++
    this.lastFailureTime = Date.now()

    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN
      this.notifyStateChange()
    } else if (this.failures >= this.options.failureThreshold) {
      this.state = CircuitState.OPEN
      this.notifyStateChange()
    }
  }

  private shouldAttemptReset(): boolean {
    return (
      this.lastFailureTime !== null &&
      Date.now() - this.lastFailureTime >= this.options.timeout
    )
  }

  private reset(): void {
    this.state = CircuitState.CLOSED
    this.failures = 0
    this.successes = 0
    this.notifyStateChange()
  }

  private notifyStateChange(): void {
    if (this.options.onStateChange) {
      this.options.onStateChange(this.state)
    }
  }

  getStats(): CircuitBreakerStats {
    return {
      state: this.state,
      failures: this.failures,
      successes: this.successes,
      lastFailureTime: this.lastFailureTime,
      lastSuccessTime: this.lastSuccessTime,
      totalRequests: this.totalRequests,
      totalFailures: this.totalFailures,
      totalSuccesses: this.totalSuccesses,
    }
  }

  // Manual control methods
  forceOpen(): void {
    this.state = CircuitState.OPEN
    this.notifyStateChange()
  }

  forceClose(): void {
    this.reset()
  }

  forceClosed(): void {
    this.state = CircuitState.CLOSED
    this.notifyStateChange()
  }
}

export class CircuitBreakerError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'CircuitBreakerError'
  }
}

// Pre-configured circuit breakers for different services
export const circuitBreakers = {
  openai: new CircuitBreaker({
    failureThreshold: 5,
    successThreshold: 3,
    timeout: 60000, // 1 minute
    resetTimeout: 300000, // 5 minutes
    onStateChange: (state) => {
      console.log(`[CIRCUIT BREAKER] OpenAI circuit breaker state changed to: ${state}`)
    }
  }),

  youtube: new CircuitBreaker({
    failureThreshold: 3,
    successThreshold: 2,
    timeout: 30000, // 30 seconds
    resetTimeout: 180000, // 3 minutes
    onStateChange: (state) => {
      console.log(`[CIRCUIT BREAKER] YouTube circuit breaker state changed to: ${state}`)
    }
  }),

  anthropic: new CircuitBreaker({
    failureThreshold: 5,
    successThreshold: 3,
    timeout: 60000, // 1 minute
    resetTimeout: 300000, // 5 minutes
    onStateChange: (state) => {
      console.log(`[CIRCUIT BREAKER] Anthropic circuit breaker state changed to: ${state}`)
    }
  }),

  database: new CircuitBreaker({
    failureThreshold: 3,
    successThreshold: 2,
    timeout: 10000, // 10 seconds
    resetTimeout: 60000, // 1 minute
    onStateChange: (state) => {
      console.log(`[CIRCUIT BREAKER] Database circuit breaker state changed to: ${state}`)
    }
  })
}

// Utility function to wrap any async function with a circuit breaker
export function withCircuitBreaker<T extends any[], R>(
  circuitBreaker: CircuitBreaker,
  fn: (...args: T) => Promise<R>
) {
  return async (...args: T): Promise<R> => {
    return circuitBreaker.execute(() => fn(...args))
  }
}