import { GoogleGenerativeAI } from '@google/generative-ai'
import OpenAI from 'openai'
import { getEnv } from '../types/env'
import { createReadStream } from 'fs'
import { StorageService } from './storage.service'
import { db } from '../db/client'
import { contentVariants, userNiches, youtubePublications } from '../db/schema'
import { eq, desc } from 'drizzle-orm'

const env = getEnv()

export interface ChatContext {
  videoTitle?: string | null
  videoDescription?: string | null
  transcript?: string | null
  recentMessages?: Array<{
    role: string
    content: string
  }>
}

export interface ChatResponse {
  content: string
  model: string
  tokens?: {
    input: number
    output: number
  }
}

export interface StreamChunk {
  content: string
  isComplete: boolean
}

export interface ContentVariant {
  id: string
  type: 'title' | 'thumbnail' | 'description' | 'tags'
  originalContent: string
  variantContent: string
  confidenceScore: number
  predictedPerformance: {
    estimatedCTR: number
    estimatedViews: number
    estimatedEngagement: number
    strengths: string[]
    weaknesses: string[]
  }
  generationReason: string
}

export interface PerformancePrediction {
  estimatedViews: number
  estimatedCTR: number
  estimatedRetention: number
  estimatedEngagement: number
  confidenceLevel: number
  factors: {
    titleStrength: number
    thumbnailAppeal: number
    contentQuality: number
    nicheAlignment: number
    trendRelevance: number
  }
  recommendations: string[]
}

export interface HookAnalysis {
  hookStrength: number
  attentionGrabbers: string[]
  improvements: string[]
  optimalHookLength: number
  emotionalTriggers: string[]
  curiosityGaps: string[]
}

export class AIService {
  private genAI: GoogleGenerativeAI
  private model: any
  private openai: OpenAI | null
  private storageService: StorageService

  constructor() {
    this.genAI = new GoogleGenerativeAI(env.GEMINI_API_KEY)
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' })
    
    // Initialize OpenAI if API key is available
    this.openai = env.OPENAI_API_KEY ? new OpenAI({ apiKey: env.OPENAI_API_KEY }) : null
    this.storageService = new StorageService()
  }

  /**
   * Transcribe audio to text using OpenAI Whisper
   */
  async transcribeAudio(audioUrl: string): Promise<string> {
    console.log('Transcribing audio from:', audioUrl)

    // If OpenAI is not configured, fall back to generating a summary
    if (!this.openai) {
      console.warn('OpenAI API key not configured, using fallback transcription')
      return this.generateFallbackTranscript(audioUrl)
    }

    try {
      // Download audio file to temp location if it's a URL
      let audioPath = audioUrl
      let tempFile: string | null = null

      if (audioUrl.startsWith('http')) {
        // Download the file temporarily
        const response = await fetch(audioUrl)
        const buffer = await response.arrayBuffer()
        
        // Create a temporary file
        const { writeFile, unlink } = await import('fs/promises')
        const { tmpdir } = await import('os')
        const { join } = await import('path')
        const { randomUUID } = await import('crypto')
        
        tempFile = join(tmpdir(), `${randomUUID()}.mp3`)
        await writeFile(tempFile, Buffer.from(buffer))
        audioPath = tempFile
      }

      // Create a readable stream for the audio file
      const audioStream = createReadStream(audioPath)

      // Use Whisper API to transcribe
      const transcription = await this.openai.audio.transcriptions.create({
        file: audioStream,
        model: 'whisper-1',
        response_format: 'text',
        language: 'en', // You can make this dynamic based on video metadata
      })

      // Clean up temp file if created
      if (tempFile) {
        const { unlink } = await import('fs/promises')
        await unlink(tempFile).catch(() => {}) // Ignore cleanup errors
      }

      return transcription
    } catch (error) {
      console.error('Whisper transcription error:', error)
      // Fall back to basic transcription
      return this.generateFallbackTranscript(audioUrl)
    }
  }

