/**
 * Error Tracking and Alerting System
 * 
 * Comprehensive error tracking, alerting, and monitoring
 * for production applications with rate limiting and
 * intelligent alert aggregation.
 */

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum ErrorCategory {
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  VALIDATION = 'validation',
  DATABASE = 'database',
  EXTERNAL_API = 'external_api',
  FILE_SYSTEM = 'file_system',
  NETWORK = 'network',
  TIMEOUT = 'timeout',
  RATE_LIMIT = 'rate_limit',
  BUSINESS_LOGIC = 'business_logic',
  SYSTEM = 'system',
  UNKNOWN = 'unknown'
}

export interface ErrorContext {
  userId?: string
  requestId?: string
  sessionId?: string
  userAgent?: string
  ip?: string
  url?: string
  method?: string
  headers?: Record<string, string>
  body?: any
  query?: Record<string, string>
  environment?: string
  version?: string
  timestamp?: string
  [key: string]: any
}

export interface TrackedError {
  id: string
  message: string
  stack?: string
  category: ErrorCategory
  severity: ErrorSeverity
  context: ErrorContext
  timestamp: number
  count: number
  firstSeen: number
  lastSeen: number
  fingerprint: string
  resolved: boolean
  resolvedAt?: number
  resolvedBy?: string
}

export interface AlertRule {
  id: string
  name: string
  condition: AlertCondition
  severity: ErrorSeverity
  channels: AlertChannel[]
  rateLimitMinutes: number
  enabled: boolean
}

export interface AlertCondition {
  type: 'error_rate' | 'error_count' | 'specific_error' | 'circuit_breaker'
  threshold?: number
  timeWindowMinutes?: number
  errorPattern?: string
  category?: ErrorCategory
  severity?: ErrorSeverity
}

export interface AlertChannel {
  type: 'console' | 'email' | 'slack' | 'webhook'
  config: Record<string, any>
}

export interface Alert {
  id: string
  ruleId: string
  title: string
  message: string
  severity: ErrorSeverity
  timestamp: number
  resolved: boolean
  data: any
}

class ErrorTracker {
  private errors: Map<string, TrackedError> = new Map()
  private alerts: Map<string, Alert> = new Map()
  private alertRules: Map<string, AlertRule> = new Map()
  private alertHistory: Map<string, number> = new Map() // For rate limiting
  private errorCounts: Map<string, { count: number; windowStart: number }> = new Map()

  constructor() {
    this.setupDefaultAlertRules()
    this.startBackgroundTasks()
  }

  /**
   * Track an error with automatic categorization and fingerprinting
   */
  trackError(
    error: Error | string,
    context: ErrorContext = {},
    category?: ErrorCategory,
    severity?: ErrorSeverity
  ): string {
    const timestamp = Date.now()
    const errorMessage = typeof error === 'string' ? error : error.message
    const errorStack = typeof error === 'string' ? undefined : error.stack

    // Auto-categorize if not provided
    const detectedCategory = category || this.categorizeError(error, context)
    const detectedSeverity = severity || this.determineSeverity(error, detectedCategory, context)

    // Generate fingerprint for error grouping
    const fingerprint = this.generateFingerprint(errorMessage, errorStack, detectedCategory)

    // Add environment context
    const enrichedContext: ErrorContext = {
      environment: process.env.NODE_ENV,
      version: '2.0.0',
      timestamp: new Date(timestamp).toISOString(),
      ...context
    }

    // Check if we've seen this error before
    const existingError = this.errors.get(fingerprint)
    
    if (existingError) {
      // Update existing error
      existingError.count++
      existingError.lastSeen = timestamp
      existingError.context = { ...existingError.context, ...enrichedContext }
      
      // Update severity if this instance is more severe
      if (this.severityWeight(detectedSeverity) > this.severityWeight(existingError.severity)) {
        existingError.severity = detectedSeverity
      }
    } else {
      // Create new error
      const trackedError: TrackedError = {
        id: this.generateId(),
        message: errorMessage,
        stack: errorStack,
        category: detectedCategory,
        severity: detectedSeverity,
        context: enrichedContext,
        timestamp,
        count: 1,
        firstSeen: timestamp,
        lastSeen: timestamp,
        fingerprint,
        resolved: false
      }

      this.errors.set(fingerprint, trackedError)
    }

    // Update error rate tracking
    this.updateErrorRateTracking(detectedCategory, detectedSeverity)

    // Check alert rules
    this.checkAlertRules(fingerprint)

    // Log error
    this.logError(this.errors.get(fingerprint)!)

    return fingerprint
  }

