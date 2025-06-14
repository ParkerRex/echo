import { createClient } from '@supabase/supabase-js'
import { importJWK, jwtVerify } from 'jose'
import type { User } from '../../context'
import { getEnv } from '../../types/env'

const env = getEnv()

// Create Supabase client
export const supabase = createClient(
  env.SUPABASE_URL,
  env.SUPABASE_SERVICE_KEY || env.SUPABASE_ANON_KEY
)

// Cache for the JWT secret
let jwtSecret: Uint8Array | null = null

/**
 * Get the JWT secret as Uint8Array
 */
async function getJwtSecret(): Promise<Uint8Array> {
  if (!jwtSecret) {
    const secret = env.SUPABASE_JWT_SECRET
    if (!secret) {
      throw new Error('SUPABASE_JWT_SECRET is not set')
    }
    jwtSecret = new TextEncoder().encode(secret)
  }
  return jwtSecret
}

/**
 * Validate a JWT token and return the user
 */
export async function validateJWT(token: string): Promise<User | null> {
  try {
    const secret = await getJwtSecret()

    // Verify the JWT
    const { payload } = await jwtVerify(token, secret, {
      issuer: env.SUPABASE_URL,
      audience: 'authenticated',
    })

    // Extract user info from payload
    const userId = payload.sub
    const email = payload.email as string | undefined

    if (!userId || !email) {
      return null
    }

    return {
      id: userId,
      email,
    }
  } catch (error) {
    console.error('JWT validation error:', error)
    return null
  }
}

/**
 * Get user by ID (using service key)
 */
export async function getUserById(userId: string): Promise<User | null> {
  try {
    const { data, error } = await supabase.auth.admin.getUserById(userId)

    if (error || !data.user) {
      return null
    }

    return {
      id: data.user.id,
      email: data.user.email || '',
    }
  } catch (error) {
    console.error('Error fetching user:', error)
    return null
  }
}

/**
 * Create a new user (for testing or admin purposes)
 */
export async function createUser(email: string, password: string): Promise<User | null> {
  try {
    const { data, error } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
    })

    if (error || !data.user) {
      throw error || new Error('Failed to create user')
    }

    return {
      id: data.user.id,
      email: data.user.email || email,
    }
  } catch (error) {
    console.error('Error creating user:', error)
    return null
  }
}
