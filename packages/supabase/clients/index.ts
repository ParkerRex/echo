import { createBrowserClient, createServerClient } from '@supabase/ssr'
import { parseCookies, setCookie } from '@tanstack/react-start/server'
import type { Database } from '../types/database'

/**
 * Get validated environment variables for Supabase
 * Ensures proper configuration in both server and client contexts
 */
function getSupabaseConfig() {
  const isServer = typeof window === 'undefined'

  if (isServer) {
    // Server-side configuration
    const url = process.env.SUPABASE_URL
    const anonKey = process.env.SUPABASE_ANON_KEY

    if (!url || !anonKey) {
      throw new Error(
        'Missing required Supabase environment variables. ' +
          'Please ensure SUPABASE_URL and SUPABASE_ANON_KEY are set.'
      )
    }

    return { url, anonKey }
  } else {
    // Client-side configuration
    const url = import.meta.env.VITE_SUPABASE_URL
    const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

    if (!url || !anonKey) {
      throw new Error(
        'Missing required Supabase environment variables. ' +
          'Please ensure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are set.'
      )
    }

    return { url, anonKey }
  }
}

/**
 * TanStack Start compatible Supabase server client
 * Uses parseCookies and setCookie from @tanstack/react-start/server
 * Includes proper error handling and cookie configuration
 */
export function getSupabaseServerClient() {
  const { url, anonKey } = getSupabaseConfig()

  return createServerClient<Database>(url, anonKey, {
    cookies: {
      getAll() {
        try {
          return Object.entries(parseCookies()).map(([name, value]) => ({
            name,
            value,
          }))
        } catch (error) {
          console.error('Error parsing cookies:', error)
          return []
        }
      },
      setAll(cookies) {
        try {
          cookies.forEach((cookie) => {
            setCookie(cookie.name, cookie.value, {
              httpOnly: true,
              secure: process.env.NODE_ENV === 'production',
              sameSite: 'lax',
              maxAge: 60 * 60 * 24 * 7, // 7 days
              path: '/',
            })
          })
        } catch (error) {
          console.error('Error setting cookies:', error)
        }
      },
    },
  })
}

/**
 * Universal Supabase client factory
 * Creates appropriate client based on context (browser vs server)
 *
 * @param context - Force specific context ('browser' | 'server'), auto-detected if not provided
 * @returns Configured Supabase client
 */
export function createSupabaseClient(context?: 'browser' | 'server') {
  // Auto-detect context if not provided
  const actualContext = context || (typeof window === 'undefined' ? 'server' : 'browser')

  if (actualContext === 'server') {
    // Server context - use the TanStack Start compatible client
    return getSupabaseServerClient()
  }

  // Browser context - create browser client with proper configuration
  const { url, anonKey } = getSupabaseConfig()

  return createBrowserClient<Database>(url, anonKey, {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
      flowType: 'pkce', // Use PKCE flow for better security
    },
    global: {
      headers: {
        'X-Client-Info': 'echo-web-app',
      },
    },
  })
}

/**
 * Browser client for client-side operations
 * Use this in React components and client-side code
 */
export const supabaseBrowser = () => createSupabaseClient('browser')

/**
 * Server client for server-side operations
 * Use this in server functions and API routes
 */
export const supabaseServer = () => createSupabaseClient('server')

/**
 * Default client instance with auto-detection
 * Automatically chooses browser or server client based on context
 * Lazy initialization to avoid SSR issues
 */
export const supabase = () => createSupabaseClient()

/**
 * Legacy compatibility function
 * @deprecated Use getSupabaseServerClient() instead for TanStack Start compatibility
 */
export const getSupabase = () => {
  console.warn(
    'getSupabase() is deprecated. Use getSupabaseServerClient() for server-side operations ' +
      'or supabase() for auto-detected client/server usage.'
  )
  return getSupabaseServerClient()
}

// Re-export types for convenience
export type { Database } from '../types/database'
