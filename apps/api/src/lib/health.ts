import { db } from '../db/client'
import { getEnv } from '../types/env'

export interface HealthCheckResult {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  version: string
  checks: {
    database: HealthCheck
    openai: HealthCheck
    youtube: HealthCheck
    storage: HealthCheck
    memory: HealthCheck
  }
  uptime: number
}

export interface HealthCheck {
  status: 'pass' | 'warn' | 'fail'
  time: number
  output?: string
  error?: string
}

const startTime = Date.now()

export async function performHealthCheck(): Promise<HealthCheckResult> {
  const env = getEnv()
  const timestamp = new Date().toISOString()
  const uptime = Math.floor((Date.now() - startTime) / 1000)

  const checks = await Promise.allSettled([
    checkDatabase(),
    checkOpenAI(),
    checkYouTube(),
    checkStorage(),
    checkMemory(),
  ])

  const [database, openai, youtube, storage, memory] = checks.map(result => 
    result.status === 'fulfilled' ? result.value : {
      status: 'fail' as const,
      time: 0,
      error: 'Health check failed to execute'
    }
  ) as [HealthCheck, HealthCheck, HealthCheck, HealthCheck, HealthCheck]

  // Determine overall status
  const criticalChecks = [database, openai]
  const hasCriticalFailures = criticalChecks.some(check => check.status === 'fail')
  const hasWarnings = Object.values({ database, openai, youtube, storage, memory })
    .some(check => check.status === 'warn')

  let status: 'healthy' | 'degraded' | 'unhealthy'
  if (hasCriticalFailures) {
    status = 'unhealthy'
  } else if (hasWarnings) {
    status = 'degraded'
  } else {
    status = 'healthy'
  }

  return {
    status,
    timestamp,
    version: '2.0.0',
    checks: {
      database,
      openai,
      youtube,
      storage,
      memory,
    },
    uptime,
  }
}

async function checkDatabase(): Promise<HealthCheck> {
  const start = performance.now()
  
  try {
    // Simple query to check database connectivity
    await db.execute('SELECT 1')
    
    const time = Math.round(performance.now() - start)
    
    if (time > 1000) {
      return {
        status: 'warn',
        time,
        output: 'Database responding slowly'
      }
    }
    
    return {
      status: 'pass',
      time,
      output: 'Database connection healthy'
    }
  } catch (error) {
    return {
      status: 'fail',
      time: Math.round(performance.now() - start),
      error: error instanceof Error ? error.message : 'Database connection failed'
    }
  }
}

async function checkOpenAI(): Promise<HealthCheck> {
  const start = performance.now()
  const env = getEnv()
  
  try {
    if (!env.OPENAI_API_KEY) {
      return {
        status: 'fail',
        time: 0,
        error: 'OpenAI API key not configured'
      }
    }

    // Simple API call to check OpenAI connectivity
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
      },
      signal: AbortSignal.timeout(5000) // 5 second timeout
    })
    
    const time = Math.round(performance.now() - start)
    
    if (!response.ok) {
      return {
        status: 'fail',
        time,
        error: `OpenAI API returned ${response.status}`
      }
    }
    
    if (time > 3000) {
      return {
        status: 'warn',
        time,
        output: 'OpenAI API responding slowly'
      }
    }
    
    return {
      status: 'pass',
      time,
      output: 'OpenAI API healthy'
    }
  } catch (error) {
    return {
      status: 'fail',
      time: Math.round(performance.now() - start),
      error: error instanceof Error ? error.message : 'OpenAI API check failed'
    }
  }
}

