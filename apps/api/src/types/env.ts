export interface Env {
  // Server Configuration
  NODE_ENV: 'development' | 'production' | 'test'
  PORT: string
  HOST: string

  // Database Configuration
  DATABASE_URL: string
  DATABASE_POOL_SIZE: string

  // Supabase Configuration
  SUPABASE_URL: string
  SUPABASE_ANON_KEY: string
  SUPABASE_SERVICE_KEY: string
  SUPABASE_JWT_SECRET: string

  // Storage Configuration
  STORAGE_BUCKET: string
  STORAGE_PUBLIC_URL: string

  // AI Service Configuration
  GEMINI_API_KEY: string
  ANTHROPIC_API_KEY?: string
  OPENAI_API_KEY?: string

  // Redis Configuration (optional)
  REDIS_URL?: string

  // Logging
  LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error'

  // CORS Configuration
  CORS_ORIGINS: string

  // Worker/Queue Configuration
  ENABLE_BACKGROUND_JOBS: string
  JOB_CONCURRENCY: string

  // Feature Flags
  ENABLE_CHAT_STREAMING: string
  ENABLE_VIDEO_PROCESSING: string

  // Webhook Secrets (optional)
  STRIPE_WEBHOOK_SECRET?: string
  YOUTUBE_WEBHOOK_SECRET?: string
  PROCESSING_WEBHOOK_SECRET?: string
  SLACK_SIGNING_SECRET?: string
  GITHUB_WEBHOOK_SECRET?: string

  // External Service URLs
  PUBLIC_URL?: string

  // Google OAuth (for YouTube)
  GOOGLE_CLIENT_ID?: string
  GOOGLE_CLIENT_SECRET?: string
}

// Type-safe environment variable access
export function getEnv(): Env {
  return process.env as unknown as Env
}

// Validate required environment variables
export function validateEnv(): void {
  const required = ['DATABASE_URL', 'SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_JWT_SECRET']

  const missing = required.filter((key) => !process.env[key])

  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`)
  }
}