  /**
   * Categorize error based on error type and context
   */
  private categorizeError(error: Error | string, context: ErrorContext): ErrorCategory {
    const errorMessage = typeof error === 'string' ? error : error.message
    const errorName = typeof error === 'string' ? 'Error' : error.constructor.name

    // Authentication errors
    if (errorMessage.includes('unauthorized') || errorMessage.includes('authentication') ||
        errorName.includes('Auth') || context.url?.includes('/auth/')) {
      return ErrorCategory.AUTHENTICATION
    }

    // Authorization errors
    if (errorMessage.includes('forbidden') || errorMessage.includes('permission') ||
        errorMessage.includes('access denied')) {
      return ErrorCategory.AUTHORIZATION
    }

    // Validation errors
    if (errorMessage.includes('validation') || errorMessage.includes('invalid') ||
        errorName.includes('Validation') || errorName.includes('Zod')) {
      return ErrorCategory.VALIDATION
    }

    // Database errors
    if (errorMessage.includes('database') || errorMessage.includes('connection') ||
        errorMessage.includes('postgres') || errorMessage.includes('query') ||
        errorName.includes('Database') || errorName.includes('SQL')) {
      return ErrorCategory.DATABASE
    }

    // Timeout errors
    if (errorMessage.includes('timeout') || errorMessage.includes('ETIMEDOUT') ||
        errorName.includes('Timeout')) {
      return ErrorCategory.TIMEOUT
    }

    // Network errors
    if (errorMessage.includes('ECONNREFUSED') || errorMessage.includes('ENOTFOUND') ||
        errorMessage.includes('network') || errorName.includes('Network')) {
      return ErrorCategory.NETWORK
    }

    // External API errors
    if (context.url?.includes('/api/') || errorMessage.includes('API') ||
        errorMessage.includes('fetch') || errorMessage.includes('HTTP')) {
      return ErrorCategory.EXTERNAL_API
    }

    // File system errors
    if (errorMessage.includes('ENOENT') || errorMessage.includes('EACCES') ||
        errorMessage.includes('file') || errorMessage.includes('directory')) {
      return ErrorCategory.FILE_SYSTEM
    }

    // Rate limit errors
    if (errorMessage.includes('rate limit') || errorMessage.includes('too many requests') ||
        context.method && this.isRateLimitError(context)) {
      return ErrorCategory.RATE_LIMIT
    }

    return ErrorCategory.UNKNOWN
  }

  /**
   * Determine error severity based on category and context
   */
  private determineSeverity(
    error: Error | string, 
    category: ErrorCategory, 
    context: ErrorContext
  ): ErrorSeverity {
    const errorMessage = typeof error === 'string' ? error : error.message

    // Critical severity conditions
    if (category === ErrorCategory.DATABASE && errorMessage.includes('connection')) {
      return ErrorSeverity.CRITICAL
    }
    if (errorMessage.includes('SIGTERM') || errorMessage.includes('SIGKILL')) {
      return ErrorSeverity.CRITICAL
    }
    if (context.url?.includes('/health') || context.url?.includes('/ready')) {
      return ErrorSeverity.CRITICAL
    }

    // High severity conditions
    if (category === ErrorCategory.AUTHENTICATION && context.userId) {
      return ErrorSeverity.HIGH
    }
    if (category === ErrorCategory.DATABASE) {
      return ErrorSeverity.HIGH
    }
    if (category === ErrorCategory.EXTERNAL_API && errorMessage.includes('payment')) {
      return ErrorSeverity.HIGH
    }

    // Medium severity conditions
    if (category === ErrorCategory.AUTHORIZATION) {
      return ErrorSeverity.MEDIUM
    }
    if (category === ErrorCategory.EXTERNAL_API) {
      return ErrorSeverity.MEDIUM
    }
    if (category === ErrorCategory.TIMEOUT) {
      return ErrorSeverity.MEDIUM
    }

    // Default to low severity
    return ErrorSeverity.LOW
  }

