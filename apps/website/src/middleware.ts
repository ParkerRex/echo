import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Simple in-memory rate limiter
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

function rateLimit(identifier: string, limit: number = 100, windowMs: number = 60000) {
  const now = Date.now()
  const windowStart = now - windowMs
  
  // Clean up old entries
  for (const [key, value] of rateLimitMap.entries()) {
    if (value.resetTime < windowStart) {
      rateLimitMap.delete(key)
    }
  }
  
  const current = rateLimitMap.get(identifier)
  
  if (!current) {
    rateLimitMap.set(identifier, { count: 1, resetTime: now })
    return { success: true, remaining: limit - 1 }
  }
  
  if (current.resetTime < windowStart) {
    rateLimitMap.set(identifier, { count: 1, resetTime: now })
    return { success: true, remaining: limit - 1 }
  }
  
  if (current.count >= limit) {
    return { success: false, remaining: 0 }
  }
  
  current.count++
  return { success: true, remaining: limit - current.count }
}

export async function middleware(request: NextRequest) {
  // Rate limiting
  const ip = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown'
  const identifier = `${ip}-${request.nextUrl.pathname}`
  
  // More aggressive rate limiting for auth routes
  const isAuthPath = request.nextUrl.pathname.startsWith('/auth/')
  const isAPIPath = request.nextUrl.pathname.startsWith('/api/')
  
  let limit = 100 // Default: 100 requests per minute
  if (isAuthPath) limit = 20 // Auth: 20 requests per minute
  if (isAPIPath) limit = 200 // API: 200 requests per minute
  
  const rateLimitResult = rateLimit(identifier, limit, 60000)
  
  if (!rateLimitResult.success) {
    return new NextResponse('Too Many Requests', { 
      status: 429,
      headers: {
        'Retry-After': '60',
        'X-RateLimit-Limit': limit.toString(),
        'X-RateLimit-Remaining': '0',
        'X-RateLimit-Reset': (Date.now() + 60000).toString()
      }
    })
  }

  let supabaseResponse = NextResponse.next({
    request,
  })
  
  // Add security headers
  supabaseResponse.headers.set('X-RateLimit-Limit', limit.toString())
  supabaseResponse.headers.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString())
  supabaseResponse.headers.set('X-RateLimit-Reset', (Date.now() + 60000).toString())
  supabaseResponse.headers.set('X-Content-Type-Options', 'nosniff')
  supabaseResponse.headers.set('X-Frame-Options', 'DENY')
  supabaseResponse.headers.set('X-XSS-Protection', '1; mode=block')
  supabaseResponse.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({
            request,
          })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  // Refresh session if expired - required for Server Components
  const { data: { user } } = await supabase.auth.getUser()

  // Check if user is accessing protected routes - ALL app functionality requires auth
  const protectedRoutes = ['/dashboard', '/creator', '/videos', '/api/trpc']
  const isProtectedRoute = protectedRoutes.some(route => request.nextUrl.pathname.startsWith(route))
  
  // Also protect any API routes that aren't public
  const publicAPIRoutes = ['/api/auth', '/api/health']
  const isAPIRoute = request.nextUrl.pathname.startsWith('/api/')
  const isPublicAPI = publicAPIRoutes.some(route => request.nextUrl.pathname.startsWith(route))
  const needsAuth = isProtectedRoute || (isAPIRoute && !isPublicAPI)
  
  // Redirect to login if accessing protected route without auth
  if (needsAuth && !user) {
    // For API calls, return 401 instead of redirect
    if (isAPIRoute) {
      return new NextResponse('Unauthorized', { status: 401 })
    }
    
    const redirectUrl = request.nextUrl.clone()
    redirectUrl.pathname = '/auth/login'
    redirectUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname)
    return NextResponse.redirect(redirectUrl)
  }

  // Redirect to dashboard if accessing auth pages while logged in
  const authRoutes = ['/auth/login', '/auth/signup']
  const isAuthRoute = authRoutes.some(route => request.nextUrl.pathname.startsWith(route))
  
  if (isAuthRoute && user) {
    // Check if there's a redirect URL from the original request
    const redirectTo = request.nextUrl.searchParams.get('redirectedFrom') || '/dashboard'
    return NextResponse.redirect(new URL(redirectTo, request.url))
  }

  return supabaseResponse
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}