import { z } from 'zod'
import { router, protectedProcedure } from '../trpc'
import { TRPCError } from '@trpc/server'
import { AIService } from '../services/ai.service'
import { TrendAnalysisService } from '../services/trend-analysis.service'
import { KeywordResearchService } from '../services/keyword-research.service'
import { YouTubeAnalyticsService } from '../services/youtube-analytics.service'
import { eq } from 'drizzle-orm'
import { videos, videoMetadata, contentVariants, abTestExperiments } from '../db/schema'

const aiService = new AIService()
const trendAnalysisService = new TrendAnalysisService()
const keywordResearchService = new KeywordResearchService()
const youtubeAnalyticsService = new YouTubeAnalyticsService()

export const contentStrategyRouter = router({
  /**
   * Get trending topics for content inspiration
   */
  getTrendingTopics: protectedProcedure
    .input(
      z.object({
        region: z.string().default('US'),
        category: z.string().optional(),
        niche: z.string().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { user } = ctx

      try {
        if (input.niche) {
          // Get personalized trends based on user's niche
          return await trendAnalysisService.getPersonalizedTrends(user.id)
        } else {
          // Get general trending topics
          return await trendAnalysisService.fetchYouTubeTrends(input.region, input.category)
        }
      } catch (error) {
        console.error('Error fetching trending topics:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to fetch trending topics',
        })
      }
    }),

  /**
   * Analyze user's content niche
   */
  analyzeUserNiche: protectedProcedure.mutation(async ({ ctx }) => {
    const { user } = ctx

    try {
      return await trendAnalysisService.analyzeUserNiche(user.id)
    } catch (error) {
      console.error('Error analyzing user niche:', error)
      throw new TRPCError({
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Failed to analyze user niche',
      })
    }
  }),

  /**
   * Generate content ideas based on trending topics
   */
  generateContentIdeas: protectedProcedure
    .input(
      z.object({
        topics: z.array(z.string()),
        niche: z.string().optional(),
        count: z.number().min(1).max(20).default(10),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { user } = ctx

      try {
        const userNiche = input.niche || 'general'
        return await aiService.generateContentIdeas(input.topics, userNiche, input.count)
      } catch (error) {
        console.error('Error generating content ideas:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to generate content ideas',
        })
      }
    }),

  /**
   * Get keyword suggestions for SEO optimization
   */
  getKeywordSuggestions: protectedProcedure
    .input(
      z.object({
        topic: z.string(),
        niche: z.string().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      try {
        return await keywordResearchService.getKeywordSuggestions(input.topic, input.niche)
      } catch (error) {
        console.error('Error getting keyword suggestions:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to get keyword suggestions',
        })
      }
    }),

  /**
   * Optimize video title for SEO
   */
  optimizeTitle: protectedProcedure
    .input(
      z.object({
        title: z.string(),
        niche: z.string(),
        targetKeywords: z.array(z.string()).default([]),
      })
    )
    .mutation(async ({ input }) => {
      try {
        return await keywordResearchService.optimizeTitle(
          input.title,
          input.niche,
          input.targetKeywords
        )
      } catch (error) {
        console.error('Error optimizing title:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to optimize title',
        })
      }
    }),

  /**
   * Generate SEO-optimized content
   */
  generateSEOContent: protectedProcedure
    .input(
      z.object({
        transcript: z.string(),
        title: z.string(),
        keywords: z.array(z.string()),
        niche: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        return await keywordResearchService.generateSEODescription(
          input.transcript,
          input.title,
          input.keywords,
          input.niche
        )
      } catch (error) {
        console.error('Error generating SEO content:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to generate SEO content',
        })
      }
    }),

  /**
   * Generate content variants for A/B testing
   */
  generateContentVariants: protectedProcedure
    .input(
      z.object({
        content: z.string(),
        type: z.enum(['title', 'thumbnail', 'description', 'tags']),
        count: z.number().min(1).max(10).default(5),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { user } = ctx

      try {
        return await aiService.generateContentVariants(
          input.content,
          input.type,
          user.id,
          input.count
        )
      } catch (error) {
        console.error('Error generating content variants:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to generate content variants',
        })
      }
    }),

  /**
   * Predict video performance
   */
  predictPerformance: protectedProcedure
    .input(
      z.object({
        title: z.string(),
        thumbnail: z.string(),
        description: z.string(),
        niche: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { user } = ctx

      try {
        return await aiService.predictPerformance(
          input.title,
          input.thumbnail,
          input.description,
          input.niche,
          user.id
        )
      } catch (error) {
        console.error('Error predicting performance:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to predict performance',
        })
      }
    }),

  /**
   * Analyze content hooks for retention optimization
   */
  analyzeContentHooks: protectedProcedure
    .input(
      z.object({
        videoId: z.string().uuid(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { db, user } = ctx

      try {
        // Get video metadata
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

        if (!video.metadata?.transcript) {
          throw new TRPCError({
            code: 'BAD_REQUEST',
            message: 'Video transcript not available',
          })
        }

        return await aiService.analyzeContentHooks(video.metadata.transcript)
      } catch (error) {
        console.error('Error analyzing content hooks:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to analyze content hooks',
        })
      }
    }),

  /**
   * Optimize content for specific goals
   */
  optimizeForGoal: protectedProcedure
    .input(
      z.object({
        title: z.string(),
        description: z.string(),
        tags: z.array(z.string()),
        goal: z.enum(['views', 'engagement', 'retention', 'subscribers']),
        niche: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        return await aiService.optimizeForGoal(
          {
            title: input.title,
            description: input.description,
            tags: input.tags,
          },
          input.goal,
          input.niche
        )
      } catch (error) {
        console.error('Error optimizing for goal:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to optimize content',
        })
      }
    }),

  /**
   * Analyze keyword competition
   */
  analyzeKeywordCompetition: protectedProcedure
    .input(
      z.object({
        keyword: z.string(),
      })
    )
    .query(async ({ input }) => {
      try {
        return await keywordResearchService.analyzeKeywordCompetition(input.keyword)
      } catch (error) {
        console.error('Error analyzing keyword competition:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to analyze keyword competition',
        })
      }
    }),

  /**
   * Get personalized keyword suggestions
   */
  getPersonalizedKeywords: protectedProcedure
    .input(
      z.object({
        topic: z.string(),
      })
    )
    .query(async ({ ctx, input }) => {
      const { user } = ctx

      try {
        return await keywordResearchService.getPersonalizedKeywords(user.id, input.topic)
      } catch (error) {
        console.error('Error getting personalized keywords:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to get personalized keywords',
        })
      }
    }),

  /**
   * Suggest optimal tags for content
   */
  suggestOptimalTags: protectedProcedure
    .input(
      z.object({
        content: z.string(),
        niche: z.string(),
        maxTags: z.number().min(5).max(20).default(15),
      })
    )
    .mutation(async ({ input }) => {
      try {
        return await keywordResearchService.suggestOptimalTags(
          input.content,
          input.niche,
          input.maxTags
        )
      } catch (error) {
        console.error('Error suggesting optimal tags:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to suggest optimal tags',
        })
      }
    }),

  /**
   * Analyze competitors for insights
   */
  analyzeCompetitors: protectedProcedure
    .input(
      z.object({
        channelIds: z.array(z.string()).max(10),
      })
    )
    .mutation(async ({ input }) => {
      try {
        return await trendAnalysisService.analyzeCompetitors(input.channelIds)
      } catch (error) {
        console.error('Error analyzing competitors:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to analyze competitors',
        })
      }
    }),

  /**
   * Get trending keywords in a niche
   */
  getTrendingKeywords: protectedProcedure
    .input(
      z.object({
        niche: z.string(),
      })
    )
    .query(async ({ input }) => {
      try {
        return await trendAnalysisService.getTrendingKeywords(input.niche)
      } catch (error) {
        console.error('Error getting trending keywords:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to get trending keywords',
        })
      }
    }),

  /**
   * Get channel analytics overview
   */
  getChannelAnalytics: protectedProcedure.query(async ({ ctx }) => {
    const { user } = ctx

    try {
      return await youtubeAnalyticsService.getChannelAnalytics(user.id)
    } catch (error) {
      console.error('Error getting channel analytics:', error)
      throw new TRPCError({
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Failed to get channel analytics',
      })
    }
  }),

  /**
   * Sync YouTube analytics for all user videos
   */
  syncAnalytics: protectedProcedure.mutation(async ({ ctx }) => {
    const { user } = ctx

    try {
      await youtubeAnalyticsService.syncUserAnalytics(user.id)
      return { success: true }
    } catch (error) {
      console.error('Error syncing analytics:', error)
      throw new TRPCError({
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Failed to sync analytics',
      })
    }
  }),

  /**
   * Get performance comparison between videos
   */
  getPerformanceComparison: protectedProcedure
    .input(
      z.object({
        days: z.number().min(1).max(365).default(30),
      })
    )
    .query(async ({ ctx, input }) => {
      const { user } = ctx

      try {
        return await youtubeAnalyticsService.getPerformanceComparison(user.id, String(input.days))
      } catch (error) {
        console.error('Error getting performance comparison:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to get performance comparison',
        })
      }
    }),

  /**
   * Track keyword performance over time
   */
  trackKeywordPerformance: protectedProcedure
    .input(
      z.object({
        keywords: z.array(z.string()).max(20),
      })
    )
    .mutation(async ({ input }) => {
      try {
        return await keywordResearchService.trackKeywordPerformance(input.keywords)
      } catch (error) {
        console.error('Error tracking keyword performance:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to track keyword performance',
        })
      }
    }),

  /**
   * Create A/B test experiment
   */
  createABTest: protectedProcedure
    .input(
      z.object({
        videoId: z.string().uuid(),
        experimentName: z.string(),
        variants: z.array(z.string()), // Array of variant IDs
        trafficSplit: z.record(z.number()), // Percentage split
        successMetric: z.enum(['ctr', 'retention', 'engagement', 'views']),
        targetSampleSize: z.number().default(1000),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { db, user } = ctx

      try {
        // Verify video ownership
        const video = await db.query.videos.findFirst({
          where: eq(videos.id, input.videoId),
        })

        if (!video || video.userId !== user.id) {
          throw new TRPCError({
            code: 'NOT_FOUND',
            message: 'Video not found',
          })
        }

        // Create A/B test experiment
        const experiment = await db.insert(abTestExperiments).values({
          userId: user.id,
          videoId: input.videoId,
          experimentName: input.experimentName,
          variants: input.variants,
          trafficSplit: input.trafficSplit,
          successMetric: input.successMetric,
          targetSampleSize: input.targetSampleSize,
        }).returning()

        return experiment[0]
      } catch (error) {
        console.error('Error creating A/B test:', error)
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to create A/B test',
        })
      }
    }),

  /**
   * Get content strategy recommendations
   */
  getContentStrategyRecommendations: protectedProcedure.query(async ({ ctx }) => {
    const { user } = ctx

    try {
      // This combines multiple services to provide comprehensive recommendations
      const [userNiche, trendingTopics, channelAnalytics] = await Promise.allSettled([
        trendAnalysisService.analyzeUserNiche(user.id).catch(() => null),
        trendAnalysisService.getPersonalizedTrends(user.id).catch(() => []),
        youtubeAnalyticsService.getChannelAnalytics(user.id).catch(() => null),
      ])

      const niche = userNiche.status === 'fulfilled' ? userNiche.value : null
      const trends = trendingTopics.status === 'fulfilled' ? trendingTopics.value : []
      const analytics = channelAnalytics.status === 'fulfilled' ? channelAnalytics.value : null

      // Generate content ideas based on trends and niche
      const contentIdeas = niche
        ? await aiService.generateContentIdeas(
            trends.slice(0, 3).map(t => t.topic),
            niche.primaryNiche,
            8
          ).catch(() => [])
        : []

      return {
        userNiche: niche,
        trendingTopics: trends.slice(0, 10),
        contentIdeas,
        channelAnalytics: analytics,
        recommendations: generateStrategicRecommendations(niche, trends, analytics),
      }
    } catch (error) {
      console.error('Error getting content strategy recommendations:', error)
      throw new TRPCError({
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Failed to get content strategy recommendations',
      })
    }
  }),

})

