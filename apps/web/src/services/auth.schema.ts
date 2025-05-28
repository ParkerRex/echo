import { z } from "zod"

/**
 * User metadata schema for profile updates
 */
export const UserMetaSchema = z.object({
  username: z.string().min(3).max(20).optional(),
  full_name: z.string().min(1).max(100).optional(),
  avatar_url: z.string().url().optional(),
})

export type UserMeta = z.infer<typeof UserMetaSchema>

/**
 * Complete user object schema
 */
export const UserSchema = z.object({
  id: z.string(),
  email: z.string().email().optional(),
  meta: z.object({
    username: z.string(),
    full_name: z.string().optional(),
    avatar_url: z.string().optional(),
  }),
})

export type User = z.infer<typeof UserSchema>

/**
 * Authentication state union type
 * Represents the current authentication status
 */
export type AuthState =
  | {
      isAuthenticated: false
    }
  | {
      isAuthenticated: true
      user: User
    }

/**
 * OAuth provider types
 */
export type OAuthProvider = 'google' | 'github' | 'discord'

/**
 * Authentication error types
 */
export const AuthErrorSchema = z.object({
  message: z.string(),
  code: z.string().optional(),
  timestamp: z.string().optional(),
})

export type AuthError = z.infer<typeof AuthErrorSchema>
