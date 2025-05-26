import { createServerClient } from "@supabase/ssr";
import type { Database } from "../types/db";

// For TanStack Start compatibility
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
  );

// Legacy compatibility - sync version for server functions
export const getSupabaseServerClient = () =>
  createServerClient<Database>(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!,
    {
      cookies: {
        get: () => null,
        set: () => {},
        remove: () => {},
      }
    }
  );