  /**
   * Generate a fallback transcript when Whisper is unavailable
   */
  private async generateFallbackTranscript(audioUrl: string): Promise<string> {
    // Use Gemini to generate a placeholder transcript based on filename
    const fileName = audioUrl.split('/').pop() || 'video'
    const prompt = `
      Generate a realistic video transcript for a video file named "${fileName}".
      Make it sound natural with some filler words and conversational tone.
      Keep it around 200-300 words.
      
      Return only the transcript text without any formatting or labels.
    `

    try {
      const result = await this.model.generateContent(prompt)
      const response = await result.response
      return response.text()
    } catch (error) {
      console.error('Fallback transcript generation error:', error)
      return 'Welcome to this video. Today we will be discussing important topics and sharing valuable insights. Thank you for watching.'
    }
  }

  /**
   * Generate subtitles from transcript
   */
  async generateSubtitles(transcript: string): Promise<any> {
    const prompt = `
      Convert the following transcript into SRT subtitle format.
      Break it into appropriate segments (max 2 lines per subtitle, ~5-7 words per line).
      Include proper timing (assume average speaking pace).
      
      Transcript:
      ${transcript}
      
      Return ONLY the SRT format without any explanation.
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const srtContent = response.text()

    // Parse SRT to structured format
    const subtitles = this.parseSRT(srtContent)

    return {
      srt: srtContent,
      entries: subtitles,
    }
  }

  /**
   * Generate video metadata (titles, description, tags)
   */
  async generateVideoMetadata(
    transcript: string,
    fileName: string
  ): Promise<{
    titles: string[]
    description: string
    tags: string[]
  }> {
    // First, extract key topics from the transcript
    const topics = await this.extractTopics(transcript)
    
    const prompt = `
      You are a YouTube optimization expert. Based on the following video transcript, generate highly optimized metadata.
      
      Video Context:
      - Filename: ${fileName}
      - Key Topics: ${topics.join(', ')}
      - Transcript excerpt: ${transcript.substring(0, 2000)}...
      
      Generate:
      
      1. **10 YouTube Titles** (Requirements):
         - Each title MUST be 50-60 characters (YouTube's sweet spot)
         - Use these proven formulas:
           • How to [achieve desired outcome] in [timeframe]
           • [Number] [adjective] Ways to [solve problem]
           • Why [counterintuitive statement] (And What to Do Instead)
           • The [adjective] Guide to [topic] for [audience]
           • [Do this] Before [consequence]
         - Include power words: Ultimate, Essential, Proven, Secret, Mistakes
         - Add numbers when relevant
         - Create curiosity gaps
         - Front-load keywords
      
      2. **SEO-Optimized Description** (150-300 words):
         - First 125 characters are crucial (shown in search)
         - Include primary keywords naturally
         - Add timestamps section
         - Include relevant links placeholder
         - End with engagement question
         - Add 3-5 relevant hashtags
      
      3. **Tags** (15-20 tags):
         - Mix broad and specific keywords
         - Include variations and synonyms
         - Add competitor/related channel names
         - Include year if relevant (e.g., "tutorial 2024")
      
      Return ONLY valid JSON:
      {
        "titles": ["exactly 10 titles"],
        "description": "full description with line breaks as \\n",
        "tags": ["15-20 relevant tags"]
      }
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    try {
      // Extract JSON from response
      const jsonMatch = text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        // Ensure we have exactly 10 titles
        if (parsed.titles && Array.isArray(parsed.titles)) {
          parsed.titles = parsed.titles.slice(0, 10)
          while (parsed.titles.length < 10) {
            parsed.titles.push(
              `${fileName.replace(/\.[^/.]+$/, '')} - Part ${parsed.titles.length + 1}`.substring(
                0,
                60
              )
            )
          }
        }
        return parsed
      }
    } catch (error) {
      console.error('Failed to parse AI response:', error)
    }

    // Fallback
    const baseTitle = fileName.replace(/\.[^/.]+$/, '').substring(0, 50)
    return {
      titles: [
        `${baseTitle} - Complete Guide`,
        `How to ${baseTitle}`,
        `${baseTitle} Explained`,
        `${baseTitle} Tutorial`,
        `${baseTitle} - What You Need to Know`,
        `The Truth About ${baseTitle}`,
        `${baseTitle} for Beginners`,
        `Master ${baseTitle} in Minutes`,
        `${baseTitle} - Tips & Tricks`,
        `Everything About ${baseTitle}`,
      ],
      description: 'Video description generated from transcript.',
      tags: ['video', 'tutorial', 'guide', 'howto', 'tips'],
    }
  }

