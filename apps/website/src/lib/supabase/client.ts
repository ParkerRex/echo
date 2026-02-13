import { createBrowserClient } from '@supabase/ssr'
import type { Database } from '@echo/supabase/types/database'

// Browser client for client-side operations
export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
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
    }
  )
}