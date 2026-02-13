import { z } from 'zod'
import { router, protectedProcedure, publicProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { YouTubeService } from '../services/youtube.service'
import { eq } from 'drizzle-orm'
import { videos, videoMetadata, youtubeCredentials } from '../db/schema'

const youtubeService = new YouTubeService()

export const youtubeRouter = router({
  /**
   * Get YouTube OAuth URL
   */
  getAuthUrl: protectedProcedure
    .input(
      z.object({
        videoId: z.string().uuid().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { user } = ctx

      const authUrl = youtubeService.getAuthUrl(user.id, input.videoId)

      return { authUrl }
    }),

  /**
   * Handle OAuth callback
   */
  callback: publicProcedure
    .input(
      z.object({
        code: z.string(),
        state: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      const { userId, videoId } = await youtubeService.handleCallback(input.code, input.state)

      return {
        success: true,
        userId,
        videoId,
        redirectUrl: videoId ? `/dashboard?video=${videoId}&youtube=connected` : '/dashboard?youtube=connected',
      }
    }),

  /**
   * Check if YouTube is connected
   */
  isConnected: protectedProcedure.query(async ({ ctx }) => {
    const { user } = ctx

    const isConnected = await youtubeService.isConnected(user.id)

    return { isConnected }
  }),

  /**
   * Get connected YouTube channel info
   */
  getChannelInfo: protectedProcedure.query(async ({ ctx }) => {
    const { db, user } = ctx

    const credentials = await db.query.youtubeCredentials.findFirst({
      where: eq(youtubeCredentials.userId, user.id),
    })

    if (!credentials) {
      return null
    }

    return {
      channelId: credentials.channelId,
      channelName: credentials.channelName,
      connectedAt: credentials.createdAt,
    }
  }),

  /**
   * Publish video to YouTube
   */
  publishVideo: protectedProcedure
    .input(
      z.object({
        videoId: z.string().uuid(),
        title: z.string().optional(),
        description: z.string().optional(),
        tags: z.array(z.string()).optional(),
        categoryId: z.string().optional(),
        privacyStatus: z.enum(['private', 'unlisted', 'public']).optional(),
        thumbnailIndex: z.number().optional(), // Which AI-generated thumbnail to use
        publishAt: z.string().optional(), // ISO date string
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Get video and metadata
      const video = await db.query.videos.findFirst({
        where: eq(videos.id, input.videoId),
        with: {
          metadata: true,
        },
      })

      if (!video || video.userId !== user.id) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Video not found',
        })
      }

      const metadata = video.metadata

      // Use provided values or fall back to generated metadata
      const title = input.title || metadata?.generatedTitles?.[0] || video.fileName
      const description = input.description || metadata?.description || ''
      const tags = input.tags || metadata?.tags || []
      
      // Select thumbnail
      let thumbnailUrl: string | undefined
      if (input.thumbnailIndex !== undefined && metadata?.thumbnailUrls?.[input.thumbnailIndex]) {
        thumbnailUrl = metadata.thumbnailUrls[input.thumbnailIndex]
      } else if (metadata?.thumbnail) {
        thumbnailUrl = metadata.thumbnail
      }

      // Upload to YouTube
      const youtubeVideoId = await youtubeService.uploadVideo({
        videoId: video.id,
        userId: user.id,
        title,
        description,
        tags,
        categoryId: input.categoryId,
        privacyStatus: input.privacyStatus,
        thumbnailUrl,
        publishAt: input.publishAt ? new Date(input.publishAt) : undefined,
      })

      return {
        success: true,
        youtubeVideoId,
        youtubeUrl: `https://youtube.com/watch?v=${youtubeVideoId}`,
      }
    }),

  /**
   * Update published video on YouTube
   */
  updateVideo: protectedProcedure
    .input(
      z.object({
        youtubeVideoId: z.string(),
        title: z.string().optional(),
        description: z.string().optional(),
        tags: z.array(z.string()).optional(),
        categoryId: z.string().optional(),
        privacyStatus: z.enum(['private', 'unlisted', 'public']).optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { user } = ctx

      await youtubeService.updateVideo(input.youtubeVideoId, user.id, {
        title: input.title,
        description: input.description,
        tags: input.tags,
        categoryId: input.categoryId,
        privacyStatus: input.privacyStatus,
      })

      return { success: true }
    }),

  /**
   * Get video analytics from YouTube
   */
  getVideoAnalytics: protectedProcedure
    .input(
      z.object({
        youtubeVideoId: z.string(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { user } = ctx

      const analytics = await youtubeService.getVideoAnalytics(input.youtubeVideoId, user.id)

      return analytics
    }),

  /**
   * Disconnect YouTube account
   */
  disconnect: protectedProcedure.mutation(async ({ ctx }) => {
    const { user } = ctx

    await youtubeService.disconnect(user.id)

    return { success: true }
  }),

  /**
   * List YouTube categories
   */
  getCategories: protectedProcedure.query(async () => {
    // Common YouTube categories
    return [
      { id: '1', name: 'Film & Animation' },
      { id: '2', name: 'Autos & Vehicles' },
      { id: '10', name: 'Music' },
      { id: '15', name: 'Pets & Animals' },
      { id: '17', name: 'Sports' },
      { id: '19', name: 'Travel & Events' },
      { id: '20', name: 'Gaming' },
      { id: '22', name: 'People & Blogs' },
      { id: '23', name: 'Comedy' },
      { id: '24', name: 'Entertainment' },
      { id: '25', name: 'News & Politics' },
      { id: '26', name: 'Howto & Style' },
      { id: '27', name: 'Education' },
      { id: '28', name: 'Science & Technology' },
      { id: '29', name: 'Nonprofits & Activism' },
    ]
  }),
})