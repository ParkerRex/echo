import { createBrowserClient, createServerClient } from "@supabase/ssr"
import type { Database } from "../types/database"

/**
 * Universal Supabase client factory
 * Creates appropriate client based on context (browser vs server)
 */
export function createSupabaseClient(
  context: 'browser' | 'server' = 'browser'
) {
  const url = typeof window !== 'undefined' 
    ? (import.meta as any).env?.VITE_SUPABASE_URL || process.env.SUPABASE_URL!
    : process.env.SUPABASE_URL!
  
  const anonKey = typeof window !== 'undefined'
    ? (import.meta as any).env?.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY!
    : process.env.SUPABASE_ANON_KEY!

  if (context === 'browser') {
    return createBrowserClient<Database>(url, anonKey)
  }

  // Server context - simplified server client for basic operations
  return createServerClient<Database>(url, anonKey, {
    cookies: {
      get: () => null,
      set: () => {},
      remove: () => {},
    }
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
 * Default browser client instance
 * Convenience export for common use cases
 */
export const supabase = createSupabaseClient('browser')

/**
 * Server client with cookie handling for TanStack Start
 * Use this when you need proper cookie handling in server functions
 */
export const getSupabase = (cookies: any) =>
  createServerClient<Database>(
    typeof window !== 'undefined' 
      ? (import.meta as any).env?.VITE_SUPABASE_URL || process.env.SUPABASE_URL!
      : process.env.SUPABASE_URL!,
    typeof window !== 'undefined'
      ? (import.meta as any).env?.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY!
      : process.env.SUPABASE_ANON_KEY!,
    { 
      cookies: {
        get: (name: string) => cookies.get(name),
        set: (name: string, value: string, options: any) => cookies.set(name, value, options),
        remove: (name: string, options: any) => cookies.delete(name, options),
      }
    }
  )

/**
 * Legacy compatibility - server client without cookie handling
 * @deprecated Use supabaseServer() instead
 */
export const getSupabaseServerClient = () => createSupabaseClient('server')

// Re-export types for convenience
export type { Database } from "../types/database" 