  /**
   * Generate chat response
   */
  async generateChatResponse(message: string, context: ChatContext): Promise<ChatResponse> {
    const systemPrompt = this.buildSystemPrompt(context)
    const conversationHistory = this.buildConversationHistory(context.recentMessages || [])

    const prompt = `
      ${systemPrompt}
      
      ${conversationHistory}
      
      User: ${message}
      Assistant:
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response

    return {
      content: response.text(),
      model: 'gemini-pro',
      tokens: {
        input: prompt.length / 4, // Rough estimate
        output: response.text().length / 4,
      },
    }
  }

  /**
   * Stream chat response
   */
  async *streamChatResponse(message: string, context: ChatContext): AsyncGenerator<StreamChunk> {
    const systemPrompt = this.buildSystemPrompt(context)
    const conversationHistory = this.buildConversationHistory(context.recentMessages || [])

    const prompt = `
      ${systemPrompt}
      
      ${conversationHistory}
      
      User: ${message}
      Assistant:
    `

    const result = await this.model.generateContentStream(prompt)

    for await (const chunk of result.stream) {
      const text = chunk.text()
      if (text) {
        yield {
          content: text,
          isComplete: false,
        }
      }
    }

    yield {
      content: '',
      isComplete: true,
    }
  }

  /**
   * Build system prompt based on context
   */
  private buildSystemPrompt(context: ChatContext): string {
    let prompt = 'You are a helpful AI assistant.'

    if (context.videoTitle || context.transcript) {
      prompt += ' You are discussing a video'
      if (context.videoTitle) {
        prompt += ` titled "${context.videoTitle}"`
      }
      if (context.videoDescription) {
        prompt += `. Description: ${context.videoDescription}`
      }
      if (context.transcript) {
        prompt += `\n\nVideo transcript excerpt:\n${context.transcript.substring(0, 500)}...`
      }
    }

    prompt += '\n\nProvide helpful, accurate, and contextual responses.'

    return prompt
  }

  /**
   * Build conversation history
   */
  private buildConversationHistory(messages: Array<{ role: string; content: string }>): string {
    if (!messages.length) return ''

    return (
      'Recent conversation:\n' +
      messages
        .slice(-5) // Last 5 messages
        .map((msg) => `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`)
        .join('\n')
    )
  }

  /**
   * Parse SRT format to structured data
   */
  private parseSRT(srtContent: string): Array<{
    index: number
    startTime: string
    endTime: string
    text: string
  }> {
    const entries: any[] = []
    const blocks = srtContent.trim().split('\n\n')

    for (const block of blocks) {
      const lines = block.trim().split('\n')
      if (lines.length >= 3) {
        const index = parseInt(lines[0]!)
        const [startTime, endTime] = lines[1]!.split(' --> ')
        const text = lines.slice(2).join('\n')

        entries.push({
          index,
          startTime: startTime?.trim() || '',
          endTime: endTime?.trim() || '',
          text: text.trim(),
        })
      }
    }

    return entries
  }

  /**
   * Summarize long text
   */
  async summarize(text: string, maxLength: number = 500): Promise<string> {
    const prompt = `
      Summarize the following text in ${maxLength} characters or less:
      
      ${text}
      
      Provide a clear, concise summary that captures the main points.
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response

    return response.text()
  }

