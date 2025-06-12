import { Context, Next } from 'hono'

export interface LogEntry {
  timestamp: string
  method: string
  path: string
  status: number
  duration: number
  ip?: string
  userAgent?: string
  userId?: string
  requestId: string
}

export async function loggingMiddleware(c: Context, next: Next) {
  const start = Date.now()
  const requestId = c.req.header('X-Request-ID') || crypto.randomUUID()
  
  // Set request ID in context
  c.set('requestId', requestId)
  
  try {
    await next()
  } finally {
    const duration = Date.now() - start
    
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      method: c.req.method,
      path: c.req.path,
      status: c.res.status,
      duration,
      ip: c.req.header('X-Forwarded-For') || c.req.header('X-Real-IP'),
      userAgent: c.req.header('User-Agent'),
      requestId,
    }
    
    // Add user ID if available
    const user = c.get('user')
    if (user?.id) {
      logEntry.userId = user.id
    }
    
    // Log based on status
    if (c.res.status >= 500) {
      console.error('[ERROR]', JSON.stringify(logEntry))
    } else if (c.res.status >= 400) {
      console.warn('[WARN]', JSON.stringify(logEntry))
    } else {
      console.log('[INFO]', JSON.stringify(logEntry))
    }
  }
}

export function requestIdMiddleware(c: Context, next: Next) {
  const requestId = c.req.header('X-Request-ID') || crypto.randomUUID()
  c.header('X-Request-ID', requestId)
  return next()
}