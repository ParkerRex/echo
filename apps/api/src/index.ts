import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { trpcServer } from '@hono/trpc-server'
import { createContext } from './context'
import { appRouter } from './routers'
import { validateEnv, getEnv } from './types/env'
import { errorMiddleware } from './middleware/error'
import { loggingMiddleware, requestIdMiddleware } from './middleware/logging'
import { performHealthCheck, metrics } from './lib/health'
import { circuitBreakers } from './lib/circuit-breaker'

// Validate environment variables on startup
validateEnv()

const env = getEnv()
const app = new Hono()

// Global middleware
app.use('*', requestIdMiddleware)
app.use('*', loggingMiddleware)
app.use('*', errorMiddleware)
app.use(
  '*',
  cors({
    origin: env.CORS_ORIGINS?.split(',') || ['http://localhost:3001'],
    credentials: true,
  })
)

// Health check endpoints
app.get('/', (c) => {
  return c.json({
    status: 'ok',
    service: 'echo-core-api',
    version: '2.0.0',
    timestamp: new Date().toISOString(),
  })
})

// Comprehensive health check
app.get('/health', async (c) => {
  try {
    const health = await performHealthCheck()
    const statusCode = health.status === 'healthy' ? 200 : 
                      health.status === 'degraded' ? 200 : 503
    
    return c.json(health, statusCode as any)
  } catch (error) {
    console.error('Health check failed:', error)
    return c.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Health check execution failed'
    }, 503 as any)
  }
})

// Metrics endpoint
app.get('/metrics', (c) => {
  const appMetrics = metrics.getMetrics()
  
  // Add circuit breaker stats
  const circuitBreakerStats = {
    openai: circuitBreakers.openai.getStats(),
    youtube: circuitBreakers.youtube.getStats(),
    anthropic: circuitBreakers.anthropic.getStats(),
    database: circuitBreakers.database.getStats(),
  }
  
  return c.json({
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    ...appMetrics,
    circuitBreakers: circuitBreakerStats,
  })
})

// Readiness probe (for Kubernetes)
app.get('/ready', async (c) => {
  try {
    // Quick check of critical services
    const health = await performHealthCheck()
    const isReady = health.checks.database.status === 'pass' && 
                   health.checks.openai.status !== 'fail'
    
    if (isReady) {
      return c.json({ status: 'ready', timestamp: new Date().toISOString() })
    } else {
      return c.json({ status: 'not ready', timestamp: new Date().toISOString() }, 503 as any)
    }
  } catch (error) {
    return c.json({ status: 'not ready', error: 'Readiness check failed' }, 503 as any)
  }
})

// Liveness probe (for Kubernetes)
app.get('/live', (c) => {
  return c.json({ status: 'alive', timestamp: new Date().toISOString() })
})

// tRPC endpoint
app.use(
  '/trpc/*',
  trpcServer({
    router: appRouter,
    createContext: async (opts, c) => {
      return (await createContext(opts, c)) as any
    },
    endpoint: '/trpc',
  })
)

// Optional REST endpoints for webhooks or 3rd party integrations
app.post('/webhooks/stripe', async (c) => {
  // Handle Stripe webhooks
  return c.json({ received: true })
})

app.post('/webhooks/youtube', async (c) => {
  // Handle YouTube webhooks
  return c.json({ received: true })
})

// 404 handler
app.notFound((c) => {
  return c.json(
    {
      error: 'Not Found',
      message: `Route ${c.req.method} ${c.req.path} not found`,
    },
    404
  )
})

// Global error handler
app.onError((err, c) => {
  console.error(`Error in ${c.req.method} ${c.req.path}:`, err)

  return c.json(
    {
      error: 'Internal Server Error',
      message: env.NODE_ENV === 'development' ? err.message : 'Something went wrong',
    },
    500
  )
})

// Start server
const port = parseInt(env.PORT || '3003', 10)
const host = env.HOST || '0.0.0.0'

console.log(`🚀 Server starting...`)
console.log(`📍 Environment: ${env.NODE_ENV}`)
console.log(`🔗 tRPC endpoint: http://${host === '0.0.0.0' ? 'localhost' : host}:${port}/trpc`)
console.log(`🌐 Health check: http://${host === '0.0.0.0' ? 'localhost' : host}:${port}/`)

serve({
  fetch: app.fetch,
  port,
  hostname: host,
})
