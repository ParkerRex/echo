// Re-export everything from the universal client factory
export {
  supabase,
  supabaseBrowser,
  supabaseServer,
  getSupabase,
  getSupabaseServerClient,
  createSupabaseClient,
  type Database
} from "@echo/db/clients"

// Import for legacy alias
import { getSupabaseServerClient } from "@echo/db/clients"

// Legacy aliases for backward compatibility
export const getSupabaseSSR = getSupabaseServerClient 