import { createServerClient } from "@supabase/ssr";
import type { Cookies } from "@tanstack/react-start";
import type { Database } from "../types/generated";

export const getSupabase = (cookies: Cookies) =>
  createServerClient<Database>(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!,
    { cookies }
  );
