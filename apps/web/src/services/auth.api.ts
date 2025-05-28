import { createMiddleware, createServerFn, json } from "@tanstack/react-start"
import { getSupabaseServerClient } from "src/lib/supabase"
import {
  type AuthState,
  SignInSchema,
  SignUpSchema,
  UserMetaSchema,
} from "./auth.schema"

export const userMiddleware = createMiddleware().server(
  async ({ next }) => {
    const supabase = getSupabaseServerClient()

    const { data } = await supabase.auth.getUser()

    return next({
      context: {
        user: data.user,
        supabase,
      },
    })
  },
)
export const userRequiredMiddleware = createMiddleware()
  .middleware([userMiddleware])
  .server(async ({ next, context }) => {
    if (!context.user) {
      throw json(
        { message: "You must be logged in to access this resource!" },
        { status: 401 },
      )
    }

    return next({
      context: {
        user: context.user,
      },
    })
  })

// Legacy email/password authentication functions removed
// Google OAuth is now the primary authentication method

export const signOut = createServerFn({ method: 'POST' }).handler(async () => {
  await getSupabaseServerClient().auth.signOut()
})

export const getUser = createServerFn()
  .middleware([userMiddleware])
  .handler<AuthState>(async ({ context: { user } }) => {
    if (!user) {
      return { isAuthenticated: false }
    }

    return {
      isAuthenticated: true,
      user: {
        email: user.email,
        meta: { username: user.user_metadata.username },
      },
    }
  })

export const updateUser = createServerFn({ method: 'POST' })
  .validator(UserMetaSchema)
  .handler(async ({ data }) => {
    const supabase = getSupabaseServerClient()

    const { error } = await supabase.auth.updateUser({
      data: { username: data.username },
    })

    if (error) {
      return { error: error.message }
    }

    return { success: true }
  })
