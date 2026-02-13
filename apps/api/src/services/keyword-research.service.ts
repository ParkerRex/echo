import { GoogleGenerativeAI } from '@google/generative-ai'
import { google } from 'googleapis'
import { getEnv } from '../types/env'
import { db } from '../db/client'
import { trendingTopics, userNiches } from '../db/schema'
import { eq, and, sql, desc } from 'drizzle-orm'

const env = getEnv()

export interface KeywordData {
  keyword: string
  searchVolume: number
  competition: 'low' | 'medium' | 'high'
  cpc?: number // Cost per click (if available)
  trend: 'rising' | 'stable' | 'declining'
  difficulty: number // 1-100 scale
  relatedKeywords: string[]
  questions: string[] // Question-based keywords
}

export interface SEOAnalysis {
  title: string
  optimizedTitle: string
  seoScore: number
  improvements: string[]
  targetKeywords: string[]
  titleLength: number
  readabilityScore: number
}

export interface TagSuggestion {
  tag: string
  relevanceScore: number
  searchVolume?: number
  competition: 'low' | 'medium' | 'high'
  reason: string
}

export interface ContentOptimization {
  optimizedDescription: string
  suggestedTags: TagSuggestion[]
  seoKeywords: string[]
  metaDescription: string
  hashtags: string[]
  contentStructure: {
    hook: string
    mainPoints: string[]
    callToAction: string
  }
}

export class KeywordResearchService {
  private genAI: GoogleGenerativeAI
  private model: any
  private youtube: any

  constructor() {
    this.genAI = new GoogleGenerativeAI(env.GEMINI_API_KEY)
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' })
    
    this.youtube = google.youtube({
      version: 'v3',
      auth: (env as any).YOUTUBE_API_KEY || env.GOOGLE_CLIENT_ID,
    })
  }

