import { router } from '../trpc'
import { videoRouter } from './video.router'
import { improvedVideoRouter } from './video.router.improved'
import { jobsRouter } from './jobs.router'
import { chatRouter } from './chat.router'
import { userRouter } from './user.router'
import { authRouter } from './auth.router'
import { analyticsRouter } from './analytics.router'
import { webhookRouter } from './webhook.router'
import { ideasRouter } from './ideas.router'
import { contentRouter } from './content.router'
import { youtubeRouter } from './youtube.router'
import { contentStrategyRouter } from './content-strategy.router'

/**
 * This is the primary router for your server.
 *
 * All routers added in /routers should be manually added here.
 */
export const appRouter = router({
  auth: authRouter,
  user: userRouter,
  video: improvedVideoRouter, // Using improved video router
  jobs: jobsRouter,
  chat: chatRouter,
  analytics: analyticsRouter,
  webhook: webhookRouter,
  youtube: youtubeRouter,
  contentStrategy: contentStrategyRouter,
  // MVP routers
  ideas: ideasRouter,
  content: contentRouter,
  // Legacy router available for backward compatibility
  legacyVideo: videoRouter,
})

// Export type definition of API
export type AppRouter = typeof appRouter
