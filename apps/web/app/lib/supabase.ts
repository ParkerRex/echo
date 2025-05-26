import { createBrowserClient, createServerClient } from "@supabase/ssr"
import type { Database } from "@echo/db/types/db"

// Browser client for client-side operations
export const supabase = createBrowserClient<Database>(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
)

// Server client for server functions (simplified version)
export const getSupabaseServerClient = () =>
  createServerClient<Database>(
    process.env.SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get: () => null,
        set: () => {},
        remove: () => {},
      }
    }
  )

// Re-export for convenience
export { getSupabase, getSupabaseServerClient as getSupabaseSSR } from "@echo/db/clients/ssr" 