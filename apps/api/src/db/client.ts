import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import * as schema from './schema'
import * as schemaMVP from './schema-mvp'
import { getEnv } from '../types/env'
import { circuitBreakers } from '../lib/circuit-breaker'
import { retryDatabase } from '../lib/retry'
import { withDatabaseTimeout } from '../lib/timeout'

const env = getEnv()

// Enhanced postgres connection with better config
const queryClient = postgres(env.DATABASE_URL, {
  max: parseInt(env.DATABASE_POOL_SIZE || '20', 10), // Increased pool size
  idle_timeout: 20,
  connect_timeout: 10,
  max_lifetime: 60 * 30, // 30 minutes
  prepare: false, // Disable prepared statements for better compatibility
  transform: postgres.camel, // Convert snake_case to camelCase
  onnotice: env.NODE_ENV === 'development' ? console.log : undefined,
  debug: env.NODE_ENV === 'development' ? console.log : undefined,
})

// Combine schemas
const combinedSchema = { ...schema, ...schemaMVP }

// Create drizzle instance with enhanced logging
export const db = drizzle(queryClient, {
  schema: combinedSchema,
  logger: env.NODE_ENV === 'development' ? {
    logQuery: (query, params) => {
      console.log('[DB QUERY]', { query, params })
      // Record metrics
      try {
        import('../lib/health').then(({ metrics }) => {
          const start = performance.now()
          // We'll track this in the actual query execution
        })
      } catch (error) {
        // Ignore metrics errors
      }
    }
  } : false,
})

// Wrap database operations with reliability patterns
export const reliableDb = {
  ...db,
  // Override execute method to add circuit breaker, retry, and timeout
  async execute(query: any): Promise<any> {
    const start = performance.now()
    
    try {
      const result = await circuitBreakers.database.execute(async () => {
        return await withDatabaseTimeout(
          retryDatabase(() => db.execute(query)),
          'query'
        )
      })
      
      // Record successful query metrics
      try {
        const { metrics } = await import('../lib/health')
        metrics.recordDbQuery(performance.now() - start, true)
      } catch (error) {
        // Ignore metrics errors
      }
      
      return result
    } catch (error) {
      // Record failed query metrics
      try {
        const { metrics } = await import('../lib/health')
        metrics.recordDbQuery(performance.now() - start, false)
      } catch (metricsError) {
        // Ignore metrics errors
      }
      
      console.error('[DB ERROR]', {
        query: query?.sql || 'unknown',
        error: error instanceof Error ? error.message : error,
        duration: performance.now() - start
      })
      
      throw error
    }
  }
}

// Export schemas for convenience
export * from './schema'
export {
  // Re-export MVP schema items
  ideas,
  generatedContent,
  competitors,
  competitorVideos,
  youtubeCredentials,
  publishedVideos,
  contentSources,
  ideaEmbeddings,
  // Relations
  ideasRelations,
  generatedContentRelations,
  competitorsRelations,
  competitorVideosRelations,
  youtubeCredentialsRelations,
  publishedVideosRelations,
  contentSourcesRelations,
  ideaEmbeddingsRelations,
  // Types
  type Idea,
  type NewIdea,
  type GeneratedContent,
  type NewGeneratedContent,
  type Competitor,
  type NewCompetitor,
  type CompetitorVideo,
  type NewCompetitorVideo,
  type PublishedVideo,
  type NewPublishedVideo,
  type ContentSource,
  type NewContentSource,
  type IdeaEmbedding,
  type NewIdeaEmbedding
} from './schema-mvp'

// Database health and management functions
export async function checkDatabaseHealth(): Promise<boolean> {
  try {
    await withDatabaseTimeout(
      db.execute('SELECT 1 as health_check'),
      'query'
    )
    return true
  } catch (error) {
    console.error('[DB HEALTH]', 'Health check failed:', error)
    return false
  }
}

export async function getDatabaseStats() {
  try {
    const [connectionStats] = await db.execute(`
      SELECT 
        sum(numbackends) as active_connections,
        sum(xact_commit) as transactions_committed,
        sum(xact_rollback) as transactions_rolled_back,
        sum(blks_read) as blocks_read,
        sum(blks_hit) as blocks_hit
      FROM pg_stat_database 
      WHERE datname = current_database()
    `)
    
    return connectionStats
  } catch (error) {
    console.error('[DB STATS]', 'Failed to get database stats:', error)
    return null
  }
}

// Graceful shutdown helper
export async function closeDb() {
  try {
    console.log('[DB]', 'Closing database connections...')
    await queryClient.end({ timeout: 5 })
    console.log('[DB]', 'Database connections closed successfully')
  } catch (error) {
    console.error('[DB]', 'Error closing database connections:', error)
  }
}

// Handle process termination
let isShuttingDown = false

process.on('SIGTERM', async () => {
  if (!isShuttingDown) {
    isShuttingDown = true
    console.log('[DB]', 'Received SIGTERM, closing database connections...')
    await closeDb()
    process.exit(0)
  }
})

process.on('SIGINT', async () => {
  if (!isShuttingDown) {
    isShuttingDown = true
    console.log('[DB]', 'Received SIGINT, closing database connections...')
    await closeDb()
    process.exit(0)
  }
})