  /**
   * Extract key topics from text
   */
  async extractTopics(text: string): Promise<string[]> {
    const prompt = `
      Extract 5-10 key topics from the following text.
      Return only the topics as a comma-separated list.
      
      Text: ${text}
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const topicsText = response.text()

    return topicsText
      .split(',')
      .map((topic: string) => topic.trim())
      .filter((topic: string) => topic.length > 0)
  }

  /**
   * Generate thumbnail backgrounds using DALL-E 3 or fallback services
   */
  async generateThumbnailBackgrounds(
    videoTitle: string,
    description: string,
    topics: string[],
    count: number = 4
  ): Promise<string[]> {
    const thumbnailUrls: string[] = []

    // Different styles for variety
    const styles = [
      'vibrant gradient background with abstract geometric shapes, modern and eye-catching',
      'cinematic dramatic lighting with deep shadows and highlights, professional atmosphere',
      'minimalist modern design with bold contrasting colors and clean composition',
      'dynamic energy with motion blur effects and explosive colors, high impact',
    ]

    // Color schemes for each style
    const colorSchemes = [
      'purple to orange gradient with teal accents',
      'deep blue and gold with dramatic contrast',
      'black, white, and electric blue minimalist palette',
      'neon pink, cyan, and yellow with dark background',
    ]

    try {
      // Use DALL-E 3 if OpenAI is configured
      if (this.openai) {
        for (let i = 0; i < count; i++) {
          const prompt = `
            Create a YouTube thumbnail background image. 
            Style: ${styles[i % styles.length]}
            Color scheme: ${colorSchemes[i % colorSchemes.length]}
            Theme: ${topics.slice(0, 2).join(' and ')}
            
            Requirements:
            - Cinematic 16:9 composition
            - High contrast for thumbnail visibility
            - Leave center-left area less busy for text overlay
            - No text, letters, or words in the image
            - Professional quality suitable for ${topics[0] || 'educational'} content
            - Eye-catching and scroll-stopping design
          `.trim()

          try {
            const response = await this.openai.images.generate({
              model: 'dall-e-3',
              prompt,
              n: 1,
              size: '1792x1024', // Closest to 16:9 that DALL-E 3 supports
              quality: 'hd',
              style: 'vivid',
            })

            if (response.data?.[0]?.url) {
              // Upload to our storage for permanent URL
              const imageResponse = await fetch(response.data[0].url)
              const imageBuffer = await imageResponse.arrayBuffer()
              
              const permanentUrl = await this.storageService.uploadFile({
                fileName: `thumbnail-${videoTitle.substring(0, 20)}-${i}.png`,
                data: Buffer.from(imageBuffer),
                mimeType: 'image/png',
                userId: 'system', // System-generated content
              })
              
              thumbnailUrls.push(permanentUrl)
            }
          } catch (error) {
            console.error(`Failed to generate thumbnail ${i + 1}:`, error)
            // Continue to try generating others
          }
        }
      }

      // If we couldn't generate enough with DALL-E, use high-quality stock photos
      const fallbackUrls = [
        'https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop', // Gradient
        'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1920&h=1080&fit=crop', // Tech
        'https://images.unsplash.com/photo-1563089145-599997674d42?w=1920&h=1080&fit=crop', // Abstract
        'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=1920&h=1080&fit=crop', // Nature
      ]

      // Fill remaining slots with fallback images
      for (let i = thumbnailUrls.length; i < count; i++) {
        thumbnailUrls.push(fallbackUrls[i % fallbackUrls.length]!)
      }
    } catch (error) {
      console.error('Thumbnail generation error:', error)
      // Return high-quality fallback thumbnails
      return [
        'https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&h=1080&fit=crop',
        'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1920&h=1080&fit=crop',
        'https://images.unsplash.com/photo-1563089145-599997674d42?w=1920&h=1080&fit=crop',
        'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=1920&h=1080&fit=crop',
      ].slice(0, count)
    }

    return thumbnailUrls.slice(0, count)
  }

  /**
   * Generate content variants for A/B testing
   */
  async generateContentVariants(
    content: string, 
    type: 'title' | 'thumbnail' | 'description' | 'tags',
    userId: string,
    count: number = 5
  ): Promise<ContentVariant[]> {
    // Get user's niche for context
    const userNiche = await db.query.userNiches.findFirst({
      where: eq(userNiches.userId, userId),
      orderBy: desc(userNiches.updatedAt),
    })

    const niche = userNiche?.niche || 'general'
    const variants: ContentVariant[] = []

    const prompt = `
    Generate ${count} alternative variations for this YouTube ${type}:
    Original: "${content}"
    User's niche: ${niche}
    Target audience: ${JSON.stringify(userNiche?.targetAudience || 'general')}
    
    Create variations that test different approaches:
    1. Emotional vs Logical appeal
    2. Short vs Long format (when applicable)
    3. Question vs Statement format
    4. Urgency vs Evergreen timing
    5. Different keywords and hooks
    
    For each variant, provide:
    - The variant content
    - Confidence score (0-1)
    - Predicted performance metrics
    - Generation reasoning
    
    Return as JSON array:
    [
      {
        "variantContent": "string",
        "confidenceScore": number,
        "predictedPerformance": {
          "estimatedCTR": number,
          "estimatedViews": number,
          "estimatedEngagement": number,
          "strengths": ["array"],
          "weaknesses": ["array"]
        },
        "generationReason": "string"
      }
    ]
    `

    const result = await this.model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    try {
      const jsonMatch = text.match(/\[[\s\S]*\]/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        
        for (let i = 0; i < parsed.length; i++) {
          const variant = parsed[i]
          variants.push({
            id: `variant_${Date.now()}_${i}`,
            type,
            originalContent: content,
            variantContent: variant.variantContent,
            confidenceScore: variant.confidenceScore,
            predictedPerformance: variant.predictedPerformance,
            generationReason: variant.generationReason,
          })
        }
      }
    } catch (error) {
      console.error('Error parsing content variants:', error)
    }

    return variants
  }

  /**
   * Predict video performance based on metadata and content
   */
  async predictPerformance(
    title: string, 
    thumbnail: string, 
    description: string,
    niche: string,
    userId?: string
  ): Promise<PerformancePrediction> {
    // Get historical performance data if user provided
    let historicalContext = ''
    if (userId) {
      const userPublications = await db.query.youtubePublications.findMany({
        where: eq(youtubePublications.userId, userId),
        orderBy: desc(youtubePublications.publishedAt),
        limit: 10,
      })

      if (userPublications.length > 0) {
        const avgViews = userPublications.reduce((sum, pub) => sum + (pub.viewCount || 0), 0) / userPublications.length
        const avgCTR = userPublications.reduce((sum, pub) => {
          const metadata = pub.metadata as any
          return sum + (metadata?.clickThroughRate || 0.03)
        }, 0) / userPublications.length

        historicalContext = `
        User's historical performance:
        - Average views: ${Math.round(avgViews)}
        - Average CTR: ${(avgCTR * 100).toFixed(2)}%
        - Channel size: ${userPublications.length > 5 ? 'established' : 'growing'}
        `
      }
    }

    const prompt = `
    Predict YouTube video performance based on:
    
    Title: "${title}"
    Thumbnail description: "${thumbnail}"
    Description: "${description.substring(0, 500)}..."
    Niche: ${niche}
    ${historicalContext}
    
    Analyze and predict performance in this exact JSON format:
    {
      "estimatedViews": number,
      "estimatedCTR": number,
      "estimatedRetention": number,
      "estimatedEngagement": number,
      "confidenceLevel": number,
      "factors": {
        "titleStrength": number,
        "thumbnailAppeal": number,
        "contentQuality": number,
        "nicheAlignment": number,
        "trendRelevance": number
      },
      "recommendations": ["array", "of", "improvements"]
    }
    
    Consider:
    - Title hook strength and keyword optimization
    - Thumbnail visual appeal and click-worthiness
    - Content depth and value proposition
    - Niche fit and audience alignment
    - Current trends and seasonality
    - Competitive landscape
    
    Use realistic metrics based on channel size and niche.
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
      console.error('Error parsing performance prediction:', error)
    }

