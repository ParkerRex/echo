import { google } from 'googleapis'
import { GoogleGenerativeAI } from '@google/generative-ai'
import { getEnv } from '../types/env'
import { db } from '../db/client'
import { 
  trendingTopics, 
  userNiches, 
  videos,
  videoMetadata
} from '../db/schema'
import type {
  TrendingTopic, 
  NewTrendingTopic,
  UserNiche,
  NewUserNiche
} from '../db/schema'
import { eq, and, desc, gte, sql } from 'drizzle-orm'

const env = getEnv()

export interface TrendingVideoData {
  videoId: string
  title: string
  channelTitle: string
  viewCount: number
  publishedAt: string
  tags: string[]
  categoryId: string
}

export interface DiscoveredTrend {
  topic: string
  category: string
  trendScore: number
  searchVolume?: number
  relatedKeywords: string[]
  sampleTitles: string[]
  sampleChannels: string[]
  competitionLevel: 'low' | 'medium' | 'high'
}

export interface NicheAnalysis {
  primaryNiche: string
  confidence: number
  keywords: string[]
  contentThemes: string[]
  targetAudience: any
  competitorChannels: string[]
  performanceMetrics: any
}

export class TrendAnalysisService {
  private youtube: any
  private genAI: GoogleGenerativeAI
  private model: any

  constructor() {
    // Note: This requires a YouTube Data API key
    this.youtube = google.youtube({
      version: 'v3',
      auth: (env as any).YOUTUBE_API_KEY || env.GOOGLE_CLIENT_ID, // Fallback to OAuth key
    })
    
    this.genAI = new GoogleGenerativeAI(env.GEMINI_API_KEY)
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' })
  }

  /**
   * Fetch and analyze current YouTube trending topics
   */
  async fetchYouTubeTrends(region: string = 'US', categoryId?: string): Promise<DiscoveredTrend[]> {
    try {
      // Get trending videos from YouTube
      const trendingResponse = await this.youtube.videos.list({
        part: ['snippet', 'statistics'],
        chart: 'mostPopular',
        regionCode: region,
        categoryId: categoryId,
        maxResults: 50,
      })

      const trendingVideos: TrendingVideoData[] = trendingResponse.data.items?.map((item: any) => ({
        videoId: item.id,
        title: item.snippet.title,
        channelTitle: item.snippet.channelTitle,
        viewCount: parseInt(item.statistics.viewCount || '0'),
        publishedAt: item.snippet.publishedAt,
        tags: item.snippet.tags || [],
        categoryId: item.snippet.categoryId,
      })) || []

      // Analyze trending patterns with AI
      const trends = await this.analyzeTrendingPatterns(trendingVideos, region)

      // Store trends in database
      await this.storeTrendingTopics(trends)

      return trends
    } catch (error) {
      console.error('Error fetching YouTube trends:', error)
      throw new Error('Failed to fetch trending topics')
    }
  }

  /**
   * Analyze user's content to determine their niche
   */
  async analyzeUserNiche(userId: string): Promise<NicheAnalysis> {
    // Get user's videos and metadata
    const userVideos = await db.query.videos.findMany({
      where: eq(videos.userId, userId),
      with: {
        metadata: true,
      },
      orderBy: desc(videos.createdAt),
      limit: 20, // Analyze last 20 videos
    })

    if (userVideos.length === 0) {
      throw new Error('No videos found for niche analysis')
    }

    // Extract content for analysis
    const contentData = userVideos.map(video => ({
      title: video.fileName,
      description: video.metadata?.description || '',
      tags: video.metadata?.tags || [],
      generatedTitles: video.metadata?.generatedTitles || [],
    }))

    // Use AI to analyze content patterns
    const analysis = await this.performNicheAnalysis(contentData)

    // Store user niche data
    await this.storeUserNiche(userId, analysis)

    return analysis
  }

  /**
   * Get personalized trending topics for a user based on their niche
   */
  async getPersonalizedTrends(userId: string): Promise<TrendingTopic[]> {
    // Get user's niche data
    const userNiche = await db.query.userNiches.findFirst({
      where: eq(userNiches.userId, userId),
      orderBy: desc(userNiches.updatedAt),
    })

    if (!userNiche) {
      // If no niche data, analyze first
      await this.analyzeUserNiche(userId)
      return this.getPersonalizedTrends(userId)
    }

    // Get trending topics that match user's niche
    const matchingTrends = await db.query.trendingTopics.findMany({
      where: and(
        sql`${trendingTopics.category} = ANY(${userNiche.contentThemes})`,
        gte(trendingTopics.expiresAt, new Date())
      ),
      orderBy: desc(trendingTopics.trendScore),
      limit: 20,
    })

    return matchingTrends
  }