async function checkYouTube(): Promise<HealthCheck> {
  const start = performance.now()
  const env = getEnv()
  
  try {
    if (!env.GOOGLE_CLIENT_ID || !env.GOOGLE_CLIENT_SECRET) {
      return {
        status: 'warn',
        time: 0,
        output: 'YouTube credentials not configured'
      }
    }

    // Simple check of YouTube API availability (if key exists)
    const apiKey = (env as any).YOUTUBE_API_KEY
    if (!apiKey) {
      return {
        status: 'warn',
        time: 0,
        output: 'YouTube API key not configured'
      }
    }
    
    const response = await fetch('https://www.googleapis.com/youtube/v3/videos?part=id&maxResults=1&key=' + apiKey, {
      signal: AbortSignal.timeout(5000)
    })
    
    const time = Math.round(performance.now() - start)
    
    if (!response.ok) {
      return {
        status: 'warn',
        time,
        output: `YouTube API returned ${response.status}`
      }
    }
    
    return {
      status: 'pass',
      time,
      output: 'YouTube API healthy'
    }
  } catch (error) {
    return {
      status: 'warn',
      time: Math.round(performance.now() - start),
      output: 'YouTube API check failed - non-critical'
    }
  }
}

async function checkStorage(): Promise<HealthCheck> {
  const start = performance.now()
  
  try {
    // Check available disk space
    const stats = await import('fs').then(fs => fs.promises.stat('.'))
    
    const time = Math.round(performance.now() - start)
    
    return {
      status: 'pass',
      time,
      output: 'Storage accessible'
    }
  } catch (error) {
    return {
      status: 'warn',
      time: Math.round(performance.now() - start),
      output: 'Storage check failed - non-critical'
    }
  }
}

async function checkMemory(): Promise<HealthCheck> {
  const start = performance.now()
  
  try {
    const memUsage = process.memoryUsage()
    const heapUsedMB = Math.round(memUsage.heapUsed / 1024 / 1024)
    const heapTotalMB = Math.round(memUsage.heapTotal / 1024 / 1024)
    const heapUsagePercent = Math.round((memUsage.heapUsed / memUsage.heapTotal) * 100)
    
    const time = Math.round(performance.now() - start)
    
    if (heapUsagePercent > 90) {
      return {
        status: 'warn',
        time,
        output: `High memory usage: ${heapUsedMB}MB (${heapUsagePercent}%)`
      }
    }
    
    return {
      status: 'pass',
      time,
      output: `Memory usage: ${heapUsedMB}MB / ${heapTotalMB}MB (${heapUsagePercent}%)`
    }
  } catch (error) {
    return {
      status: 'warn',
      time: Math.round(performance.now() - start),
      output: 'Memory check failed'
    }
  }
}

// Simple metrics collection
export interface Metrics {
  requests: {
    total: number
    success: number
    errors: number
    avgResponseTime: number
  }
  database: {
    connections: number
    queries: number
    errors: number
    avgQueryTime: number
  }
  memory: {
    heapUsed: number
    heapTotal: number
    external: number
    rss: number
  }
}

class MetricsCollector {
  private requestCount = 0
  private successCount = 0
  private errorCount = 0
  private totalResponseTime = 0
  private dbQueryCount = 0
  private dbErrorCount = 0
  private totalDbTime = 0

  recordRequest(responseTime: number, success: boolean) {
    this.requestCount++
    this.totalResponseTime += responseTime
    
    if (success) {
      this.successCount++
    } else {
      this.errorCount++
    }
  }

  recordDbQuery(queryTime: number, success: boolean) {
    this.dbQueryCount++
    this.totalDbTime += queryTime
    
    if (!success) {
      this.dbErrorCount++
    }
  }

  getMetrics(): Metrics {
    const memUsage = process.memoryUsage()
    
    return {
      requests: {
        total: this.requestCount,
        success: this.successCount,
        errors: this.errorCount,
        avgResponseTime: this.requestCount > 0 ? this.totalResponseTime / this.requestCount : 0,
      },
      database: {
        connections: 1, // Simple single connection for now
        queries: this.dbQueryCount,
        errors: this.dbErrorCount,
        avgQueryTime: this.dbQueryCount > 0 ? this.totalDbTime / this.dbQueryCount : 0,
      },
      memory: {
        heapUsed: memUsage.heapUsed,
        heapTotal: memUsage.heapTotal,
        external: memUsage.external,
        rss: memUsage.rss,
      },
    }
  }

  reset() {
    this.requestCount = 0
    this.successCount = 0
    this.errorCount = 0
    this.totalResponseTime = 0
    this.dbQueryCount = 0
    this.dbErrorCount = 0
    this.totalDbTime = 0
  }
}

export const metrics = new MetricsCollector()