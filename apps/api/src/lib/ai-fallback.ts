/**
 * AI Service Graceful Degradation and Fallback System
 * 
 * Provides fallback mechanisms when AI services fail,
 * ensuring the application continues to function even
 * when external AI providers are unavailable.
 */

import { circuitBreakers } from './circuit-breaker'
import { retryExternalAPI } from './retry'
import { withAITimeout } from './timeout'

export interface AIServiceConfig {
  name: string
  priority: number  // Lower number = higher priority
  isAvailable: () => Promise<boolean>
  cost: number      // Relative cost (1 = cheapest, 10 = most expensive)
  capabilities: AICapability[]
}

export enum AICapability {
  TEXT_GENERATION = 'text_generation',
  TITLE_GENERATION = 'title_generation',
  DESCRIPTION_GENERATION = 'description_generation',
  KEYWORD_EXTRACTION = 'keyword_extraction',
  SENTIMENT_ANALYSIS = 'sentiment_analysis',
  CONTENT_CLASSIFICATION = 'content_classification',
  TRANSLATION = 'translation',
  SUMMARIZATION = 'summarization',
}

export interface AIRequest {
  capability: AICapability
  input: any
  options?: {
    maxRetries?: number
    timeout?: number
    preferredService?: string
    fallbackToCache?: boolean
  }
}

export interface AIResponse<T = any> {
  result: T
  service: string
  confidence: number
  cached: boolean
  degraded: boolean
  fallbackUsed: boolean
  processingTime: number
}

export interface FallbackStrategy {
  useCache: boolean
  useBasicAlgorithm: boolean
  useHumanGenerated: boolean
  gracefulFailure: boolean
}

// Cache for AI responses
const responseCache = new Map<string, { result: any; timestamp: number; ttl: number }>()

// Basic fallback algorithms
const fallbackAlgorithms = {
  [AICapability.TEXT_GENERATION]: (content: string): string => {
    // Simple text generation - return first paragraph
    const paragraphs = content.split(/\n\s*\n/)
    return paragraphs[0]?.trim() || 'Content generated successfully'
  },

  [AICapability.TITLE_GENERATION]: (content: string): string[] => {
    // Simple title generation based on content analysis
    const words = content.toLowerCase().split(/\s+/)
    const commonWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    const importantWords = words.filter(word => 
      word.length > 3 && !commonWords.includes(word)
    ).slice(0, 5)
    
    const title = importantWords
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
    
    return [
      title,
      `How to ${title}`,
      `The Ultimate Guide to ${title}`,
      `${title}: Everything You Need to Know`,
      `Amazing ${title} Tips and Tricks`
    ]
  },

  [AICapability.DESCRIPTION_GENERATION]: (content: string): string => {
    // Basic description generation
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0)
    const firstFew = sentences.slice(0, 2).join('. ')
    return firstFew.length > 160 ? firstFew.substring(0, 157) + '...' : firstFew
  },

  [AICapability.KEYWORD_EXTRACTION]: (content: string): string[] => {
    // Simple keyword extraction
    const words = content.toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 3)
    
    const wordFreq = words.reduce((acc, word) => {
      acc[word] = (acc[word] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    return Object.entries(wordFreq)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([word]) => word)
  },

  [AICapability.SENTIMENT_ANALYSIS]: (content: string): { sentiment: string; confidence: number } => {
    // Basic sentiment analysis
    const positiveWords = ['good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'best', 'fantastic']
    const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting']
    
    const words = content.toLowerCase().split(/\s+/)
    const positiveCount = words.filter(word => positiveWords.includes(word)).length
    const negativeCount = words.filter(word => negativeWords.includes(word)).length
    
    if (positiveCount > negativeCount) {
      return { sentiment: 'positive', confidence: 0.6 }
    } else if (negativeCount > positiveCount) {
      return { sentiment: 'negative', confidence: 0.6 }
    } else {
      return { sentiment: 'neutral', confidence: 0.5 }
    }
  },

  [AICapability.SUMMARIZATION]: (content: string): string => {
    // Basic summarization (take first and last sentences from each paragraph)
    const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim().length > 0)
    const summaryParts = paragraphs.map(paragraph => {
      const sentences = paragraph.split(/[.!?]+/).filter(s => s.trim().length > 0)
      if (sentences.length === 1) return sentences[0]
      if (sentences.length === 2) return sentences.join('. ')
      return sentences[0] + '. ' + sentences[sentences.length - 1]
    })
    
    return summaryParts.join('\n\n')
  }
}