  /**
   * Get keyword suggestions for a topic
   */
  async getKeywordSuggestions(topic: string, niche?: string): Promise<KeywordData[]> {
    const prompt = `
    Generate keyword research data for the topic "${topic}" ${niche ? `in the ${niche} niche` : ''}.
    
    Provide comprehensive keyword analysis in this exact JSON format:
    [
      {
        "keyword": "string",
        "searchVolume": number,
        "competition": "low|medium|high",
        "trend": "rising|stable|declining",
        "difficulty": number,
        "relatedKeywords": ["array", "of", "related"],
        "questions": ["question", "based", "keywords"]
      }
    ]
    
    Include:
    - Primary keywords (high volume, competitive)
    - Long-tail keywords (lower volume, less competitive)
    - Question-based keywords (What, How, Why, etc.)
    - Location-based variations if relevant
    - Seasonal variations if applicable
    
    Provide 15-20 keywords total.
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    try {
      const jsonMatch = text.match(/\[[\s\S]*\]/)
      if (jsonMatch) {
        const keywords = JSON.parse(jsonMatch[0])
        
        // Enhance with YouTube-specific data
        return await this.enhanceWithYouTubeData(keywords)
      }
    } catch (error) {
      console.error('Error parsing keyword suggestions:', error)
    }

    return []
  }

  /**
   * Analyze and optimize a video title for SEO
   */
  async optimizeTitle(originalTitle: string, niche: string, targetKeywords: string[] = []): Promise<SEOAnalysis> {
    const prompt = `
    Analyze and optimize this YouTube video title for SEO:
    Original title: "${originalTitle}"
    Niche: ${niche}
    Target keywords: ${targetKeywords.join(', ')}
    
    Provide analysis in this exact JSON format:
    {
      "optimizedTitle": "string",
      "seoScore": number,
      "improvements": ["array", "of", "improvements"],
      "targetKeywords": ["keywords", "found", "or", "suggested"],
      "titleLength": number,
      "readabilityScore": number
    }
    
    Guidelines:
    - Keep titles under 60 characters for full display
    - Include target keywords naturally
    - Make it compelling and clickable
    - Maintain accuracy to content
    - Consider search intent
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const analysis = JSON.parse(jsonMatch[0])
        return {
          title: originalTitle,
          ...analysis,
        }
      }
    } catch (error) {
      console.error('Error parsing title optimization:', error)
    }

    // Fallback analysis
    return {
      title: originalTitle,
      optimizedTitle: originalTitle,
      seoScore: 50,
      improvements: ['Consider adding target keywords'],
      targetKeywords: [],
      titleLength: originalTitle.length,
      readabilityScore: 70,
    }
  }

  /**
   * Generate optimized description for SEO
   */
  async generateSEODescription(
    transcript: string, 
    title: string, 
    keywords: string[],
    niche: string
  ): Promise<ContentOptimization> {
    const prompt = `
    Create SEO-optimized YouTube content based on:
    
    Title: ${title}
    Niche: ${niche}
    Target Keywords: ${keywords.join(', ')}
    Transcript excerpt: ${transcript.substring(0, 1000)}...
    
    Provide optimization in this exact JSON format:
    {
      "optimizedDescription": "string",
      "suggestedTags": [
        {
          "tag": "string",
          "relevanceScore": number,
          "competition": "low|medium|high",
          "reason": "string"
        }
      ],
      "seoKeywords": ["array", "of", "keywords"],
      "metaDescription": "string",
      "hashtags": ["array", "of", "hashtags"],
      "contentStructure": {
        "hook": "string",
        "mainPoints": ["array", "of", "points"],
        "callToAction": "string"
      }
    }
    
    Requirements:
    - Description should be 125-200 words
    - Include target keywords naturally (2-3% density)
    - Add compelling call-to-action
    - Include relevant links placeholders
    - Tags should be specific and searchable
    - Hashtags should be relevant and trending
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
      console.error('Error parsing content optimization:', error)
    }

    // Fallback optimization
    return {
      optimizedDescription: transcript.substring(0, 200) + '...',
      suggestedTags: keywords.map(keyword => ({
        tag: keyword,
        relevanceScore: 0.8,
        competition: 'medium' as const,
        reason: 'Related to content topic',
      })),
      seoKeywords: keywords,
      metaDescription: title,
      hashtags: keywords.map(k => `#${k.replace(/\s+/g, '')}`),
      contentStructure: {
        hook: 'Engaging opening statement',
        mainPoints: ['Key point 1', 'Key point 2', 'Key point 3'],
        callToAction: 'Like and subscribe for more content!',
      },
    }
  }

  /**
   * Suggest optimal tags for video content
   */
  async suggestOptimalTags(
    content: string, 
    niche: string, 
    maxTags: number = 15
  ): Promise<TagSuggestion[]> {
    // Get trending keywords in the niche
    const trendingInNiche = await this.getTrendingKeywordsInNiche(niche)
    
    const prompt = `
    Suggest optimal YouTube tags for this content:
    
    Content: ${content.substring(0, 500)}...
    Niche: ${niche}
    Trending in niche: ${trendingInNiche.join(', ')}
    
    Provide ${maxTags} tags in this exact JSON format:
    [
      {
        "tag": "string",
        "relevanceScore": number,
        "competition": "low|medium|high",
        "reason": "string"
      }
    ]
    
    Balance:
    - High-relevance primary tags (exact content match)
    - Medium-relevance secondary tags (niche-related)
    - Low-competition long-tail tags
    - Trending tags in the niche
    - Evergreen tags for discovery
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    try {
      const jsonMatch = text.match(/\[[\s\S]*\]/)
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0])
      }
    } catch (error) {
      console.error('Error parsing tag suggestions:', error)
    }

    return []
  }

  /**
   * Analyze keyword competition on YouTube
   */
  async analyzeKeywordCompetition(keyword: string): Promise<{
    competition: 'low' | 'medium' | 'high'
    searchResults: number
    topChannelTypes: string[]
    avgViews: number
    difficulty: number
  }> {
    try {
      // Search YouTube for the keyword
      const searchResponse = await this.youtube.search.list({
        part: ['snippet'],
        q: keyword,
        type: 'video',
        maxResults: 50,
        order: 'relevance',
      })

      const videos = searchResponse.data.items || []
      
      // Get detailed stats for top videos
      const videoIds = videos.slice(0, 10).map((v: any) => v.id.videoId)
      const statsResponse = await this.youtube.videos.list({
        part: ['statistics', 'snippet'],
        id: videoIds,
      })

      const videoStats = statsResponse.data.items || []
      
      // Analyze competition
      const avgViews = videoStats.reduce((sum: number, video: any) => {
        return sum + parseInt(video.statistics?.viewCount || '0')
      }, 0) / videoStats.length

      const channelTypes = videoStats.map((video: any) => 
        this.categorizeChannel(video.snippet?.channelTitle || '')
      )

      const uniqueChannelTypes = [...new Set(channelTypes)]
      
      // Determine competition level
      let competition: 'low' | 'medium' | 'high' = 'medium'
      if (avgViews < 10000) competition = 'low'
      else if (avgViews > 100000) competition = 'high'

      return {
        competition,
        searchResults: videos.length,
        topChannelTypes: uniqueChannelTypes as string[],
        avgViews: Math.round(avgViews),
        difficulty: this.calculateDifficulty(avgViews, uniqueChannelTypes.length),
      }
    } catch (error) {
      console.error('Error analyzing keyword competition:', error)
      return {
        competition: 'medium',
        searchResults: 0,
        topChannelTypes: [],
        avgViews: 0,
        difficulty: 50,
      }
    }
  }

  /**
   * Get personalized keyword suggestions based on user's niche
   */
  async getPersonalizedKeywords(userId: string, topic: string): Promise<KeywordData[]> {
    // Get user's niche data
    const userNiche = await db.query.userNiches.findFirst({
      where: eq(userNiches.userId, userId),
      orderBy: desc(userNiches.updatedAt),
    })

    const niche = userNiche?.niche || 'general'
    const existingKeywords = userNiche?.keywords || []

    // Get keywords that performed well for this user
    const performanceKeywords = (userNiche as any)?.performanceMetrics?.topKeywords || []

    const prompt = `
    Generate personalized keyword suggestions for:
    Topic: ${topic}
    User's niche: ${niche}
    User's existing keywords: ${existingKeywords.join(', ')}
    Previously successful keywords: ${performanceKeywords.join(', ')}
    
    Focus on:
    - Keywords that align with user's proven content style
    - Long-tail variations of successful keywords
    - Emerging trends in their niche
    - Keywords their competitors might be missing
    
    Provide suggestions in the standard keyword format.
    `

    return await this.getKeywordSuggestions(topic, niche)
  }

  /**
   * Track keyword performance over time
   */
  async trackKeywordPerformance(keywords: string[]): Promise<any[]> {
    const performanceData = []

    for (const keyword of keywords) {
      try {
        const competition = await this.analyzeKeywordCompetition(keyword)
        const trends = await this.getKeywordTrends(keyword)
        
        performanceData.push({
          keyword,
          ...competition,
          trends,
          lastUpdated: new Date(),
        })
      } catch (error) {
        console.error(`Error tracking keyword ${keyword}:`, error)
      }
    }

    return performanceData
  }

  /**
   * Private helper methods
   */
  private async enhanceWithYouTubeData(keywords: KeywordData[]): Promise<KeywordData[]> {
    const enhanced = []

    for (const keyword of keywords) {
      try {
        const competition = await this.analyzeKeywordCompetition(keyword.keyword)
        enhanced.push({
          ...keyword,
          competition: competition.competition,
          difficulty: competition.difficulty,
        })
      } catch (error) {
        enhanced.push(keyword) // Use original data if enhancement fails
      }
    }

    return enhanced
  }

  private async getTrendingKeywordsInNiche(niche: string): Promise<string[]> {
    const trends = await db.query.trendingTopics.findMany({
      where: eq(trendingTopics.category, niche),
      orderBy: desc(trendingTopics.trendScore),
      limit: 10,
    })

    return trends.flatMap(trend => trend.relatedKeywords || [])
  }

  private categorizeChannel(channelTitle: string): string {
    // Simple channel categorization
    const title = channelTitle.toLowerCase()
    
    if (title.includes('official') || title.includes('music')) return 'official'
    if (title.includes('news') || title.includes('media')) return 'media'
    if (title.includes('tutorial') || title.includes('how')) return 'educational'
    if (title.includes('gaming') || title.includes('game')) return 'gaming'
    if (title.includes('tech') || title.includes('review')) return 'tech'
    
    return 'creator'
  }

  private calculateDifficulty(avgViews: number, channelVariety: number): number {
    // Simple difficulty calculation
    let difficulty = 50 // Base difficulty

    // Higher average views = higher difficulty
    if (avgViews > 1000000) difficulty += 30
    else if (avgViews > 100000) difficulty += 20
    else if (avgViews > 10000) difficulty += 10

    // More channel variety = lower difficulty (less saturated)
    if (channelVariety > 8) difficulty -= 10
    else if (channelVariety < 3) difficulty += 20

    return Math.max(1, Math.min(100, difficulty))
  }

  private async getKeywordTrends(keyword: string): Promise<any> {
    // This would integrate with Google Trends API or similar
    // For now, return mock trend data
    return {
      trend: 'stable',
      searchVolume: Math.floor(Math.random() * 10000),
      relatedQueries: [],
    }
  }
}