/**
 * Private helper to generate strategic recommendations
 */
function generateStrategicRecommendations(userNiche: any, trends: any[], analytics: any) {
    const recommendations = []

    if (!userNiche) {
      recommendations.push({
        type: 'niche',
        priority: 'high',
        title: 'Define Your Content Niche',
        description: 'Upload more content to help us analyze your niche and provide personalized recommendations.',
        action: 'Upload 3-5 more videos to get niche analysis',
      })
    }

    if (trends.length > 0) {
      recommendations.push({
        type: 'trending',
        priority: 'medium',
        title: 'Capitalize on Trending Topics',
        description: `${trends.length} trending topics match your content style.`,
        action: `Create content around: ${trends.slice(0, 3).map(t => t.topic).join(', ')}`,
      })
    }

    if (analytics && analytics.totalViews < 10000) {
      recommendations.push({
        type: 'growth',
        priority: 'high',
        title: 'Focus on SEO and Discoverability',
        description: 'Optimize your titles and descriptions for better search visibility.',
        action: 'Use our SEO optimization tools for your next 5 videos',
      })
    }

    if (analytics && analytics.subscriberCount < 1000) {
      recommendations.push({
        type: 'subscribers',
        priority: 'medium',
        title: 'Build Your Subscriber Base',
        description: 'Create series content and consistent posting schedule.',
        action: 'Plan a 5-part series in your niche',
      })
    }

    return recommendations
}