    // Fallback prediction
    return {
      estimatedViews: 1000,
      estimatedCTR: 0.03,
      estimatedRetention: 0.45,
      estimatedEngagement: 0.02,
      confidenceLevel: 0.6,
      factors: {
        titleStrength: 0.7,
        thumbnailAppeal: 0.6,
        contentQuality: 0.7,
        nicheAlignment: 0.8,
        trendRelevance: 0.5,
      },
      recommendations: ['Improve title hook', 'Optimize thumbnail contrast'],
    }
  }

  /**
   * Analyze content hooks for retention optimization
   */
  async analyzeContentHooks(transcript: string): Promise<HookAnalysis> {
    const firstMinute = transcript.substring(0, 1000) // Approximate first minute
    
    const prompt = `
    Analyze the opening hook of this video transcript:
    
    "${firstMinute}"
    
    Evaluate for audience retention and provide analysis in this exact JSON format:
    {
      "hookStrength": number,
      "attentionGrabbers": ["array", "of", "elements"],
      "improvements": ["array", "of", "suggestions"],
      "optimalHookLength": number,
      "emotionalTriggers": ["array", "of", "triggers"],
      "curiosityGaps": ["array", "of", "gaps"]
    }
    
    Consider:
    - Does it immediately grab attention?
    - Are there curiosity gaps or cliffhangers?
    - Does it promise value or transformation?
    - Is there emotional engagement?
    - How quickly does it get to the point?
    - Are there any retention killers?
    
    Hook strength: 1-10 scale
    Optimal length: seconds for maximum retention
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
      console.error('Error parsing hook analysis:', error)
    }

    // Fallback analysis
    return {
      hookStrength: 5,
      attentionGrabbers: ['Opening statement'],
      improvements: ['Add curiosity gap', 'Increase energy'],
      optimalHookLength: 15,
      emotionalTriggers: [],
      curiosityGaps: [],
    }
  }

  /**
   * Generate content ideas based on trending topics and user niche
   */
  async generateContentIdeas(
    trendingTopics: string[], 
    userNiche: string,
    count: number = 10
  ): Promise<string[]> {
    const prompt = `
    Generate ${count} specific YouTube video ideas that combine:
    
    Trending topics: ${trendingTopics.join(', ')}
    User's niche: ${userNiche}
    
    Requirements for each idea:
    - Specific and actionable title
    - Combines trending elements with niche expertise
    - Has clear value proposition
    - Searchable and discoverable
    - Unique angle or perspective
    
    Return as JSON array of strings:
    ["idea 1", "idea 2", ...]
    
    Focus on formats that perform well:
    - How-to guides with trending tools/methods
    - Reaction/analysis of trending events
    - Comparisons involving trending topics
    - "What if" scenarios with current trends
    - Predictions about trending developments
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
      console.error('Error parsing content ideas:', error)
    }

    // Fallback ideas
    return [
      `How to use ${trendingTopics[0] || 'new tools'} for ${userNiche}`,
      `${userNiche} trends in 2024: What you need to know`,
      `My honest reaction to ${trendingTopics[0] || 'recent developments'}`,
      `${userNiche} vs ${trendingTopics[0] || 'new approaches'}: Which is better?`,
      `The future of ${userNiche}: Predictions and insights`,
    ].slice(0, count)
  }

  /**
   * Optimize content for specific goals (views, engagement, retention)
   */
  async optimizeForGoal(
    content: { title: string; description: string; tags: string[] },
    goal: 'views' | 'engagement' | 'retention' | 'subscribers',
    niche: string
  ): Promise<{
    optimizedTitle: string
    optimizedDescription: string
    optimizedTags: string[]
    changes: string[]
    reasoning: string
  }> {
    const prompt = `
    Optimize this YouTube content for maximum ${goal}:
    
    Current content:
    Title: "${content.title}"
    Description: "${content.description}"
    Tags: ${content.tags.join(', ')}
    Niche: ${niche}
    
    Optimization strategies for ${goal}:
    ${this.getOptimizationStrategies(goal)}
    
    Return optimized content in this exact JSON format:
    {
      "optimizedTitle": "string",
      "optimizedDescription": "string", 
      "optimizedTags": ["array"],
      "changes": ["list", "of", "changes", "made"],
      "reasoning": "explanation of optimization strategy"
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
      console.error('Error parsing content optimization:', error)
    }

    // Fallback optimization
    return {
      optimizedTitle: content.title,
      optimizedDescription: content.description,
      optimizedTags: content.tags,
      changes: ['No changes applied'],
      reasoning: 'Optimization failed, content returned as-is',
    }
  }

  /**
   * Private helper method for optimization strategies
   */
  private getOptimizationStrategies(goal: string): string {
    const strategies = {
      views: `
      - Use high-CTR title formats with curiosity gaps
      - Include trending keywords and search terms
      - Create urgency or timeliness in title
      - Optimize for search discovery
      - Use proven clickable phrases
      `,
      engagement: `
      - Ask questions in title and description
      - Create controversy or debate topics
      - Use emotional triggers and strong language
      - Include call-to-actions for comments
      - Design for shareability
      `,
      retention: `
      - Promise specific value or transformation
      - Use step-by-step or numbered formats
      - Create curiosity loops and cliffhangers
      - Segment content clearly in description
      - Optimize for binge-watching
      `,
      subscribers: `
      - Position as authority content
      - Use series or episodic formats
      - Create community around content
      - Include strong channel branding
      - Design for repeat viewing
      `,
    }

    return strategies[goal as keyof typeof strategies] || strategies.views
  }
}
