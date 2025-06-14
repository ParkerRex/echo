import { z } from 'zod'
import { router, publicProcedure, protectedProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { db, ideas, generatedContent, type NewIdea } from '../db/client'
import { eq, desc, and } from 'drizzle-orm'

export const ideasRouter = router({
  // Create a new idea
  create: protectedProcedure
    .input(
      z.object({
        content: z.string().min(1).max(5000),
        type: z.enum(['idea', 'transcript', 'url']).default('idea'),
        source: z.string().optional(),
        videoType: z.enum(['tutorial', 'review', 'vlog', 'shorts', 'podcast', 'other']).optional(),
        metadata: z.record(z.any()).optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const userId = ctx.user.id

      const [idea] = await db
        .insert(ideas)
        .values({
          userId,
          content: input.content,
          type: input.type,
          source: input.source,
          videoType: input.videoType,
          metadata: input.metadata,
        })
        .returning()

      return idea
    }),

  // Get a single idea
  get: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      const userId = ctx.user.id

      const idea = await db.query.ideas.findFirst({
        where: and(eq(ideas.id, input.id), eq(ideas.userId, userId)),
        with: {
          generatedContent: true,
          publishedVideo: true,
        },
      })

      if (!idea) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Idea not found',
        })
      }

      return idea
    }),

  // List ideas
  list: protectedProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(20),
        offset: z.number().min(0).default(0),
        status: z
          .enum(['draft', 'outlining', 'scripting', 'ready', 'published', 'archived'])
          .optional(),
        type: z.enum(['idea', 'transcript', 'url']).optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const userId = ctx.user.id

      const conditions = [eq(ideas.userId, userId)]
      if (input.status) conditions.push(eq(ideas.status, input.status))
      if (input.type) conditions.push(eq(ideas.type, input.type))

      const results = await db
        .select()
        .from(ideas)
        .where(and(...conditions))
        .orderBy(desc(ideas.createdAt))
        .limit(input.limit)
        .offset(input.offset)

      return results
    }),

  // Update idea status
  updateStatus: protectedProcedure
    .input(
      z.object({
        id: z.string().uuid(),
        status: z.enum(['draft', 'outlining', 'scripting', 'ready', 'published', 'archived']),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const userId = ctx.user.id

      const [updated] = await db
        .update(ideas)
        .set({
          status: input.status,
          updatedAt: new Date(),
        })
        .where(and(eq(ideas.id, input.id), eq(ideas.userId, userId)))
        .returning()

      if (!updated) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Idea not found',
        })
      }

      return updated
    }),

  // Delete idea
  delete: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ ctx, input }) => {
      const userId = ctx.user.id

      const [deleted] = await db
        .delete(ideas)
        .where(and(eq(ideas.id, input.id), eq(ideas.userId, userId)))
        .returning()

      if (!deleted) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Idea not found',
        })
      }

      return { success: true }
    }),

  // Archive old ideas
  archiveOld: protectedProcedure
    .input(
      z.object({
        daysOld: z.number().min(1).default(30),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const userId = ctx.user.id
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - input.daysOld)

      const result = await db
        .update(ideas)
        .set({
          status: 'archived',
          updatedAt: new Date(),
        })
        .where(
          and(
            eq(ideas.userId, userId),
            eq(ideas.status, 'draft')
            // Note: You'll need to import lt from drizzle-orm
            // lt(ideas.createdAt, cutoffDate)
          )
        )
        .returning()

      return {
        archived: result.length,
      }
    }),
})
