import { createClient, SupabaseClient } from '@supabase/supabase-js';

// These variables are expected to be set in the environment of the consuming application (apps/web)
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    // In a shared package, throwing an error might be too aggressive during build.
    // Consider logging a warning or having a more robust config strategy if used in multiple apps with different envs.
    // For now, we assume apps/web will provide these.
    console.warn("Supabase URL or Anon Key is missing for shared client. Ensure .env is set up in the apps/web project.");
}

// Initialize with a check to prevent errors if env vars are missing during certain build/import scenarios
export const supabase: SupabaseClient = createClient(
    supabaseUrl || "", // Provide a fallback or handle more gracefully
    supabaseAnonKey || "" // Provide a fallback or handle more gracefully
);

// It's crucial that the consuming app (apps/web) ensures these ENV VARS are correctly populated.
