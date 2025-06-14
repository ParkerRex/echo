import { z } from 'zod'
import { router, protectedProcedure, publicProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { eq } from 'drizzle-orm'
import { users, videos, chats, videoJobs } from '../db/schema'
import { getUserById } from '../lib/auth/supabase'

export const userRouter = router({
  /**
   * Get current user profile
   */
  me: protectedProcedure.query(async ({ ctx }) => {
    const { user } = ctx

    // Get fresh user data from Supabase
    const userData = await getUserById(user.id)

    if (!userData) {
      throw new TRPCError({
        code: 'NOT_FOUND',
        message: 'User not found',
      })
    }

    return userData
  }),

  /**
   * Get user by ID (public)
   */
  getById: publicProcedure
    .input(
      z.object({
        userId: z.string().uuid(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db } = ctx

      const user = await db.query.users.findFirst({
        where: eq(users.id, input.userId),
      })

      if (!user) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'User not found',
        })
      }

      // Return public user data only
      return {
        id: user.id,
        createdAt: user.createdAt,
      }
    }),

  /**
   * Update user profile
   */
  update: protectedProcedure
    .input(
      z.object({
        email: z.string().email().optional(),
        metadata: z.record(z.any()).optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // In a real app, you'd update via Supabase Auth Admin API
      // For now, we'll just update our local users table
      const [updatedUser] = await db
        .update(users)
        .set({
          email: input.email || user.email,
          updatedAt: new Date(),
        })
        .where(eq(users.id, user.id))
        .returning()

      return updatedUser
    }),

  /**
   * Get user statistics
   */
  stats: protectedProcedure.query(async ({ ctx }) => {
    const { db, user } = ctx

    const [videoStats, chatStats, jobStats] = await Promise.all([
      // Video statistics
      db.query.videos.findMany({
        where: eq(videos.userId, user.id),
        columns: {
          status: true,
        },
      }),

      // Chat statistics
      db.query.chats.findMany({
        where: eq(chats.userId, user.id),
        columns: {
          isActive: true,
        },
      }),

      // Job statistics
      db.query.videoJobs.findMany({
        where: eq(videoJobs.userId, user.id),
        columns: {
          status: true,
        },
      }),
    ])

    // Calculate stats
    const stats = {
      videos: {
        total: videoStats.length,
        draft: videoStats.filter((v) => v.status === 'draft').length,
        processing: videoStats.filter((v) => v.status === 'processing').length,
        published: videoStats.filter((v) => v.status === 'published').length,
        failed: videoStats.filter((v) => v.status === 'failed').length,
      },
      chats: {
        total: chatStats.length,
        active: chatStats.filter((c) => c.isActive).length,
        archived: chatStats.filter((c) => !c.isActive).length,
      },
      jobs: {
        total: jobStats.length,
        pending: jobStats.filter((j) => j.status === 'pending').length,
        processing: jobStats.filter((j) => j.status === 'processing').length,
        completed: jobStats.filter((j) => j.status === 'completed').length,
        failed: jobStats.filter((j) => j.status === 'failed').length,
        cancelled: jobStats.filter((j) => j.status === 'cancelled').length,
      },
    }

    return stats
  }),

  /**
   * Delete user account (soft delete)
   */
  delete: protectedProcedure
    .input(
      z.object({
        confirmation: z.literal('DELETE_MY_ACCOUNT'),
      })
    )
    .mutation(async ({ ctx }) => {
      const { db, user } = ctx

      // In production, this would:
      // 1. Delete from Supabase Auth
      // 2. Delete or anonymize all user data
      // 3. Cancel any active subscriptions

      // For now, we'll just mark as deleted
      await db
        .update(users)
        .set({
          email: `deleted_${user.id}@deleted.com`,
          updatedAt: new Date(),
        })
        .where(eq(users.id, user.id))

      return { success: true }
    }),

  /**
   * Export user data (GDPR compliance)
   */
  exportData: protectedProcedure.query(async ({ ctx }) => {
    const { db, user } = ctx

    // Gather all user data
    const [userData, userVideos, userChats, jobs] = await Promise.all([
      db.query.users.findFirst({
        where: eq(users.id, user.id),
      }),
      db.query.videos.findMany({
        where: eq(videos.userId, user.id),
        with: {
          metadata: true,
        },
      }),
      db.query.chats.findMany({
        where: eq(chats.userId, user.id),
        with: {
          messages: true,
        },
      }),
      db.query.videoJobs.findMany({
        where: eq(videoJobs.userId, user.id),
      }),
    ])

    return {
      user: userData,
      videos: userVideos,
      chats: userChats,
      jobs,
      exportedAt: new Date().toISOString(),
    }
  }),
})
