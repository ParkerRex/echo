import { z } from "zod"

export const UserMetaSchema = z.object({
  username: z.string().min(3).max(20),
})

export type UserMeta = z.infer<typeof UserMetaSchema>

// Legacy password-based schemas removed
// Google OAuth is now the primary authentication method

export type AuthState =
  | {
      isAuthenticated: false
    }
  | {
      isAuthenticated: true
      user: User
    }

export type User = { email?: string; meta: UserMeta }
