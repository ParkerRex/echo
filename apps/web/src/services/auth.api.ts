import { createMiddleware, createServerFn, json, redirect } from "@tanstack/react-start"
import { getSupabaseServerClient } from "src/lib/supabase"
import type { AuthState, User } from "./auth.schema"
import { UserMetaSchema } from "./auth.schema"

/**
 * Core authentication middleware
 * Extracts user from Supabase session and adds to context
 * This is the single source of truth for authentication state
 */
export const userMiddleware = createMiddleware().server(
  async ({ next }) => {
    const supabase = getSupabaseServerClient()

    try {
      // Get user from Supabase session
      const { data: { user }, error } = await supabase.auth.getUser()

      if (error) {
        console.error("Auth middleware error:", error)
        // Don't throw here - let the user be null and handle downstream
      }

      return next({
        context: {
          user: user || null,
          supabase,
        },
      })
    } catch (error) {
      console.error("Auth middleware unexpected error:", error)
      return next({
        context: {
          user: null,
          supabase,
        },
      })
    }
  },
)

/**
 * Protected route middleware
 * Requires authentication and throws 401 if not authenticated
 * Use this for API endpoints that require authentication
 */
export const userRequiredMiddleware = createMiddleware()
  .middleware([userMiddleware])
  .server(async ({ next, context }) => {
    if (!context.user) {
      throw json(
        {
          message: "Authentication required",
          code: "UNAUTHORIZED",
          timestamp: new Date().toISOString(),
        },
        { status: 401 },
      )
    }

    return next({
      context: {
        user: context.user,
        supabase: context.supabase,
      },
    })
  })

/**
 * Protected page middleware
 * Requires authentication and redirects to login if not authenticated
 * Use this for page routes that require authentication
 */
export const userRequiredPageMiddleware = createMiddleware()
  .middleware([userMiddleware])
  .server(async ({ next, context, request }) => {
    if (!context.user) {
      const url = new URL(request.url)
      const redirectTo = encodeURIComponent(url.pathname + url.search)

      throw redirect({
        to: "/login",
        search: { redirect: redirectTo },
      })
    }

    return next({
      context: {
        user: context.user,
        supabase: context.supabase,
      },
    })
  })

/**
 * Server function to get current user authentication state
 * This is the primary way to check auth status from components
 */
export const getUser = createServerFn()
  .middleware([userMiddleware])
  .handler<AuthState>(async ({ context: { user } }) => {
    if (!user) {
      return { isAuthenticated: false }
    }

    return {
      isAuthenticated: true,
      user: {
        id: user.id,
        email: user.email || undefined,
        meta: {
          username: user.user_metadata?.username || user.email?.split('@')[0] || 'User',
          full_name: user.user_metadata?.full_name,
          avatar_url: user.user_metadata?.avatar_url,
        },
      },
    }
  })

/**
 * Server function to sign out user
 * Clears Supabase session and cookies
 */
export const signOut = createServerFn({ method: 'POST' })
  .middleware([userMiddleware])
  .handler(async ({ context: { supabase } }) => {
    try {
      const { error } = await supabase.auth.signOut()

      if (error) {
        console.error("Sign out error:", error)
        throw json(
          {
            message: "Failed to sign out",
            error: error.message,
          },
          { status: 500 }
        )
      }

      // Successful sign out - redirect will be handled by the client
      return { success: true }
    } catch (error) {
      console.error("Unexpected sign out error:", error)
      throw json(
        {
          message: "An unexpected error occurred during sign out",
        },
        { status: 500 }
      )
    }
  })

/**
 * Server function to initiate Google OAuth sign in
 * Returns the OAuth URL for redirection
 */
export const signInWithGoogle = createServerFn({ method: 'POST' })
  .handler(async () => {
    console.log('🚀 signInWithGoogle server function called')

    const supabase = getSupabaseServerClient()

    // Use server-side environment variables (not VITE_ prefixed)
    const baseUrl = process.env.NODE_ENV === 'production'
      ? 'https://echomycontent.com'
      : 'http://localhost:3000'
    console.log('🔧 Base URL for redirect:', baseUrl)
    console.log('🔧 Supabase URL:', process.env.SUPABASE_URL)

    try {
      const redirectTo = `${baseUrl}/auth/callback`
      console.log('🔗 Full redirect URL:', redirectTo)

      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      })

      console.log('📊 Supabase OAuth response:', { data: !!data, error: !!error })

      if (error) {
        console.error("❌ Google OAuth initiation error:", error)
        throw json(
          {
            message: "Failed to initiate Google sign in",
            error: error.message,
          },
          { status: 500 }
        )
      }

      if (!data.url) {
        console.error("❌ No OAuth URL returned from Supabase")
        throw json(
          {
            message: "No OAuth URL returned from Supabase",
          },
          { status: 500 }
        )
      }

      console.log('✅ OAuth URL generated successfully:', data.url.substring(0, 100) + '...')

      return {
        success: true,
        url: data.url,
      }
    } catch (error) {
      console.error("❌ Unexpected Google OAuth error:", error)
      throw json(
        {
          message: "An unexpected error occurred during Google sign in",
        },
        { status: 500 }
      )
    }
  })

/**
 * Server function to refresh user session
 * Useful for checking if session is still valid
 */
export const refreshSession = createServerFn()
  .middleware([userMiddleware])
  .handler(async ({ context: { supabase } }) => {
    try {
      const { data, error } = await supabase.auth.refreshSession()

      if (error) {
        console.error("Session refresh error:", error)
        return { success: false, error: error.message }
      }

      return {
        success: true,
        session: data.session ? {
          access_token: data.session.access_token,
          expires_at: data.session.expires_at,
        } : null,
      }
    } catch (error) {
      console.error("Unexpected session refresh error:", error)
      return { success: false, error: "Unexpected error during session refresh" }
    }
  })

/**
 * Server function to update user metadata
 * Updates user profile information in Supabase
 */
export const updateUser = createServerFn({ method: 'POST' })
  .middleware([userRequiredMiddleware])
  .validator(UserMetaSchema)
  .handler(async ({ data, context: { supabase } }) => {
    try {
      const { error } = await supabase.auth.updateUser({
        data: {
          username: data.username,
          full_name: data.full_name,
          avatar_url: data.avatar_url,
        },
      })

      if (error) {
        console.error("User update error:", error)
        throw json(
          {
            message: "Failed to update user profile",
            error: error.message,
          },
          { status: 500 }
        )
      }

      return { success: true }
    } catch (error) {
      console.error("Unexpected user update error:", error)
      throw json(
        {
          message: "An unexpected error occurred while updating profile",
        },
        { status: 500 }
      )
    }
  })
