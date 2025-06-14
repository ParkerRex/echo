import { z } from 'zod'
import { router, protectedProcedure } from '../trpc'
import { eq, and, desc, sql, gte, lte, between } from 'drizzle-orm'
import { videos, videoJobs, videoMetadata, chats, chatMessages } from '../db/schema'
import { commonSchemas } from '../lib/validation'
import { rateLimiters } from '../middleware/rateLimit'

export const analyticsRouter = router({
  /**
   * Get overview statistics
   */
  overview: protectedProcedure.use(rateLimiters.read).query(async ({ ctx }) => {
    const { db, user } = ctx

    const [videoStats, jobStats, storageStats] = await Promise.all([
      // Video statistics
      db
        .select({
          total: sql<number>`count(*)`,
          published: sql<number>`count(*) filter (where ${videos.status} = 'published')`,
          draft: sql<number>`count(*) filter (where ${videos.status} = 'draft')`,
          processing: sql<number>`count(*) filter (where ${videos.status} = 'processing')`,
          failed: sql<number>`count(*) filter (where ${videos.status} = 'failed')`,
        })
        .from(videos)
        .where(eq(videos.userId, user.id)),

      // Job statistics
      db
        .select({
          total: sql<number>`count(*)`,
          pending: sql<number>`count(*) filter (where ${videoJobs.status} = 'pending')`,
          processing: sql<number>`count(*) filter (where ${videoJobs.status} = 'processing')`,
          completed: sql<number>`count(*) filter (where ${videoJobs.status} = 'completed')`,
          failed: sql<number>`count(*) filter (where ${videoJobs.status} = 'failed')`,
          avgProcessingTime: sql<number>`
              avg(extract(epoch from (${videoJobs.completedAt} - ${videoJobs.startedAt})))
              filter (where ${videoJobs.status} = 'completed')
            `,
        })
        .from(videoJobs)
        .where(eq(videoJobs.userId, user.id)),

      // Storage statistics
      db
        .select({
          totalSize: sql<number>`coalesce(sum(${videos.fileSize}), 0)`,
          totalDuration: sql<number>`coalesce(sum(${videos.duration}), 0)`,
          avgFileSize: sql<number>`coalesce(avg(${videos.fileSize}), 0)`,
          avgDuration: sql<number>`coalesce(avg(${videos.duration}), 0)`,
        })
        .from(videos)
        .where(eq(videos.userId, user.id)),
    ])

    return {
      videos: videoStats[0],
      jobs: jobStats[0],
      storage: storageStats[0],
    }
  }),

  /**
   * Get time series data for charts
   */
  timeSeries: protectedProcedure
    .use(rateLimiters.read)
    .input(
      z.object({
        metric: z.enum(['uploads', 'processing', 'storage', 'duration']),
        period: z.enum(['hour', 'day', 'week', 'month']),
        startDate: z.date().optional(),
        endDate: z.date().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const endDate = input.endDate || new Date()
      const startDate =
        input.startDate ||
        new Date(endDate.getTime() - (input.period === 'hour' ? 24 : 30) * 24 * 60 * 60 * 1000)

      // Date truncation based on period
      const dateTrunc = {
        hour: sql`date_trunc('hour', ${videos.uploadedAt})`,
        day: sql`date_trunc('day', ${videos.uploadedAt})`,
        week: sql`date_trunc('week', ${videos.uploadedAt})`,
        month: sql`date_trunc('month', ${videos.uploadedAt})`,
      }[input.period]

      // Metric aggregation
      const metricAgg = {
        uploads: sql<number>`count(*)`,
        processing: sql<number>`avg(extract(epoch from (${videoJobs.completedAt} - ${videoJobs.startedAt})))`,
        storage: sql<number>`sum(${videos.fileSize})`,
        duration: sql<number>`sum(${videos.duration})`,
      }[input.metric]

      const data = await db
        .select({
          date: dateTrunc.as('date'),
          value: metricAgg.as('value'),
        })
        .from(videos)
        .leftJoin(videoJobs, eq(videos.id, videoJobs.videoId))
        .where(and(eq(videos.userId, user.id), between(videos.uploadedAt, startDate, endDate)))
        .groupBy(sql`date`)
        .orderBy(sql`date`)

      return {
        metric: input.metric,
        period: input.period,
        data,
      }
    }),

  /**
   * Get video performance metrics
   */
  videoPerformance: protectedProcedure
    .use(rateLimiters.read)
    .input(
      z.object({
        videoId: commonSchemas.uuid,
        includeHourly: z.boolean().default(false),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Verify ownership
      const video = await db.query.videos.findFirst({
        where: and(eq(videos.id, input.videoId), eq(videos.userId, user.id)),
        with: {
          metadata: true,
          jobs: {
            orderBy: [desc(videoJobs.createdAt)],
          },
        },
      })

      if (!video) {
        throw new Error('Video not found')
      }

      // Get chat interactions if any
      const chatStats = await db
        .select({
          totalChats: sql<number>`count(distinct ${chats.id})`,
          totalMessages: sql<number>`count(${chatMessages.id})`,
          avgMessagesPerChat: sql<number>`
            avg(message_count) from (
              select count(*) as message_count 
              from ${chatMessages} 
              group by ${chatMessages.chatId}
            ) as chat_counts
          `,
        })
        .from(chats)
        .leftJoin(chatMessages, eq(chats.id, chatMessages.chatId))
        .where(and(eq(chats.userId, user.id), eq(chats.videoId, input.videoId)))

      return {
        video: {
          id: video.id,
          fileName: video.fileName,
          status: video.status,
          uploadedAt: video.uploadedAt,
          duration: video.duration,
          fileSize: video.fileSize,
        },
        processing: {
          jobCount: video.jobs.length,
          lastProcessed: video.jobs[0]?.completedAt,
          avgProcessingTime:
            video.jobs
              .filter((j) => j.completedAt && j.startedAt)
              .reduce((acc, job) => {
                const duration = job.completedAt!.getTime() - job.startedAt!.getTime()
                return acc + duration
              }, 0) / (video.jobs.filter((j) => j.completedAt).length || 1),
        },
        engagement: chatStats[0],
        metadata: video.metadata,
      }
    }),

  /**
   * Get content insights
   */
  contentInsights: protectedProcedure.use(rateLimiters.read).query(async ({ ctx }) => {
    const { db, user } = ctx

    const [formatDistribution, durationDistribution, tagFrequency, processingSuccess] =
      await Promise.all([
        // Format distribution
        db
          .select({
            format: videos.mimeType,
            count: sql<number>`count(*)`,
            totalSize: sql<number>`sum(${videos.fileSize})`,
          })
          .from(videos)
          .where(eq(videos.userId, user.id))
          .groupBy(videos.mimeType),

        // Duration distribution
        db
          .select({
            range: sql<string>`
              case 
                when ${videos.duration} < 60 then '< 1min'
                when ${videos.duration} < 300 then '1-5min'
                when ${videos.duration} < 600 then '5-10min'
                when ${videos.duration} < 1800 then '10-30min'
                else '> 30min'
              end
            `,
            count: sql<number>`count(*)`,
          })
          .from(videos)
          .where(and(eq(videos.userId, user.id), sql`${videos.duration} is not null`))
          .groupBy(sql`range`)
          .orderBy(sql`range`),

        // Tag frequency
        db
          .select({
            tag: sql<string>`unnest(${videoMetadata.tags})`,
            count: sql<number>`count(*)`,
          })
          .from(videoMetadata)
          .innerJoin(videos, eq(videoMetadata.videoId, videos.id))
          .where(and(eq(videos.userId, user.id), sql`${videoMetadata.tags} is not null`))
          .groupBy(sql`tag`)
          .orderBy(desc(sql`count`))
          .limit(20),

        // Processing success rate
        db
          .select({
            total: sql<number>`count(*)`,
            successful: sql<number>`
              count(*) filter (where ${videoJobs.status} = 'completed')
            `,
            failed: sql<number>`
              count(*) filter (where ${videoJobs.status} = 'failed')
            `,
            avgRetries: sql<number>`
              avg(retry_count) from (
                select ${videoJobs.videoId}, count(*) - 1 as retry_count
                from ${videoJobs}
                group by ${videoJobs.videoId}
              ) as retries
            `,
          })
          .from(videoJobs)
          .where(eq(videoJobs.userId, user.id)),
      ])

    return {
      formats: formatDistribution,
      durations: durationDistribution,
      topTags: tagFrequency,
      processingStats: processingSuccess[0],
    }
  }),

  /**
   * Get usage trends
   */
  usageTrends: protectedProcedure
    .use(rateLimiters.read)
    .input(
      z.object({
        days: z.number().min(7).max(90).default(30),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const startDate = new Date()
      startDate.setDate(startDate.getDate() - input.days)

      const dailyUsage = await db
        .select({
          date: sql`date_trunc('day', ${videos.uploadedAt})`.as('date'),
          uploads: sql<number>`count(*)`,
          totalSize: sql<number>`sum(${videos.fileSize})`,
          totalDuration: sql<number>`sum(${videos.duration})`,
          uniqueFormats: sql<number>`count(distinct ${videos.mimeType})`,
        })
        .from(videos)
        .where(and(eq(videos.userId, user.id), gte(videos.uploadedAt, startDate)))
        .groupBy(sql`date`)
        .orderBy(sql`date`)

      // Calculate growth metrics
      const growth =
        dailyUsage.length >= 2
          ? {
              uploads:
                ((dailyUsage[dailyUsage.length - 1]!.uploads - dailyUsage[0]!.uploads) /
                  dailyUsage[0]!.uploads) *
                100,
              storage:
                ((dailyUsage[dailyUsage.length - 1]!.totalSize - dailyUsage[0]!.totalSize) /
                  dailyUsage[0]!.totalSize) *
                100,
            }
          : { uploads: 0, storage: 0 }

      return {
        period: input.days,
        daily: dailyUsage,
        growth,
        summary: {
          totalUploads: dailyUsage.reduce((sum, day) => sum + day.uploads, 0),
          totalStorage: dailyUsage.reduce((sum, day) => sum + day.totalSize, 0),
          avgUploadsPerDay:
            dailyUsage.reduce((sum, day) => sum + day.uploads, 0) / dailyUsage.length,
        },
      }
    }),
})