// Human-generated templates for common scenarios
const humanTemplates = {
  [AICapability.TEXT_GENERATION]: {
    default: [
      "Generated content will be available shortly.",
      "Content is being processed.",
      "Please check back for updated content."
    ]
  },
  
  [AICapability.TITLE_GENERATION]: {
    default: [
      "Amazing Video You Need to Watch",
      "This Will Change Everything",
      "You Won't Believe What Happens Next",
      "The Truth About [Topic]",
      "Ultimate Guide to [Topic]"
    ],
    tutorial: [
      "How to [Action] in [Time]",
      "Step by Step [Action] Guide", 
      "Learn [Skill] Today",
      "Master [Topic] Fast",
      "Complete [Topic] Tutorial"
    ],
    review: [
      "[Product] Review: Is It Worth It?",
      "My Honest [Product] Review",
      "[Product] vs [Competitor]: Which is Better?",
      "Testing [Product] for [Duration]",
      "Why I Love/Hate [Product]"
    ]
  }
}

export class AIFallbackManager {
  private services: Map<string, AIServiceConfig> = new Map()
  private fallbackStrategy: FallbackStrategy = {
    useCache: true,
    useBasicAlgorithm: true,
    useHumanGenerated: true,
    gracefulFailure: true
  }

  constructor() {
    this.registerDefaultServices()
  }

  private registerDefaultServices() {
    // Register OpenAI
    this.services.set('openai', {
      name: 'OpenAI',
      priority: 1,
      cost: 8,
      capabilities: [
        AICapability.TEXT_GENERATION,
        AICapability.TITLE_GENERATION,
        AICapability.DESCRIPTION_GENERATION,
        AICapability.KEYWORD_EXTRACTION,
        AICapability.SENTIMENT_ANALYSIS,
        AICapability.CONTENT_CLASSIFICATION,
        AICapability.SUMMARIZATION
      ],
      isAvailable: async () => {
        return circuitBreakers.openai.getStats().state !== 'OPEN'
      }
    })

    // Register Anthropic
    this.services.set('anthropic', {
      name: 'Anthropic',
      priority: 2,
      cost: 7,
      capabilities: [
        AICapability.TEXT_GENERATION,
        AICapability.TITLE_GENERATION,
        AICapability.DESCRIPTION_GENERATION,
        AICapability.SUMMARIZATION
      ],
      isAvailable: async () => {
        return circuitBreakers.anthropic.getStats().state !== 'OPEN'
      }
    })
  }

  async processRequest<T>(request: AIRequest): Promise<AIResponse<T>> {
    const startTime = performance.now()
    const cacheKey = this.generateCacheKey(request)

    // Try cache first if enabled
    if (request.options?.fallbackToCache !== false && this.fallbackStrategy.useCache) {
      const cached = this.getFromCache<T>(cacheKey)
      if (cached) {
        return {
          result: cached,
          service: 'cache',
          confidence: 0.9,
          cached: true,
          degraded: false,
          fallbackUsed: false,
          processingTime: performance.now() - startTime
        }
      }
    }

    // Get available services for this capability
    const availableServices = await this.getAvailableServices(request.capability)
    
    // Sort by priority and cost
    availableServices.sort((a, b) => {
      if (a.priority !== b.priority) return a.priority - b.priority
      return a.cost - b.cost
    })

    // Try preferred service first if specified
    if (request.options?.preferredService) {
      const preferred = availableServices.find(s => s.name === request.options?.preferredService)
      if (preferred) {
        availableServices.unshift(preferred)
      }
    }

    // Try each service
    for (const service of availableServices) {
      try {
        const result = await this.callAIService<T>(service, request)
        
        // Cache successful result
        if (this.fallbackStrategy.useCache) {
          this.cacheResult(cacheKey, result, 3600000) // 1 hour TTL
        }

        return {
          result,
          service: service.name,
          confidence: 0.95,
          cached: false,
          degraded: false,
          fallbackUsed: false,
          processingTime: performance.now() - startTime
        }
      } catch (error) {
        console.warn(`[AI FALLBACK] ${service.name} failed:`, error)
        continue
      }
    }

    // All AI services failed, try fallback strategies
    return this.useFallbackStrategy<T>(request, startTime)
  }

  private async getAvailableServices(capability: AICapability): Promise<AIServiceConfig[]> {
    const services: AIServiceConfig[] = []
    
    for (const service of this.services.values()) {
      if (service.capabilities.includes(capability)) {
        try {
          const isAvailable = await service.isAvailable()
          if (isAvailable) {
            services.push(service)
          }
        } catch (error) {
          // Service availability check failed, skip it
        }
      }
    }
    
    return services
  }

  private async callAIService<T>(service: AIServiceConfig, request: AIRequest): Promise<T> {
    // This would integrate with the actual AI service
    // For now, we'll simulate it
    const circuitBreaker = circuitBreakers[service.name.toLowerCase() as keyof typeof circuitBreakers]
    
    if (circuitBreaker) {
      return await circuitBreaker.execute(async () => {
        return await withAITimeout(
          retryExternalAPI(() => this.makeAICall<T>(service, request)),
          'standard'
        )
      })
    } else {
      return await withAITimeout(
        retryExternalAPI(() => this.makeAICall<T>(service, request)),
        'standard'
      )
    }
  }