  /**
   * Generate error fingerprint for grouping similar errors
   */
  private generateFingerprint(message: string, stack?: string, category?: ErrorCategory): string {
    const crypto = require('crypto')
    
    // Normalize message by removing dynamic parts
    const normalizedMessage = message
      .replace(/\d+/g, 'N') // Replace numbers
      .replace(/[a-f0-9-]{8,}/gi, 'ID') // Replace IDs/hashes
      .replace(/https?:\/\/[^\s]+/gi, 'URL') // Replace URLs
      .replace(/\b\w+@\w+\.\w+\b/gi, 'EMAIL') // Replace emails

    // Use first few lines of stack trace for fingerprint
    const stackLines = stack?.split('\n').slice(0, 3).join('\n') || ''
    
    const fingerprintData = `${category}:${normalizedMessage}:${stackLines}`
    return crypto.createHash('md5').update(fingerprintData).digest('hex')
  }

  /**
   * Set up default alert rules
   */
  private setupDefaultAlertRules(): void {
    // High error rate alert
    this.alertRules.set('high_error_rate', {
      id: 'high_error_rate',
      name: 'High Error Rate',
      condition: {
        type: 'error_rate',
        threshold: 10, // 10 errors per minute
        timeWindowMinutes: 5
      },
      severity: ErrorSeverity.HIGH,
      channels: [{ type: 'console', config: {} }],
      rateLimitMinutes: 15,
      enabled: true
    })

    // Critical errors alert
    this.alertRules.set('critical_errors', {
      id: 'critical_errors',
      name: 'Critical Error Detected',
      condition: {
        type: 'specific_error',
        severity: ErrorSeverity.CRITICAL
      },
      severity: ErrorSeverity.CRITICAL,
      channels: [{ type: 'console', config: {} }],
      rateLimitMinutes: 5,
      enabled: true
    })

    // Database connection failures
    this.alertRules.set('database_failures', {
      id: 'database_failures',
      name: 'Database Connection Failures',
      condition: {
        type: 'error_count',
        threshold: 3,
        timeWindowMinutes: 5,
        category: ErrorCategory.DATABASE
      },
      severity: ErrorSeverity.CRITICAL,
      channels: [{ type: 'console', config: {} }],
      rateLimitMinutes: 10,
      enabled: true
    })
  }

  /**
   * Check alert rules and trigger alerts if conditions are met
   */
  private checkAlertRules(errorFingerprint: string): void {
    const error = this.errors.get(errorFingerprint)
    if (!error) return

    for (const rule of this.alertRules.values()) {
      if (!rule.enabled) continue

      // Check rate limiting
      const lastAlertTime = this.alertHistory.get(rule.id) || 0
      const rateLimitMs = rule.rateLimitMinutes * 60 * 1000
      if (Date.now() - lastAlertTime < rateLimitMs) {
        continue
      }

      if (this.checkAlertCondition(rule.condition, error)) {
        this.triggerAlert(rule, error)
        this.alertHistory.set(rule.id, Date.now())
      }
    }
  }

  /**
   * Check if alert condition is met
   */
  private checkAlertCondition(condition: AlertCondition, error: TrackedError): boolean {
    switch (condition.type) {
      case 'specific_error':
        if (condition.severity && error.severity !== condition.severity) return false
        if (condition.category && error.category !== condition.category) return false
        if (condition.errorPattern && !error.message.includes(condition.errorPattern)) return false
        return true

      case 'error_count':
        return this.checkErrorCountCondition(condition)

      case 'error_rate':
        return this.checkErrorRateCondition(condition)

      default:
        return false
    }
  }

  /**
   * Trigger an alert
   */
  private triggerAlert(rule: AlertRule, error: TrackedError): void {
    const alert: Alert = {
      id: this.generateId(),
      ruleId: rule.id,
      title: rule.name,
      message: this.generateAlertMessage(rule, error),
      severity: rule.severity,
      timestamp: Date.now(),
      resolved: false,
      data: { error, rule }
    }

    this.alerts.set(alert.id, alert)

    // Send alert through configured channels
    for (const channel of rule.channels) {
      this.sendAlert(alert, channel)
    }
  }

  /**
   * Generate alert message
   */
  private generateAlertMessage(rule: AlertRule, error: TrackedError): string {
    return `Alert: ${rule.name}\n` +
           `Error: ${error.message}\n` +
           `Category: ${error.category}\n` +
           `Severity: ${error.severity}\n` +
           `Count: ${error.count}\n` +
           `First seen: ${new Date(error.firstSeen).toISOString()}\n` +
           `Context: ${JSON.stringify(error.context, null, 2)}`
  }