  /**
   * Suggest content ideas based on trending topics
   */
  async generateContentIdeas(topic: string, userNiche?: string): Promise<string[]> {
    const prompt = `
    Generate 10 unique YouTube video ideas based on the trending topic "${topic}".
    ${userNiche ? `The content should fit the niche: ${userNiche}` : ''}
    
    Requirements:
    - Each idea should be specific and actionable
    - Include hook potential (attention-grabbing elements)
    - Consider SEO-friendly titles
    - Vary the content formats (tutorial, review, comparison, etc.)
    
    Return as a JSON array of strings.
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    try {
      // Extract JSON from response
      const jsonMatch = text.match(/\[[\s\S]*\]/)
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0])
      }
    } catch (error) {
      console.error('Error parsing AI response:', error)
    }

    // Fallback: split by lines and clean up
    return text
      .split('\n')
      .filter((line: string) => line.trim() && !line.includes('```'))
      .map((line: string) => line.replace(/^\d+\.\s*/, '').trim())
      .slice(0, 10)
  }

  /**
   * Analyze competitor channels for insights
   */
  async analyzeCompetitors(channelIds: string[]): Promise<any> {
    const competitorData = []

    for (const channelId of channelIds) {
      try {
        // Get channel info
        const channelResponse = await this.youtube.channels.list({
          part: ['snippet', 'statistics'],
          id: [channelId],
        })

        // Get recent videos
        const videosResponse = await this.youtube.search.list({
          part: ['snippet'],
          channelId: channelId,
          order: 'date',
          maxResults: 10,
        })

        const channel = channelResponse.data.items?.[0]
        const recentVideos = videosResponse.data.items || []

        if (channel) {
          competitorData.push({
            channelId,
            channelTitle: channel.snippet.title,
            subscriberCount: parseInt(channel.statistics.subscriberCount || '0'),
            videoCount: parseInt(channel.statistics.videoCount || '0'),
            recentTitles: recentVideos.map((v: any) => v.snippet.title),
            contentPattern: await this.analyzeContentPattern(recentVideos),
          })
        }
      } catch (error) {
        console.error(`Error analyzing channel ${channelId}:`, error)
      }
    }

    return competitorData
  }

  /**
   * Get trending keywords in a specific niche
   */
  async getTrendingKeywords(niche: string): Promise<string[]> {
    const trends = await db.query.trendingTopics.findMany({
      where: and(
        eq(trendingTopics.category, niche),
        gte(trendingTopics.expiresAt, new Date())
      ),
      orderBy: desc(trendingTopics.trendScore),
      limit: 10,
    })

    const keywords = new Set<string>()
    
    trends.forEach(trend => {
      trend.relatedKeywords?.forEach(keyword => keywords.add(keyword))
    })

    return Array.from(keywords).slice(0, 20)
  }

  /**
   * Private helper methods
   */
  private async analyzeTrendingPatterns(videos: TrendingVideoData[], region: string): Promise<DiscoveredTrend[]> {
    // Group videos by common themes/topics
    const topicGroups = this.groupVideosByTopic(videos)
    const trends: DiscoveredTrend[] = []

    for (const [topic, groupVideos] of Object.entries(topicGroups)) {
      if (groupVideos.length < 2) continue // Need at least 2 videos to be a trend

      const trendScore = this.calculateTrendScore(groupVideos)
      const relatedKeywords = this.extractKeywords(groupVideos)
      const sampleTitles = groupVideos.slice(0, 5).map(v => v.title)
      const sampleChannels = [...new Set(groupVideos.map(v => v.channelTitle))].slice(0, 5)

      trends.push({
        topic,
        category: this.categorizeContent(groupVideos),
        trendScore,
        relatedKeywords,
        sampleTitles,
        sampleChannels,
        competitionLevel: this.assessCompetitionLevel(groupVideos),
      })
    }

    return trends.sort((a, b) => b.trendScore - a.trendScore).slice(0, 20)
  }

  private groupVideosByTopic(videos: TrendingVideoData[]): Record<string, TrendingVideoData[]> {
    const groups: Record<string, TrendingVideoData[]> = {}
    
    videos.forEach(video => {
      const topic = this.extractMainTopic(video.title)
      if (!groups[topic]) {
        groups[topic] = []
      }
      groups[topic].push(video)
    })

    return groups
  }

  private extractMainTopic(title: string): string {
    // Simple topic extraction - in production, use more sophisticated NLP
    const words = title.toLowerCase().split(' ')
    const commonWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'why', 'when', 'where']
    const meaningfulWords = words.filter(word => word.length > 3 && !commonWords.includes(word))
    
