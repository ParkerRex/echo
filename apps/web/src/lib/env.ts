import { z } from "zod"

/**
 * Environment variable validation schema
 * Ensures all required environment variables are present and valid
 */
const envSchema = z.object({
  // Supabase Configuration
  SUPABASE_URL: z.string().url("SUPABASE_URL must be a valid URL"),
  SUPABASE_ANON_KEY: z.string().min(1, "SUPABASE_ANON_KEY is required"),
  SUPABASE_JWT_SECRET: z.string().min(32, "SUPABASE_JWT_SECRET must be at least 32 characters"),
  
  // API Configuration
  API_URL: z.string().url("API_URL must be a valid URL").optional(),
  
  // Environment
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  ENVIRONMENT: z.enum(["development", "production", "test"]).default("development"),
})

/**
 * Client-side environment variable validation schema
 * Only includes variables that should be available on the client
 */
const clientEnvSchema = z.object({
  VITE_SUPABASE_URL: z.string().url("VITE_SUPABASE_URL must be a valid URL"),
  VITE_SUPABASE_ANON_KEY: z.string().min(1, "VITE_SUPABASE_ANON_KEY is required"),
  VITE_API_URL: z.string().url("VITE_API_URL must be a valid URL").optional(),
  VITE_WS_BASE_URL: z.string().optional(),
})

/**
 * Server-side environment variables
 * Validated on server startup
 */
export function getServerEnv() {
  try {
    return envSchema.parse({
      SUPABASE_URL: process.env.SUPABASE_URL,
      SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY,
      SUPABASE_JWT_SECRET: process.env.SUPABASE_JWT_SECRET,
      API_URL: process.env.API_URL,
      NODE_ENV: process.env.NODE_ENV,
      ENVIRONMENT: process.env.ENVIRONMENT,
    })
  } catch (error) {
    console.error("❌ Invalid server environment variables:", error)
    throw new Error("Server environment validation failed")
  }
}

/**
 * Client-side environment variables
 * Validated when accessed on the client
 */
export function getClientEnv() {
  if (typeof window === "undefined") {
    throw new Error("getClientEnv() can only be called on the client side")
  }

  try {
    return clientEnvSchema.parse({
      VITE_SUPABASE_URL: import.meta.env.VITE_SUPABASE_URL,
      VITE_SUPABASE_ANON_KEY: import.meta.env.VITE_SUPABASE_ANON_KEY,
      VITE_API_URL: import.meta.env.VITE_API_URL,
      VITE_WS_BASE_URL: import.meta.env.VITE_WS_BASE_URL,
    })
  } catch (error) {
    console.error("❌ Invalid client environment variables:", error)
    throw new Error("Client environment validation failed")
  }
}

/**
 * Type definitions for environment variables
 */
export type ServerEnv = z.infer<typeof envSchema>
export type ClientEnv = z.infer<typeof clientEnvSchema>

/**
 * Environment validation status
 */
export function validateEnvironment() {
  const isServer = typeof window === "undefined"
  
  if (isServer) {
    try {
      getServerEnv()
      console.log("✅ Server environment variables validated successfully")
      return true
    } catch (error) {
      console.error("❌ Server environment validation failed:", error)
      return false
    }
  } else {
    try {
      getClientEnv()
      console.log("✅ Client environment variables validated successfully")
      return true
    } catch (error) {
      console.error("❌ Client environment validation failed:", error)
      return false
    }
  }
}
