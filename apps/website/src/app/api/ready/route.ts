import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Quick readiness check - only check critical services
    const checks = await Promise.allSettled([
      checkAPIReadiness(),
      checkSupabaseReadiness()
    ])

    const [apiCheck, supabaseCheck] = checks.map(result => 
      result.status === 'fulfilled' ? result.value : { ready: false, error: 'Check failed' }
    )

    const isReady = apiCheck?.ready && supabaseCheck?.ready

    if (isReady) {
      return NextResponse.json({
        status: 'ready',
        timestamp: new Date().toISOString(),
        checks: {
          api: apiCheck,
          supabase: supabaseCheck
        }
      })
    } else {
      return NextResponse.json({
        status: 'not ready',
        timestamp: new Date().toISOString(),
        checks: {
          api: apiCheck,
          supabase: supabaseCheck
        }
      }, { status: 503 })
    }
  } catch (error) {
    return NextResponse.json({
      status: 'not ready',
      timestamp: new Date().toISOString(),
      error: 'Readiness check failed'
    }, { status: 503 })
  }
}

async function checkAPIReadiness() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3003'
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 3000) // Quick 3 second timeout

    const response = await fetch(`${apiUrl}/ready`, {
      signal: controller.signal
    })

    clearTimeout(timeoutId)
    return {
      ready: response.ok,
      url: apiUrl
    }
  } catch (error) {
    return {
      ready: false,
      error: 'API not ready'
    }
  }
}

async function checkSupabaseReadiness() {
  try {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!supabaseUrl || !supabaseKey) {
      return {
        ready: false,
        error: 'Supabase not configured'
      }
    }

    // Quick ping to Supabase
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 3000)

    const response = await fetch(`${supabaseUrl}/rest/v1/`, {
      method: 'HEAD',
      headers: {
        'apikey': supabaseKey
      },
      signal: controller.signal
    })

    clearTimeout(timeoutId)
    return {
      ready: response.ok,
      url: supabaseUrl
    }
  } catch (error) {
    return {
      ready: false,
      error: 'Supabase not ready'
    }
  }
}

export async function HEAD() {
  const response = await GET()
  return new NextResponse(null, { 
    status: response.status,
    headers: response.headers
  })
}