  private async makeAICall<T>(service: AIServiceConfig, request: AIRequest): Promise<T> {
    // This is where you'd integrate with the actual AI service APIs
    // For now, throwing an error to simulate service failure for demo
    throw new Error(`Simulated ${service.name} failure`)
  }

  private async useFallbackStrategy<T>(request: AIRequest, startTime: number): Promise<AIResponse<T>> {
    // Try basic algorithm fallback
    if (this.fallbackStrategy.useBasicAlgorithm) {
      try {
        const algorithms = fallbackAlgorithms as any
        const algorithm = algorithms[request.capability]
        if (algorithm) {
          const result = algorithm(request.input) as T
          return {
            result,
            service: 'basic-algorithm',
            confidence: 0.6,
            cached: false,
            degraded: true,
            fallbackUsed: true,
            processingTime: performance.now() - startTime
          }
        }
      } catch (error) {
        console.warn('[AI FALLBACK] Basic algorithm failed:', error)
      }
    }

    // Try human-generated templates
    if (this.fallbackStrategy.useHumanGenerated) {
      const templates = (humanTemplates as any)[request.capability]
      if (templates) {
        const result = this.selectHumanTemplate(templates, request.input) as T
        return {
          result,
          service: 'human-template',
          confidence: 0.7,
          cached: false,
          degraded: true,
          fallbackUsed: true,
          processingTime: performance.now() - startTime
        }
      }
    }

    // Graceful failure
    if (this.fallbackStrategy.gracefulFailure) {
      const result = this.getGracefulFailureResult<T>(request.capability)
      return {
        result,
        service: 'graceful-failure',
        confidence: 0.3,
        cached: false,
        degraded: true,
        fallbackUsed: true,
        processingTime: performance.now() - startTime
      }
    }

    throw new Error('All AI services and fallback strategies failed')
  }

  private selectHumanTemplate(templates: any, input: string): any {
    // Simple template selection based on input content
    if (typeof templates === 'object' && !Array.isArray(templates)) {
      // Detect content type and select appropriate template
      if (input.includes('how to') || input.includes('tutorial')) {
        return templates.tutorial?.[0] || templates.default?.[0]
      } else if (input.includes('review') || input.includes('test')) {
        return templates.review?.[0] || templates.default?.[0]
      } else {
        return templates.default?.[0]
      }
    }
    
    // If templates is an array, return first item
    if (Array.isArray(templates)) {
      return templates[0]
    }
    
    return templates
  }

  private getGracefulFailureResult<T>(capability: AICapability): T {
    const defaults: Record<AICapability, any> = {
      [AICapability.TITLE_GENERATION]: ['Untitled Video'],
      [AICapability.DESCRIPTION_GENERATION]: 'Video description will be available soon.',
      [AICapability.KEYWORD_EXTRACTION]: ['video', 'content'],
      [AICapability.SENTIMENT_ANALYSIS]: { sentiment: 'neutral', confidence: 0.5 },
      [AICapability.CONTENT_CLASSIFICATION]: 'general',
      [AICapability.TRANSLATION]: 'Translation not available',
      [AICapability.SUMMARIZATION]: 'Summary not available',
      [AICapability.TEXT_GENERATION]: 'Content generation temporarily unavailable'
    }

    return defaults[capability] as T
  }

  private generateCacheKey(request: AIRequest): string {
    const hash = require('crypto').createHash('md5')
    hash.update(JSON.stringify({
      capability: request.capability,
      input: request.input
    }))
    return `ai_cache_${hash.digest('hex')}`
  }

  private getFromCache<T>(key: string): T | null {
    const cached = responseCache.get(key)
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      return cached.result
    }
    responseCache.delete(key)
    return null
  }

  private cacheResult(key: string, result: any, ttl: number): void {
    responseCache.set(key, {
      result,
      timestamp: Date.now(),
      ttl
    })
  }

  // Configuration methods
  setFallbackStrategy(strategy: Partial<FallbackStrategy>): void {
    this.fallbackStrategy = { ...this.fallbackStrategy, ...strategy }
  }

  registerService(id: string, config: AIServiceConfig): void {
    this.services.set(id, config)
  }

  getServiceStats(): Record<string, any> {
    const stats: Record<string, any> = {}
    
    for (const [id, service] of this.services) {
      const circuitBreaker = circuitBreakers[id as keyof typeof circuitBreakers]
      stats[id] = {
        name: service.name,
        priority: service.priority,
        cost: service.cost,
        capabilities: service.capabilities,
        circuitBreaker: circuitBreaker?.getStats() || null
      }
    }
    
    return stats
  }
}

// Export singleton instance
export const aiFallbackManager = new AIFallbackManager()

// Utility function for easy use
export async function processAIRequest<T>(
  capability: AICapability,
  input: any,
  options?: AIRequest['options']
): Promise<AIResponse<T>> {
  return aiFallbackManager.processRequest<T>({
    capability,
    input,
    options
  })
}