  /**
   * Send alert through specified channel
   */
  private sendAlert(alert: Alert, channel: AlertChannel): void {
    switch (channel.type) {
      case 'console':
        console.error(`🚨 [ALERT] ${alert.title}`)
        console.error(alert.message)
        break

      case 'email':
        // Implement email sending
        console.log(`📧 Email alert would be sent: ${alert.title}`)
        break

      case 'slack':
        // Implement Slack webhook
        console.log(`💬 Slack alert would be sent: ${alert.title}`)
        break

      case 'webhook':
        // Implement webhook
        console.log(`🔗 Webhook alert would be sent: ${alert.title}`)
        break
    }
  }

  /**
   * Log error with appropriate level
   */
  private logError(error: TrackedError): void {
    const logData = {
      id: error.id,
      message: error.message,
      category: error.category,
      severity: error.severity,
      count: error.count,
      context: error.context
    }

    switch (error.severity) {
      case ErrorSeverity.CRITICAL:
        console.error('[CRITICAL ERROR]', JSON.stringify(logData, null, 2))
        break
      case ErrorSeverity.HIGH:
        console.error('[HIGH ERROR]', JSON.stringify(logData))
        break
      case ErrorSeverity.MEDIUM:
        console.warn('[MEDIUM ERROR]', JSON.stringify(logData))
        break
      case ErrorSeverity.LOW:
        console.log('[LOW ERROR]', JSON.stringify(logData))
        break
    }
  }

  // Utility methods
  private generateId(): string {
    return Math.random().toString(36).substring(2) + Date.now().toString(36)
  }

  private severityWeight(severity: ErrorSeverity): number {
    const weights = {
      [ErrorSeverity.LOW]: 1,
      [ErrorSeverity.MEDIUM]: 2,
      [ErrorSeverity.HIGH]: 3,
      [ErrorSeverity.CRITICAL]: 4
    }
    return weights[severity]
  }

  private isRateLimitError(context: ErrorContext): boolean {
    return false // Implement rate limit detection logic
  }

  private updateErrorRateTracking(category: ErrorCategory, severity: ErrorSeverity): void {
    // Implement error rate tracking
  }

  private checkErrorCountCondition(condition: AlertCondition): boolean {
    // Implement error count checking
    return false
  }

  private checkErrorRateCondition(condition: AlertCondition): boolean {
    // Implement error rate checking
    return false
  }

  private startBackgroundTasks(): void {
    // Clean up old errors and alerts periodically
    setInterval(() => {
      this.cleanupOldData()
    }, 60000) // Run every minute
  }

  private cleanupOldData(): void {
    const retentionPeriod = 7 * 24 * 60 * 60 * 1000 // 7 days
    const cutoff = Date.now() - retentionPeriod

    // Clean up old errors
    for (const [fingerprint, error] of this.errors.entries()) {
      if (error.lastSeen < cutoff) {
        this.errors.delete(fingerprint)
      }
    }

    // Clean up old alerts
    for (const [id, alert] of this.alerts.entries()) {
      if (alert.timestamp < cutoff) {
        this.alerts.delete(id)
      }
    }
  }

  // Public API methods
  getErrors(): TrackedError[] {
    return Array.from(this.errors.values())
  }

  getAlerts(): Alert[] {
    return Array.from(this.alerts.values())
  }

  resolveError(fingerprint: string, resolvedBy?: string): boolean {
    const error = this.errors.get(fingerprint)
    if (error) {
      error.resolved = true
      error.resolvedAt = Date.now()
      error.resolvedBy = resolvedBy
      return true
    }
    return false
  }

  getErrorStats(): any {
    const errors = this.getErrors()
    const total = errors.length
    const bySeverity = errors.reduce((acc, error) => {
      acc[error.severity] = (acc[error.severity] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    const byCategory = errors.reduce((acc, error) => {
      acc[error.category] = (acc[error.category] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      total,
      bySeverity,
      byCategory,
      resolved: errors.filter(e => e.resolved).length,
      unresolved: errors.filter(e => !e.resolved).length
    }
  }
}

// Export singleton instance
export const errorTracker = new ErrorTracker()

// Convenience functions
export function trackError(
  error: Error | string,
  context?: ErrorContext,
  category?: ErrorCategory,
  severity?: ErrorSeverity
): string {
  return errorTracker.trackError(error, context, category, severity)
}

export function resolveError(fingerprint: string, resolvedBy?: string): boolean {
  return errorTracker.resolveError(fingerprint, resolvedBy)
}

export function getErrorStats() {
  return errorTracker.getErrorStats()
}