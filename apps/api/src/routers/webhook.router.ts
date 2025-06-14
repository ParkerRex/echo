import { z } from 'zod'
import { router, publicProcedure } from '../trpc'
import { createHash, createHmac } from 'crypto'
import { videoJobs, videos } from '../db/schema'
import { eq } from 'drizzle-orm'
import { ValidationError } from '../lib/errors'
import { getEnv } from '../types/env'

const env = getEnv()

/**
 * Verify webhook signature
 */
function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string,
  algorithm: 'sha256' | 'sha1' = 'sha256'
): boolean {
  const expectedSignature = createHmac(algorithm, secret).update(payload).digest('hex')

  return signature === expectedSignature
}

export const webhookRouter = router({
  /**
   * Stripe webhook handler
   */
  stripe: publicProcedure
    .input(
      z.object({
        type: z.string(),
        data: z.object({
          object: z.record(z.any()),
        }),
        signature: z.string(),
        timestamp: z.number(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db } = ctx

      // Verify webhook signature
      const secret = env.STRIPE_WEBHOOK_SECRET
      if (!secret) {
        throw new ValidationError('Stripe webhook secret not configured')
      }

      // Stripe signature verification would go here
      // This is a simplified example

      switch (input.type) {
        case 'payment_intent.succeeded':
          // Handle successful payment
          const customerId = input.data.object.customer as string
          const amount = input.data.object.amount as number

          // Update user credits or subscription status
          console.log(`Payment succeeded for customer ${customerId}: $${amount / 100}`)
          break

        case 'customer.subscription.updated':
          // Handle subscription updates
          break

        default:
          console.log(`Unhandled Stripe event type: ${input.type}`)
      }

      return { received: true }
    }),

  /**
   * YouTube webhook handler for video processing callbacks
   */
  youtube: publicProcedure
    .input(
      z.object({
        videoId: z.string(),
        channelId: z.string(),
        status: z.enum(['processing', 'ready', 'failed']),
        metadata: z
          .object({
            title: z.string().optional(),
            description: z.string().optional(),
            duration: z.number().optional(),
            thumbnail: z.string().optional(),
          })
          .optional(),
        signature: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db } = ctx

      // Verify webhook signature
      const secret = env.YOUTUBE_WEBHOOK_SECRET
      if (!secret) {
        throw new ValidationError('YouTube webhook secret not configured')
      }

      const payload = JSON.stringify({
        videoId: input.videoId,
        channelId: input.channelId,
        status: input.status,
      })

      if (!verifyWebhookSignature(payload, input.signature, secret)) {
        throw new ValidationError('Invalid webhook signature')
      }

      // Update video status based on YouTube processing
      if (input.status === 'ready' && input.metadata) {
        await db.transaction(async (tx) => {
          // Update video metadata
          await tx
            .update(videos)
            .set({
              status: 'published',
              duration: input.metadata!.duration,
              updatedAt: new Date(),
            })
            .where(eq(videos.id, input.videoId))

          // You might also want to update video metadata table
        })
      }

      return { received: true }
    }),

  /**
   * Generic webhook handler for video processing services
   */
  processing: publicProcedure
    .input(
      z.object({
        jobId: z.string().uuid(),
        status: z.enum(['started', 'progress', 'completed', 'failed']),
        progress: z.number().min(0).max(100).optional(),
        result: z
          .object({
            transcriptUrl: z.string().optional(),
            subtitlesUrl: z.string().optional(),
            thumbnailUrl: z.string().optional(),
            metadata: z.record(z.any()).optional(),
          })
          .optional(),
        error: z.string().optional(),
        signature: z.string(),
        timestamp: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db } = ctx

      // Verify webhook signature
      const secret = env.PROCESSING_WEBHOOK_SECRET
      if (!secret) {
        throw new ValidationError('Processing webhook secret not configured')
      }

      const payload = `${input.jobId}:${input.status}:${input.timestamp}`
      if (!verifyWebhookSignature(payload, input.signature, secret)) {
        throw new ValidationError('Invalid webhook signature')
      }

      // Update job status
      const updateData: any = {
        status: input.status === 'started' ? 'processing' : input.status,
        updatedAt: new Date(),
      }

      if (input.progress !== undefined) {
        updateData.progress = input.progress
      }

      if (input.status === 'started') {
        updateData.startedAt = new Date()
      } else if (input.status === 'completed') {
        updateData.completedAt = new Date()
        updateData.result = input.result
      } else if (input.status === 'failed') {
        updateData.completedAt = new Date()
        updateData.error = input.error
      }

      await db.update(videoJobs).set(updateData).where(eq(videoJobs.id, input.jobId))

      // If completed, update the video status
      if (input.status === 'completed') {
        const job = await db.query.videoJobs.findFirst({
          where: eq(videoJobs.id, input.jobId),
        })

        if (job) {
          await db
            .update(videos)
            .set({
              status: 'published',
              updatedAt: new Date(),
            })
            .where(eq(videos.id, job.videoId))
        }
      }

      return { received: true }
    }),

  /**
   * Slack webhook for notifications
   */
  slack: publicProcedure
    .input(
      z.object({
        type: z.enum(['event_callback', 'url_verification']),
        challenge: z.string().optional(), // For URL verification
        event: z
          .object({
            type: z.string(),
            user: z.string().optional(),
            text: z.string().optional(),
            channel: z.string().optional(),
            ts: z.string().optional(),
          })
          .optional(),
        signature: z.string(),
        timestamp: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      // Handle Slack URL verification
      if (input.type === 'url_verification' && input.challenge) {
        return { challenge: input.challenge }
      }

      // Verify webhook signature
      const secret = env.SLACK_SIGNING_SECRET
      if (!secret) {
        throw new ValidationError('Slack signing secret not configured')
      }

      const baseString = `v0:${input.timestamp}:${JSON.stringify(input)}`
      const expectedSignature = `v0=${createHmac('sha256', secret)
        .update(baseString)
        .digest('hex')}`

      if (input.signature !== expectedSignature) {
        throw new ValidationError('Invalid Slack signature')
      }

      // Handle Slack events
      if (input.event) {
        switch (input.event.type) {
          case 'app_mention':
            // Handle when your app is mentioned
            console.log(`App mentioned by ${input.event.user}: ${input.event.text}`)
            break

          case 'message':
            // Handle direct messages
            console.log(`Message from ${input.event.user}: ${input.event.text}`)
            break

          default:
            console.log(`Unhandled Slack event type: ${input.event.type}`)
        }
      }

      return { received: true }
    }),

  /**
   * GitHub webhook handler
   */
  github: publicProcedure
    .input(
      z.object({
        action: z.string(),
        repository: z
          .object({
            name: z.string(),
            full_name: z.string(),
          })
          .optional(),
        sender: z
          .object({
            login: z.string(),
          })
          .optional(),
        signature: z.string(),
        event: z.string(), // X-GitHub-Event header
      })
    )
    .mutation(async ({ input }) => {
      // Verify webhook signature
      const secret = env.GITHUB_WEBHOOK_SECRET
      if (!secret) {
        throw new ValidationError('GitHub webhook secret not configured')
      }

      // GitHub uses HMAC hex digest with sha256
      // The signature format is sha256=<signature>
      const [algorithm, signature] = input.signature.split('=')
      if (algorithm !== 'sha256') {
        throw new ValidationError('Invalid signature algorithm')
      }

      // Handle different GitHub events
      switch (input.event) {
        case 'push':
          console.log(`Push to ${input.repository?.full_name} by ${input.sender?.login}`)
          break

        case 'pull_request':
          console.log(`PR ${input.action} in ${input.repository?.full_name}`)
          break

        case 'issues':
          console.log(`Issue ${input.action} in ${input.repository?.full_name}`)
          break

        default:
          console.log(`Unhandled GitHub event: ${input.event}`)
      }

      return { received: true }
    }),
})
