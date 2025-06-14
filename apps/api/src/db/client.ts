import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import * as schema from './schema'
import * as schemaMVP from './schema-mvp'
import { getEnv } from '../types/env'

const env = getEnv()

// Create postgres connection
const queryClient = postgres(env.DATABASE_URL, {
  max: parseInt(env.DATABASE_POOL_SIZE || '10', 10),
  idle_timeout: 20,
  connect_timeout: 10,
})

// Combine schemas
const combinedSchema = { ...schema, ...schemaMVP }

// Create drizzle instance
export const db = drizzle(queryClient, {
  schema: combinedSchema,
  logger: env.NODE_ENV === 'development',
})

// Export schemas for convenience
export * from './schema'
export * from './schema-mvp'

// Helper to close database connection
export async function closeDb() {
  await queryClient.end()
}
