import { GoogleGenerativeAI } from '@google/generative-ai'
import { getEnv } from '../types/env'

const env = getEnv()

export interface ChatContext {
  videoTitle?: string
  videoDescription?: string
  transcript?: string
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

export class AIService {
  private genAI: GoogleGenerativeAI
  private model: any
  private imagenModel: any

  constructor() {
    this.genAI = new GoogleGenerativeAI(env.GEMINI_API_KEY)
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' })
    this.imagenModel = this.genAI.getGenerativeModel({ model: 'imagen-3' })
  }

  /**
   * Transcribe audio to text
   */
  async transcribeAudio(audioUrl: string): Promise<string> {
    // In a real implementation, this would use a speech-to-text service
    // For now, we'll use Gemini with audio capabilities when available
    // or integrate with services like Whisper API
    
    // Placeholder implementation
    console.log('Transcribing audio from:', audioUrl)
    
    // You would typically:
    // 1. Download the audio file
    // 2. Send to transcription service
    // 3. Return the transcript
    
    return 'This is a placeholder transcript. In production, integrate with Whisper API or similar service.'
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
  async generateVideoMetadata(transcript: string, fileName: string): Promise<{
    titles: string[]
    description: string
    tags: string[]
  }> {
    const prompt = `
      Based on the following video transcript and filename, generate:
      1. 10 different catchy, SEO-friendly YouTube titles (each max 60 characters)
         - Mix different styles: how-to, listicle, question, emotional, etc.
         - Include relevant keywords
         - Make them clickable and engaging
      2. A comprehensive description (150-300 words)
      3. Relevant tags (10-15 tags)
      
      Filename: ${fileName}
      Transcript: ${transcript.substring(0, 1500)}...
      
      Return the response in JSON format:
      {
        "titles": [
          "Title 1",
          "Title 2",
          ...10 titles total
        ],
        "description": "...",
        "tags": ["tag1", "tag2", ...]
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
            parsed.titles.push(`${fileName.replace(/\.[^/.]+$/, '')} - Part ${parsed.titles.length + 1}`.substring(0, 60))
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
  async generateChatResponse(
    message: string,
    context: ChatContext
  ): Promise<ChatResponse> {
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
  async *streamChatResponse(
    message: string,
    context: ChatContext
  ): AsyncGenerator<StreamChunk> {
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

    return 'Recent conversation:\n' + 
      messages
        .slice(-5) // Last 5 messages
        .map(msg => `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`)
        .join('\n')
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
        const index = parseInt(lines[0])
        const [startTime, endTime] = lines[1].split(' --> ')
        const text = lines.slice(2).join('\n')

        entries.push({
          index,
          startTime: startTime.trim(),
          endTime: endTime.trim(),
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
      .map(topic => topic.trim())
      .filter(topic => topic.length > 0)
  }

  /**
   * Generate thumbnail backgrounds using Google Imagen 3
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
      'vibrant gradient background with abstract shapes',
      'cinematic dramatic lighting with depth',
      'minimalist modern design with bold colors',
      'dynamic energy with motion blur effects',
    ]

    try {
      for (let i = 0; i < count; i++) {
        const prompt = `
          Create a YouTube thumbnail background image for a video titled "${videoTitle}".
          Style: ${styles[i % styles.length]}
          Topics: ${topics.slice(0, 3).join(', ')}
          
          Requirements:
          - 16:9 aspect ratio (1920x1080)
          - High contrast and eye-catching
          - Leave space for text overlay
          - Professional and engaging
          - No text in the image
          - Suitable for ${topics[0] || 'general'} content
        `

        // Note: This is a placeholder for Imagen 3 API
        // In production, you would use the actual Imagen 3 API endpoint
        // For now, we'll generate a placeholder URL
        const placeholderUrl = `https://picsum.photos/seed/${videoTitle}-${i}/1920/1080`
        thumbnailUrls.push(placeholderUrl)
        
        // In production with real Imagen 3:
        // const result = await this.imagenModel.generateImage({
        //   prompt,
        //   numberOfImages: 1,
        //   aspectRatio: '16:9',
        // })
        // thumbnailUrls.push(result.images[0].url)
      }
    } catch (error) {
      console.error('Failed to generate thumbnails:', error)
      // Return placeholder thumbnails on error
      for (let i = thumbnailUrls.length; i < count; i++) {
        thumbnailUrls.push(`https://picsum.photos/seed/fallback-${i}/1920/1080`)
      }
    }

    return thumbnailUrls
  }
}