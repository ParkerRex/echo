import type { FetchCreateContextFnOptions } from '@trpc/server/adapters/fetch'
import type { Context as HonoContext } from 'hono'
import { db } from './db/client'
import { validateJWT } from './lib/auth/supabase'
import type { Env } from './types/env'

export interface User {
  id: string
  email: string
  emailVerified?: boolean
  role?: string
  sessionCreatedAt?: Date
}

export interface Context {
  db: typeof db
  user: User | null
  env: Env
  requestId?: string
  apiKey?: string
  isServiceRequest?: boolean
  req: HonoContext['req']
}

/**
 * Creates context for each request
 */
export async function createContext(
  opts: FetchCreateContextFnOptions,
  c: HonoContext
): Promise<Context> {
  // Get auth header
  const authHeader = c.req.header('Authorization')

  let user: User | null = null

  // Validate JWT if present
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7)
    try {
      user = await validateJWT(token)
    } catch (error) {
      // Invalid token, but we don't throw here
      // Let the procedures handle authorization
      console.error('JWT validation error:', error)
    }
  }

  return {
    db,
    user,
    env: c.env as Env,
    req: c.req,
  }
}

export type CreateContextOptions = FetchCreateContextFnOptions