    return meaningfulWords.slice(0, 2).join(' ')
  }

  private calculateTrendScore(videos: TrendingVideoData[]): number {
    const totalViews = videos.reduce((sum, video) => sum + video.viewCount, 0)
    const averageViews = totalViews / videos.length
    const recency = videos.filter(v => {
      const publishDate = new Date(v.publishedAt)
      const daysDiff = (Date.now() - publishDate.getTime()) / (1000 * 60 * 60 * 24)
      return daysDiff <= 7 // Published in last week
    }).length

    return Math.min(100, Math.round((averageViews / 100000) * 30 + (recency / videos.length) * 70))
  }

  private extractKeywords(videos: TrendingVideoData[]): string[] {
    const allTags = videos.flatMap(video => video.tags)
    const tagCount = new Map<string, number>()
    
    allTags.forEach(tag => {
      const normalized = tag.toLowerCase()
      tagCount.set(normalized, (tagCount.get(normalized) || 0) + 1)
    })

    return Array.from(tagCount.entries())
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([tag]) => tag)
  }

  private categorizeContent(videos: TrendingVideoData[]): string {
    // Simple categorization based on most common category
    const categories = videos.map(v => v.categoryId)
    const categoryCount = new Map<string, number>()
    
    categories.forEach(cat => {
      categoryCount.set(cat, (categoryCount.get(cat) || 0) + 1)
    })

    const topCategory = Array.from(categoryCount.entries())
      .sort(([, a], [, b]) => b - a)[0]?.[0]

    // Map YouTube category IDs to readable names
    const categoryMap: Record<string, string> = {
      '1': 'Film & Animation',
      '2': 'Autos & Vehicles',
      '10': 'Music',
      '15': 'Pets & Animals',
      '17': 'Sports',
      '19': 'Travel & Events',
      '20': 'Gaming',
      '22': 'People & Blogs',
      '23': 'Comedy',
      '24': 'Entertainment',
      '25': 'News & Politics',
      '26': 'Howto & Style',
      '27': 'Education',
      '28': 'Science & Technology',
    }

    return categoryMap[topCategory || '22'] || 'General'
  }

  private assessCompetitionLevel(videos: TrendingVideoData[]): 'low' | 'medium' | 'high' {
    const uniqueChannels = new Set(videos.map(v => v.channelTitle)).size
    const totalVideos = videos.length
    
    if (uniqueChannels / totalVideos > 0.8) return 'low'
    if (uniqueChannels / totalVideos > 0.5) return 'medium'
    return 'high'
  }

  private async performNicheAnalysis(contentData: any[]): Promise<NicheAnalysis> {
    const prompt = `
    Analyze the following YouTube content data to determine the creator's niche:
    
    ${JSON.stringify(contentData, null, 2)}
    
    Provide analysis in this exact JSON format:
    {
      "primaryNiche": "string",
      "confidence": number between 0-1,
      "keywords": ["array", "of", "keywords"],
      "contentThemes": ["array", "of", "themes"],
      "targetAudience": {
        "demographics": "description",
        "interests": ["interests"]
      },
      "competitorChannels": ["suggested", "competitor", "channels"],
      "performanceMetrics": {
        "recommendedTitleLength": number,
        "commonHooks": ["hooks"],
        "contentFormats": ["formats"]
      }
    }
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0])
      }
    } catch (error) {
      console.error('Error parsing niche analysis:', error)
    }

    // Fallback analysis
    return {
      primaryNiche: 'General',
      confidence: 0.5,
      keywords: [],
      contentThemes: ['General'],
      targetAudience: { demographics: 'General audience', interests: [] },
      competitorChannels: [],
      performanceMetrics: { recommendedTitleLength: 60, commonHooks: [], contentFormats: [] },
    }
  }

  private async analyzeContentPattern(videos: any[]): Promise<any> {
    const titles = videos.map((v: any) => v.snippet.title)
    
    // Simple pattern analysis
    return {
      averageTitleLength: titles.reduce((sum, title) => sum + title.length, 0) / titles.length,
      commonWords: this.findCommonWords(titles),
      uploadFrequency: 'unknown', // Would need more data to determine
    }
  }

  private findCommonWords(titles: string[]): string[] {
    const allWords = titles.flatMap(title => 
      title.toLowerCase().split(' ').filter(word => word.length > 3)
    )
    const wordCount = new Map<string, number>()
    
    allWords.forEach(word => {
      wordCount.set(word, (wordCount.get(word) || 0) + 1)
    })

    return Array.from(wordCount.entries())
      .filter(([, count]) => count > 1)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([word]) => word)
  }

  private async storeTrendingTopics(trends: DiscoveredTrend[]): Promise<void> {
    const expirationDate = new Date()
    expirationDate.setDate(expirationDate.getDate() + 7) // Trends expire in 7 days

    for (const trend of trends) {
      const trendData: NewTrendingTopic = {
        topic: trend.topic,
        category: trend.category,
        trendScore: trend.trendScore,
        searchVolume: trend.searchVolume,
        competitionLevel: trend.competitionLevel,
        relatedKeywords: trend.relatedKeywords,
        sampleTitles: trend.sampleTitles,
        sampleChannels: trend.sampleChannels,
        expiresAt: expirationDate,
      }

      await db.insert(trendingTopics).values(trendData)
    }
  }

  private async storeUserNiche(userId: string, analysis: NicheAnalysis): Promise<void> {
    const nicheData: NewUserNiche = {
      userId,
      niche: analysis.primaryNiche,
      keywords: analysis.keywords,
      competitorChannels: analysis.competitorChannels,
      targetAudience: analysis.targetAudience,
      contentThemes: analysis.contentThemes,
      performanceMetrics: analysis.performanceMetrics,
    }

    await db.insert(userNiches).values(nicheData)
      .onConflictDoUpdate({
        target: userNiches.userId,
        set: {
          ...nicheData,
          updatedAt: new Date(),
        },
      })
  }
}