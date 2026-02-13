import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check basic application health
    const healthChecks = {
      timestamp: new Date().toISOString(),
      status: 'healthy',
      version: '2.0.0',
      environment: process.env.NODE_ENV,
      checks: {
        memory: checkMemoryUsage(),
        api: await checkAPIConnection(),
        supabase: await checkSupabaseConnection(),
        build: checkBuildHealth()
      }
    }

    // Determine overall status
    const hasFailures = Object.values(healthChecks.checks).some(check => check.status === 'fail')
    const hasWarnings = Object.values(healthChecks.checks).some(check => check.status === 'warn')
    
    if (hasFailures) {
      healthChecks.status = 'unhealthy'
      return NextResponse.json(healthChecks, { status: 503 })
    } else if (hasWarnings) {
      healthChecks.status = 'degraded'
    }

    return NextResponse.json(healthChecks, { status: 200 })
  } catch (error) {
    return NextResponse.json({
      timestamp: new Date().toISOString(),
      status: 'unhealthy',
      error: 'Health check failed to execute',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 503 })
  }
}

function checkMemoryUsage() {
  try {
    const memUsage = process.memoryUsage()
    const heapUsedMB = Math.round(memUsage.heapUsed / 1024 / 1024)
    const heapTotalMB = Math.round(memUsage.heapTotal / 1024 / 1024)
    const heapUsagePercent = Math.round((memUsage.heapUsed / memUsage.heapTotal) * 100)

    return {
      status: heapUsagePercent > 90 ? 'warn' : 'pass',
      memory: {
        heapUsed: `${heapUsedMB}MB`,
        heapTotal: `${heapTotalMB}MB`,
        usage: `${heapUsagePercent}%`
      }
    }
  } catch (error) {
    return {
      status: 'fail',
      error: 'Failed to check memory usage'
    }
  }
}

async function checkAPIConnection() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3003'
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout

    const response = await fetch(`${apiUrl}/health`, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'echo-website-health-check'
      }
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      return {
        status: 'fail',
        error: `API health check failed with status ${response.status}`
      }
    }

    const data = await response.json()
    return {
      status: data.status === 'healthy' ? 'pass' : 'warn',
      api: {
        url: apiUrl,
        status: data.status,
        responseTime: '<5s'
      }
    }
  } catch (error) {
    return {
      status: 'fail',
      error: error instanceof Error ? error.message : 'API connection failed'
    }
  }
}

async function checkSupabaseConnection() {
  try {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseKey) {
      return {
        status: 'fail',
        error: 'Supabase configuration missing'
      }
    }

    // Simple connectivity check
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)

    const response = await fetch(`${supabaseUrl}/rest/v1/`, {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`
      },
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    return {
      status: response.ok ? 'pass' : 'warn',
      supabase: {
        url: supabaseUrl,
        connected: response.ok
      }
    }
  } catch (error) {
    return {
      status: 'fail',
      error: error instanceof Error ? error.message : 'Supabase connection failed'
    }
  }
}

function checkBuildHealth() {
  try {
    // Check if we're in a proper build environment
    const nodeEnv = process.env.NODE_ENV
    const isProduction = nodeEnv === 'production'
    const hasBuildId = !!process.env.VERCEL_DEPLOYMENT_ID || !!process.env.BUILD_ID

    return {
      status: 'pass',
      build: {
        environment: nodeEnv,
        isProduction,
        buildId: process.env.VERCEL_DEPLOYMENT_ID || process.env.BUILD_ID || 'development',
        nextVersion: process.env.npm_package_dependencies_next || 'unknown'
      }
    }
  } catch (error) {
    return {
      status: 'warn',
      error: 'Failed to check build information'
    }
  }
}

// Also export as HEAD for uptime monitoring
export async function HEAD() {
  try {
    const response = await GET()
    return new NextResponse(null, { 
      status: response.status,
      headers: response.headers
    })
  } catch (error) {
    return new NextResponse(null, { status: 503 })
  }
}