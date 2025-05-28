import { createBrowserClient, createServerClient } from "@supabase/ssr"
import { parseCookies, setCookie } from '@tanstack/react-start/server'
import type { Database } from "../types/database"

/**
 * TanStack Start compatible Supabase server client
 * Uses parseCookies and setCookie from @tanstack/react-start/server
 */
export function getSupabaseServerClient() {
  return createServerClient<Database>(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!,
    {
      cookies: {
        // @ts-ignore Wait till Supabase overload works
        getAll() {
          return Object.entries(parseCookies()).map(([name, value]) => ({
            name,
            value,
          }))
        },
        setAll(cookies) {
          cookies.forEach((cookie) => {
            setCookie(cookie.name, cookie.value)
          })
        },
      },
    },
  )
}

/**
 * Universal Supabase client factory
 * Creates appropriate client based on context (browser vs server)
 */
export function createSupabaseClient(
  context: 'browser' | 'server' = 'browser'
) {
  // Use different environment variables for browser vs server
  // Browser: VITE_ prefixed variables (available in client-side code)
  // Server: process.env variables (available in server-side code)
  let url: string
  let anonKey: string

  if (context === 'browser') {
    // Client-side: use VITE_ prefixed environment variables
    url = import.meta.env?.VITE_SUPABASE_URL || process.env.VITE_SUPABASE_URL!
    anonKey = import.meta.env?.VITE_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY!
  } else {
    // Server-side: use process.env variables
    url = process.env.SUPABASE_URL!
    anonKey = process.env.SUPABASE_ANON_KEY!
  }

  // Debug logging
  if (!url || !anonKey) {
    console.error('Supabase environment variables missing:', {
      url: url ? 'present' : 'missing',
      anonKey: anonKey ? 'present' : 'missing',
      context,
      availableEnv: context === 'browser' ? import.meta.env : process.env
    })
    throw new Error('Supabase URL and ANON_KEY are required')
  }

  if (context === 'browser') {
    return createBrowserClient<Database>(url, anonKey)
  }

  // Server context - use the TanStack Start compatible client
  return getSupabaseServerClient()
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
 * Default browser client instance
 * Convenience export for common use cases
 * Lazy initialization to avoid SSR issues
 */
export const supabase = () => createSupabaseClient('browser')

/**
 * Server client with cookie handling for TanStack Start
 * Use this when you need proper cookie handling in server functions
 * @deprecated Use getSupabaseServerClient() instead for TanStack Start compatibility
 */
export const getSupabase = (cookies: any) =>
  createServerClient<Database>(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!,
    {
      cookies: {
        get: (name: string) => cookies.get(name),
        set: (name: string, value: string, options: any) => cookies.set(name, value, options),
        remove: (name: string, options: any) => cookies.delete(name, options),
      }
    }
  )

// Re-export types for convenience
export type { Database } from "../types/database"