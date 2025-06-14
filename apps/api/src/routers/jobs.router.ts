import { z } from 'zod'
import { router, protectedProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { eq, and, desc, inArray } from 'drizzle-orm'
import { videoJobs } from '../db/schema'

export const jobsRouter = router({
  /**
   * Get a specific job by ID
   */
  getById: protectedProcedure
    .input(
      z.object({
        jobId: z.string().uuid(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const job = await db.query.videoJobs.findFirst({
        where: and(eq(videoJobs.id, input.jobId), eq(videoJobs.userId, user.id)),
        with: {
          video: {
            with: {
              metadata: true,
            },
          },
        },
      })

      if (!job) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Job not found',
        })
      }

      return job
    }),

  /**
   * List user's jobs with optional filtering
   */
  list: protectedProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(20),
        offset: z.number().min(0).default(0),
        status: z.enum(['pending', 'processing', 'completed', 'failed', 'cancelled']).optional(),
        videoId: z.string().uuid().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const where = and(
        eq(videoJobs.userId, user.id),
        input.status ? eq(videoJobs.status, input.status) : undefined,
        input.videoId ? eq(videoJobs.videoId, input.videoId) : undefined
      )

      const [items, totalCount] = await Promise.all([
        db.query.videoJobs.findMany({
          where,
          limit: input.limit,
          offset: input.offset,
          orderBy: [desc(videoJobs.createdAt)],
          with: {
            video: {
              with: {
                metadata: true,
              },
            },
          },
        }),
        db.$count(videoJobs, where),
      ])

      return {
        items,
        totalCount,
        hasMore: input.offset + items.length < totalCount,
      }
    }),

  /**
   * Get job statistics for the user
   */
  stats: protectedProcedure.query(async ({ ctx }) => {
    const { db, user } = ctx

    const jobs = await db.query.videoJobs.findMany({
      where: eq(videoJobs.userId, user.id),
      columns: {
        status: true,
      },
    })

    const stats = {
      total: jobs.length,
      pending: 0,
      processing: 0,
      completed: 0,
      failed: 0,
      cancelled: 0,
    }

    for (const job of jobs) {
      stats[job.status]++
    }

    return stats
  }),

  /**
   * Cancel a job
   */
  cancel: protectedProcedure
    .input(
      z.object({
        jobId: z.string().uuid(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Verify ownership and check if job can be cancelled
      const job = await db.query.videoJobs.findFirst({
        where: and(eq(videoJobs.id, input.jobId), eq(videoJobs.userId, user.id)),
      })

      if (!job) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Job not found',
        })
      }

      if (!['pending', 'processing'].includes(job.status)) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: `Cannot cancel job with status: ${job.status}`,
        })
      }

      // Update job status
      await db
        .update(videoJobs)
        .set({
          status: 'cancelled',
          completedAt: new Date(),
        })
        .where(eq(videoJobs.id, input.jobId))

      return { success: true }
    }),

  /**
   * Retry a failed job
   */
  retry: protectedProcedure
    .input(
      z.object({
        jobId: z.string().uuid(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Verify ownership and check if job can be retried
      const job = await db.query.videoJobs.findFirst({
        where: and(eq(videoJobs.id, input.jobId), eq(videoJobs.userId, user.id)),
      })

      if (!job) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Job not found',
        })
      }

      if (job.status !== 'failed') {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: 'Can only retry failed jobs',
        })
      }

      // Reset job for retry
      await db
        .update(videoJobs)
        .set({
          status: 'pending',
          progress: 0,
          error: null,
          startedAt: null,
          completedAt: null,
        })
        .where(eq(videoJobs.id, input.jobId))

      // Queue for processing
      const { VideoProcessingService } = await import('../services/video-processing')
      const processingService = new VideoProcessingService()
      await processingService.queueJob(input.jobId)

      return { success: true }
    }),

  /**
   * Subscribe to job updates (for real-time updates)
   */
  onUpdate: protectedProcedure
    .input(
      z.object({
        jobId: z.string().uuid(),
      })
    )
    .subscription(async function* ({ ctx, input }) {
      const { db, user } = ctx

      // Verify ownership
      const job = await db.query.videoJobs.findFirst({
        where: and(eq(videoJobs.id, input.jobId), eq(videoJobs.userId, user.id)),
      })

      if (!job) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Job not found',
        })
      }

      // In a real implementation, this would connect to a pub/sub system
      // For now, we'll poll the database
      while (true) {
        const currentJob = await db.query.videoJobs.findFirst({
          where: eq(videoJobs.id, input.jobId),
          with: {
            video: {
              with: {
                metadata: true,
              },
            },
          },
        })

        if (currentJob) {
          yield currentJob

          // Stop if job is complete
          if (['completed', 'failed', 'cancelled'].includes(currentJob.status)) {
            break
          }
        }

        // Wait 2 seconds before next poll
        await new Promise((resolve) => setTimeout(resolve, 2000))
      }
    }),
})
