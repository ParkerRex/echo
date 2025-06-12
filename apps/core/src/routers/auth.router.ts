import { z } from 'zod'
import { router, publicProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { supabase } from '../lib/auth/supabase'

export const authRouter = router({
  /**
   * Sign up with email and password
   */
  signUp: publicProcedure
    .input(z.object({
      email: z.string().email(),
      password: z.string().min(8),
    }))
    .mutation(async ({ input }) => {
      const { email, password } = input
      
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      })
      
      if (error) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: error.message,
        })
      }
      
      return {
        user: data.user,
        session: data.session,
      }
    }),

  /**
   * Sign in with email and password
   */
  signIn: publicProcedure
    .input(z.object({
      email: z.string().email(),
      password: z.string(),
    }))
    .mutation(async ({ input }) => {
      const { email, password } = input
      
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      
      if (error) {
        throw new TRPCError({
          code: 'UNAUTHORIZED',
          message: error.message,
        })
      }
      
      return {
        user: data.user,
        session: data.session,
      }
    }),

  /**
   * Sign in with OAuth provider
   */
  signInWithProvider: publicProcedure
    .input(z.object({
      provider: z.enum(['google', 'github', 'discord']),
      redirectTo: z.string().url().optional(),
    }))
    .mutation(async ({ input }) => {
      const { provider, redirectTo } = input
      
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo,
        },
      })
      
      if (error) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: error.message,
        })
      }
      
      return {
        url: data.url,
      }
    }),

  /**
   * Sign out
   */
  signOut: publicProcedure
    .mutation(async () => {
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: error.message,
        })
      }
      
      return { success: true }
    }),

  /**
   * Request password reset
   */
  resetPassword: publicProcedure
    .input(z.object({
      email: z.string().email(),
      redirectTo: z.string().url().optional(),
    }))
    .mutation(async ({ input }) => {
      const { email, redirectTo } = input
      
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo,
      })
      
      if (error) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: error.message,
        })
      }
      
      return { success: true }
    }),

  /**
   * Update password
   */
  updatePassword: publicProcedure
    .input(z.object({
      newPassword: z.string().min(8),
    }))
    .mutation(async ({ input }) => {
      const { newPassword } = input
      
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      })
      
      if (error) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: error.message,
        })
      }
      
      return { success: true }
    }),

  /**
   * Verify email with OTP
   */
  verifyOTP: publicProcedure
    .input(z.object({
      email: z.string().email(),
      token: z.string(),
      type: z.enum(['signup', 'recovery', 'invite']),
    }))
    .mutation(async ({ input }) => {
      const { email, token, type } = input
      
      const { data, error } = await supabase.auth.verifyOtp({
        email,
        token,
        type,
      })
      
      if (error) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: error.message,
        })
      }
      
      return {
        user: data.user,
        session: data.session,
      }
    }),

  /**
   * Refresh session
   */
  refreshSession: publicProcedure
    .input(z.object({
      refreshToken: z.string(),
    }))
    .mutation(async ({ input }) => {
      const { refreshToken } = input
      
      const { data, error } = await supabase.auth.refreshSession({
        refresh_token: refreshToken,
      })
      
      if (error) {
        throw new TRPCError({
          code: 'UNAUTHORIZED',
          message: error.message,
        })
      }
      
      return {
        user: data.user,
        session: data.session,
      }
    }),

  /**
   * Get session from JWT
   */
  getSession: publicProcedure
    .input(z.object({
      accessToken: z.string(),
    }))
    .query(async ({ input }) => {
      const { accessToken } = input
      
      const { data, error } = await supabase.auth.getUser(accessToken)
      
      if (error) {
        throw new TRPCError({
          code: 'UNAUTHORIZED',
          message: error.message,
        })
      }
      
      return {
        user: data.user,
      }
    }),
})