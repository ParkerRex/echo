import { z } from 'zod'
import { router, protectedProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { eq, and, desc } from 'drizzle-orm'
import { videos, videoJobs, videoMetadata, type NewVideo, type NewVideoJob } from '../db/schema'
import { VideoProcessingService } from '../services/video-processing'
import { StorageService } from '../services/storage.service'

const videoProcessingService = new VideoProcessingService()
const storageService = new StorageService()

export const videoRouter = router({
  /**
   * Get presigned URL for video upload
   */
  getUploadUrl: protectedProcedure
    .input(
      z.object({
        fileName: z.string(),
        fileSize: z.number(),
        mimeType: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { user } = ctx

      // Validate file
      const maxSize = 500 * 1024 * 1024 // 500MB
      if (input.fileSize > maxSize) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: 'File size must be less than 500MB',
        })
      }

      const allowedTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
      if (!allowedTypes.includes(input.mimeType)) {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: 'Invalid file type. Supported formats: MP4, MOV, AVI, MKV, WEBM',
        })
      }

      // Get presigned upload URL
      const uploadUrl = await storageService.getPresignedUploadUrl({
        fileName: input.fileName,
        mimeType: input.mimeType,
        userId: user.id,
      })

      // Generate the file key that will be used
      const fileKey = storageService.generateFileKey(user.id, input.fileName)

      return {
        uploadUrl,
        fileKey,
      }
    }),

  /**
   * Create video record after successful upload
   */
  createVideo: protectedProcedure
    .input(
      z.object({
        fileName: z.string(),
        fileSize: z.number(),
        mimeType: z.string(),
        fileKey: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Get the public URL for the uploaded file
      const fileUrl = storageService.getPublicUrl(input.fileKey)

      // Create video record
      const [video] = await db
        .insert(videos)
        .values({
          userId: user.id,
          fileName: input.fileName,
          fileUrl,
          fileSize: input.fileSize,
          mimeType: input.mimeType,
          status: 'processing',
        } satisfies NewVideo)
        .returning()

      // Create processing job
      const [job] = await db
        .insert(videoJobs)
        .values({
          videoId: video!.id,
          userId: user.id,
          status: 'pending',
          config: {
            generateTranscript: true,
            generateSubtitles: true,
            extractMetadata: true,
          },
        } satisfies NewVideoJob)
        .returning()

      // Queue processing job
      await videoProcessingService.queueJob(job!.id)

      return {
        video: video!,
        jobId: job!.id,
      }
    }),

  /**
   * Get a specific video by ID
   */
  getById: protectedProcedure
    .input(
      z.object({
        videoId: z.string().uuid(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const video = await db.query.videos.findFirst({
        where: and(eq(videos.id, input.videoId), eq(videos.userId, user.id)),
        with: {
          metadata: true,
          jobs: {
            orderBy: [desc(videoJobs.createdAt)],
            limit: 1,
          },
        },
      })

      if (!video) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Video not found',
        })
      }

      return video
    }),

  /**
   * List user's videos
   */
  list: protectedProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(20),
        offset: z.number().min(0).default(0),
        status: z.enum(['draft', 'processing', 'published', 'failed']).optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const where = and(
        eq(videos.userId, user.id),
        input.status ? eq(videos.status, input.status) : undefined
      )

      const [items, totalCount] = await Promise.all([
        db.query.videos.findMany({
          where,
          limit: input.limit,
          offset: input.offset,
          orderBy: [desc(videos.createdAt)],
          with: {
            metadata: true,
            jobs: {
              orderBy: [desc(videoJobs.createdAt)],
              limit: 1,
            },
          },
        }),
        db.$count(videos, where),
      ])

      return {
        items,
        totalCount,
        hasMore: input.offset + items.length < totalCount,
      }
    }),

  /**
   * Delete a video
   */
  delete: protectedProcedure
    .input(
      z.object({
        videoId: z.string().uuid(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      // Verify ownership
      const video = await db.query.videos.findFirst({
        where: and(eq(videos.id, input.videoId), eq(videos.userId, user.id)),
      })

      if (!video) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Video not found',
        })
      }

      // Delete from storage
      await storageService.deleteFile(video.fileUrl)

      // Delete from database (cascades to related tables)
      await db.delete(videos).where(eq(videos.id, input.videoId))

      return { success: true }
    }),

  /**
   * Complete multipart upload
   */
  completeUpload: protectedProcedure
    .input(
      z.object({
        fileKey: z.string(),
        fileName: z.string(),
        fileSize: z.number(),
        mimeType: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      const fileUrl = storageService.getPublicUrl(input.fileKey)

      // Create video record
      const [video] = await db
        .insert(videos)
        .values({
          userId: user.id,
          fileName: input.fileName,
          fileUrl,
          fileSize: input.fileSize,
          mimeType: input.mimeType,
          status: 'draft',
        } satisfies NewVideo)
        .returning()

      // Create processing job
      const [job] = await db
        .insert(videoJobs)
        .values({
          videoId: video!.id,
          userId: user.id,
          status: 'pending',
          config: {
            generateTranscript: true,
            generateSubtitles: true,
            extractMetadata: true,
          },
        } satisfies NewVideoJob)
        .returning()

      // Queue processing job
      await videoProcessingService.queueJob(job!.id)

      return {
        video: video!,
        jobId: job!.id,
      }
    }),

  /**
   * Get job status
   */
  getJobStatus: protectedProcedure
    .input(
      z.object({
        jobId: z.string().uuid(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      const job = await db.query.videoJobs.findFirst({
        where: and(
          eq(videoJobs.id, input.jobId),
          eq(videoJobs.userId, user.id)
        ),
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
})
