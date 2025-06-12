import { z } from 'zod'
import { router, protectedProcedure } from '../trpc'
import { eq, and, desc, sql, inArray, or, like, gte, lte } from 'drizzle-orm'
import { videos, videoJobs, videoMetadata, NewVideo, NewVideoJob } from '../db/schema'
import { VideoProcessingService } from '../services/video-processing'
import { StorageService } from '../services/storage.service'
import { 
  NotFoundError, 
  ValidationError, 
  PayloadTooLargeError,
  handleAsync 
} from '../lib/errors'
import {
  commonSchemas,
  fileSchemas,
  videoConfigSchema,
  batchSchemas,
  filterSchemas,
  paginatedResponse,
  sanitizeFileName,
} from '../lib/validation'
import { rateLimiters } from '../middleware/rateLimit'

const videoProcessingService = new VideoProcessingService()
const storageService = new StorageService()

export const improvedVideoRouter = router({
  /**
   * Upload a video file with enhanced validation and chunking support
   */
  upload: protectedProcedure
    .use(rateLimiters.write)
    .input(
      fileSchemas.videoUpload.extend({
        base64Data: z.string().optional(), // For small files
        chunkIndex: z.number().optional(), // For chunked uploads
        totalChunks: z.number().optional(),
        uploadId: z.string().optional(), // For resumable uploads
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx
      
      // Sanitize file name
      const sanitizedFileName = sanitizeFileName(input.fileName)
      
      // Handle chunked uploads
      if (input.chunkIndex !== undefined && input.totalChunks !== undefined) {
        // Store chunk and return progress
        // Implementation depends on your storage backend
        return {
          uploadId: input.uploadId || crypto.randomUUID(),
          chunkIndex: input.chunkIndex,
          totalChunks: input.totalChunks,
          progress: ((input.chunkIndex + 1) / input.totalChunks) * 100,
        }
      }
      
      // Validate file size
      if (input.fileSize > 5 * 1024 * 1024 * 1024) {
        throw new PayloadTooLargeError('Video file size exceeds 5GB limit')
      }
      
      // Upload file to storage
      const [fileUrl, uploadError] = await handleAsync(
        storageService.uploadFile({
          fileName: sanitizedFileName,
          data: input.base64Data ? Buffer.from(input.base64Data, 'base64') : Buffer.alloc(0),
          mimeType: input.mimeType,
          userId: user.id,
        })
      )
      
      if (uploadError) {
        throw new ValidationError('Failed to upload file', uploadError)
      }
      
      // Create video record with transaction
      const result = await db.transaction(async (tx) => {
        const [video] = await tx.insert(videos).values({
          userId: user.id,
          fileName: sanitizedFileName,
          fileUrl: fileUrl!,
          fileSize: input.fileSize,
          mimeType: input.mimeType,
          status: 'draft',
        } satisfies NewVideo).returning()
        
        const [job] = await tx.insert(videoJobs).values({
          videoId: video.id,
          userId: user.id,
          status: 'pending',
          config: {
            generateTranscript: true,
            generateSubtitles: true,
            extractMetadata: true,
            generateThumbnail: true,
          },
        } satisfies NewVideoJob).returning()
        
        return { video, job }
      })
      
      // Queue processing job
      await videoProcessingService.queueJob(result.job.id)
      
      return {
        video: result.video,
        jobId: result.job.id,
      }
    }),

  /**
   * Get video by ID with related data
   */
  getById: protectedProcedure
    .use(rateLimiters.read)
    .input(
      z.object({
        videoId: commonSchemas.uuid,
        includeMetadata: z.boolean().default(true),
        includeJobs: z.boolean().default(true),
        includeTranscript: z.boolean().default(false),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx
      
      const video = await db.query.videos.findFirst({
        where: and(
          eq(videos.id, input.videoId),
          eq(videos.userId, user.id)
        ),
        with: {
          metadata: input.includeMetadata,
          jobs: input.includeJobs ? {
            orderBy: [desc(videoJobs.createdAt)],
            limit: 5,
          } : false,
        },
      })
      
      if (!video) {
        throw new NotFoundError('Video', input.videoId)
      }
      
      // Optionally exclude transcript from metadata if not requested
      if (video.metadata && !input.includeTranscript) {
        video.metadata.transcript = null
      }
      
      return video
    }),

  /**
   * List videos with advanced filtering and search
   */
  list: protectedProcedure
    .use(rateLimiters.read)
    .input(
      commonSchemas.pagination
        .merge(commonSchemas.sorting)
        .merge(filterSchemas.videoFilter)
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx
      
      // Build where conditions
      const conditions = [eq(videos.userId, user.id)]
      
      if (input.status) {
        conditions.push(eq(videos.status, input.status))
      }
      
      if (input.mimeType) {
        conditions.push(eq(videos.mimeType, input.mimeType))
      }
      
      if (input.minDuration) {
        conditions.push(gte(videos.duration, input.minDuration))
      }
      
      if (input.maxDuration) {
        conditions.push(lte(videos.duration, input.maxDuration))
      }
      
      if (input.search) {
        // Search in file name and metadata
        conditions.push(
          or(
            like(videos.fileName, `%${input.search}%`),
            // Add metadata search if your DB supports it
          )
        )
      }
      
      const where = and(...conditions)
      
      // Execute queries in parallel
      const [items, totalCount] = await Promise.all([
        db.query.videos.findMany({
          where,
          limit: input.limit,
          offset: input.offset,
          orderBy: input.sortBy === 'createdAt' 
            ? [input.sortOrder === 'asc' ? videos.createdAt : desc(videos.createdAt)]
            : [desc(videos.createdAt)],
          with: {
            metadata: {
              columns: {
                id: true,
                title: true,
                description: true,
                tags: true,
                thumbnail: true,
              },
            },
            jobs: {
              orderBy: [desc(videoJobs.createdAt)],
              limit: 1,
              columns: {
                id: true,
                status: true,
                progress: true,
              },
            },
          },
        }),
        db.$count(videos, where),
      ])
      
      return {
        items,
        totalCount,
        hasMore: input.offset + items.length < totalCount,
        nextOffset: input.offset + items.length < totalCount 
          ? input.offset + items.length 
          : undefined,
      }
    }),

  /**
   * Batch operations on videos
   */
  batch: protectedProcedure
    .use(rateLimiters.write)
    .input(batchSchemas.batchOperation)
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx
      
      // Verify ownership of all videos
      const userVideos = await db.query.videos.findMany({
        where: and(
          inArray(videos.id, input.ids),
          eq(videos.userId, user.id)
        ),
        columns: { id: true, fileUrl: true },
      })
      
      if (userVideos.length !== input.ids.length) {
        throw new ValidationError('Some videos not found or not owned by user')
      }
      
      switch (input.operation) {
        case 'delete': {
          // Delete files from storage in parallel
          await Promise.all(
            userVideos.map(video => 
              storageService.deleteFile(video.fileUrl).catch(console.error)
            )
          )
          
          // Delete from database
          await db.delete(videos).where(
            and(
              inArray(videos.id, input.ids),
              eq(videos.userId, user.id)
            )
          )
          
          return { success: true, affected: userVideos.length }
        }
        
        case 'publish': {
          await db.update(videos)
            .set({ status: 'published', updatedAt: new Date() })
            .where(
              and(
                inArray(videos.id, input.ids),
                eq(videos.userId, user.id)
              )
            )
          
          return { success: true, affected: userVideos.length }
        }
        
        case 'unpublish': {
          await db.update(videos)
            .set({ status: 'draft', updatedAt: new Date() })
            .where(
              and(
                inArray(videos.id, input.ids),
                eq(videos.userId, user.id)
              )
            )
          
          return { success: true, affected: userVideos.length }
        }
        
        case 'reprocess': {
          // Create new processing jobs
          const jobs = await db.insert(videoJobs).values(
            input.ids.map(videoId => ({
              videoId,
              userId: user.id,
              status: 'pending' as const,
              config: {
                generateTranscript: true,
                generateSubtitles: true,
                extractMetadata: true,
                generateThumbnail: true,
              },
            }))
          ).returning()
          
          // Queue all jobs
          await Promise.all(
            jobs.map(job => videoProcessingService.queueJob(job.id))
          )
          
          return { success: true, affected: jobs.length }
        }
        
        default:
          throw new ValidationError('Invalid batch operation')
      }
    }),

  /**
   * Update video metadata
   */
  updateMetadata: protectedProcedure
    .use(rateLimiters.write)
    .input(
      z.object({
        videoId: commonSchemas.uuid,
        title: z.string().min(1).max(255).optional(),
        description: z.string().max(5000).optional(),
        tags: z.array(z.string()).max(20).optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx
      const { videoId, ...metadata } = input
      
      // Verify ownership
      const video = await db.query.videos.findFirst({
        where: and(
          eq(videos.id, videoId),
          eq(videos.userId, user.id)
        ),
      })
      
      if (!video) {
        throw new NotFoundError('Video', videoId)
      }
      
      // Update or create metadata
      const existingMetadata = await db.query.videoMetadata.findFirst({
        where: eq(videoMetadata.videoId, videoId),
      })
      
      if (existingMetadata) {
        await db.update(videoMetadata)
          .set({ ...metadata, updatedAt: new Date() })
          .where(eq(videoMetadata.id, existingMetadata.id))
      } else {
        await db.insert(videoMetadata).values({
          videoId,
          ...metadata,
        })
      }
      
      return { success: true }
    }),

  /**
   * Get video analytics
   */
  analytics: protectedProcedure
    .use(rateLimiters.read)
    .input(
      z.object({
        videoId: commonSchemas.uuid.optional(),
        dateRange: commonSchemas.dateRange.optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx
      
      // This is a placeholder - implement based on your analytics needs
      const stats = await db
        .select({
          totalVideos: sql<number>`count(*)`,
          totalSize: sql<number>`sum(${videos.fileSize})`,
          totalDuration: sql<number>`sum(${videos.duration})`,
          statusCounts: sql<Record<string, number>>`
            json_object_agg(${videos.status}, count(*))
          `,
        })
        .from(videos)
        .where(eq(videos.userId, user.id))
      
      return {
        overview: stats[0],
        // Add more analytics as needed
      }
    }),

  /**
   * Generate shareable link
   */
  createShareLink: protectedProcedure
    .use(rateLimiters.write)
    .input(
      z.object({
        videoId: commonSchemas.uuid,
        expiresIn: z.number().min(3600).max(604800).default(86400), // 1 hour to 1 week
        password: z.string().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx
      
      // Verify ownership
      const video = await db.query.videos.findFirst({
        where: and(
          eq(videos.id, input.videoId),
          eq(videos.userId, user.id)
        ),
      })
      
      if (!video) {
        throw new NotFoundError('Video', input.videoId)
      }
      
      // Generate share token
      const shareToken = crypto.randomUUID()
      const expiresAt = new Date(Date.now() + input.expiresIn * 1000)
      
      // Store share link info (you'll need a shares table)
      // This is a placeholder - implement based on your needs
      
      return {
        shareUrl: `${process.env.PUBLIC_URL}/share/${shareToken}`,
        expiresAt,
      }
    }),
})