import { db, videoJobs, videos, videoMetadata, type NewVideoMetadata } from '../db/client'
import { eq } from 'drizzle-orm'
import { AIService } from './ai.service'
import { FFmpegService } from '../lib/utils/ffmpeg'

export class VideoProcessingService {
  private aiService: AIService
  private ffmpegService: FFmpegService

  constructor() {
    this.aiService = new AIService()
    this.ffmpegService = new FFmpegService()
  }

  /**
   * Queue a video processing job
   */
  async queueJob(jobId: string): Promise<void> {
    // In a real implementation, this would queue to a job processor
    // For now, we'll process synchronously (or you could use BullMQ, etc.)
    setImmediate(() => {
      this.processJob(jobId).catch(console.error)
    })
  }

  /**
   * Process a video job
   */
  async processJob(jobId: string): Promise<void> {
    try {
      // Update job status
      await db
        .update(videoJobs)
        .set({
          status: 'processing',
          startedAt: new Date(),
        })
        .where(eq(videoJobs.id, jobId))

      // Get job details
      const job = await db.query.videoJobs.findFirst({
        where: eq(videoJobs.id, jobId),
        with: {
          video: true,
        },
      })

      if (!job || !job.video) {
        throw new Error('Job or video not found')
      }

      const { video } = job
      const config = (job.config as any) || {}

      // Extract video metadata
      const metadata = await this.ffmpegService.extractMetadata(video.fileUrl)

      // Update video duration
      await db.update(videos).set({ duration: metadata.duration }).where(eq(videos.id, video.id))

      let transcriptText = ''
      let subtitlesData = null

      // Generate transcript if requested
      if (config.generateTranscript) {
        await this.updateProgress(jobId, 30)
        const audioUrl = await this.ffmpegService.extractAudio(video.fileUrl)
        transcriptText = await this.aiService.transcribeAudio(audioUrl)
      }

      // Generate subtitles if requested
      if (config.generateSubtitles && transcriptText) {
        await this.updateProgress(jobId, 60)
        subtitlesData = await this.aiService.generateSubtitles(transcriptText)
      }

      // Generate titles and description
      await this.updateProgress(jobId, 80)
      const { titles, description, tags } = await this.aiService.generateVideoMetadata(
        transcriptText || 'No transcript available',
        video.fileName
      )

      // Generate thumbnail from video
      const thumbnailUrl = await this.ffmpegService.generateThumbnail(video.fileUrl)

      // Generate AI thumbnail backgrounds
      await this.updateProgress(jobId, 90)
      const aiThumbnails = await this.aiService.generateThumbnailBackgrounds(
        titles[0] || '', // Use the first title
        description,
        tags,
        4 // Generate 4 different thumbnail options
      )

      // Save metadata
      await db.insert(videoMetadata).values({
        videoId: video.id,
        title: titles[0], // Use first title as main title
        description,
        transcript: transcriptText,
        subtitles: subtitlesData,
        tags,
        thumbnail: thumbnailUrl,
        generatedTitles: titles, // Save all 10 titles
        thumbnailUrls: aiThumbnails, // AI-generated thumbnail backgrounds
        metadata: {
          duration: metadata.duration,
          width: metadata.width,
          height: metadata.height,
          fps: metadata.fps,
          codec: metadata.codec,
        },
      } satisfies NewVideoMetadata)

      // Update video status
      await db.update(videos).set({ status: 'published' }).where(eq(videos.id, video.id))

      // Mark job as completed
      await db
        .update(videoJobs)
        .set({
          status: 'completed',
          progress: 100,
          completedAt: new Date(),
          result: {
            transcript: !!transcriptText,
            subtitles: !!subtitlesData,
            metadata: true,
            thumbnail: true,
          },
        })
        .where(eq(videoJobs.id, jobId))
    } catch (error) {
      console.error('Video processing error:', error)

      // Mark job as failed
      await db
        .update(videoJobs)
        .set({
          status: 'failed',
          error: error instanceof Error ? error.message : 'Unknown error',
          completedAt: new Date(),
        })
        .where(eq(videoJobs.id, jobId))

      // Update video status
      const job = await db.query.videoJobs.findFirst({
        where: eq(videoJobs.id, jobId),
      })

      if (job?.videoId) {
        await db.update(videos).set({ status: 'failed' }).where(eq(videos.id, job.videoId))
      }
    }
  }

  /**
   * Update job progress
   */
  private async updateProgress(jobId: string, progress: number): Promise<void> {
    await db.update(videoJobs).set({ progress }).where(eq(videoJobs.id, jobId))
  }

  /**
   * Cancel a job
   */
  async cancelJob(jobId: string): Promise<void> {
    await db
      .update(videoJobs)
      .set({
        status: 'cancelled',
        completedAt: new Date(),
      })
      .where(eq(videoJobs.id, jobId))
  }
}
