import { createMiddleware, createServerFn, json } from "@tanstack/react-start"
import { getSupabaseServerClient } from "~/lib/supabase"
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

export const signUp = createServerFn({ method: 'POST' })
  .validator(SignUpSchema)
  .handler(async ({ data }) => {
    const { data: userData, error } =
      await getSupabaseServerClient().auth.signUp({
        email: data.email,
        password: data.password,
      })

    if (error) {
      switch (error.code) {
        case "email_exists":
          return { error: "Email already exists" }
        case "weak_password":
          return { error: "Your password is too weak" }
        default:
          return { error: error.message }
      }
    }

    if (userData.user) {
      return { success: true, userId: userData.user.id }
    }

    return { error: "Something went wrong" }
  })

export const signIn = createServerFn({ method: 'POST' })
  .validator(SignInSchema)
  .handler(async ({ data }) => {
    const { error } = await getSupabaseServerClient().auth.signInWithPassword({
      email: data.email,
      password: data.password,
    })

    if (error) {
      return { error: error.message }
    }
  })

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
