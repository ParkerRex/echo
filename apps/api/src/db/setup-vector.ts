import 'dotenv/config'
import postgres from 'postgres'

async function setupVector() {
  console.log('🚀 Setting up pgvector extension...')

  const connectionString = process.env.DATABASE_URL!
  const sql = postgres(connectionString, { max: 1 })

  try {
    // Enable vector extension
    await sql`CREATE EXTENSION IF NOT EXISTS vector;`
    console.log('✅ pgvector extension enabled!')

    // Check if extension is available
    const extensions = await sql`SELECT * FROM pg_available_extensions WHERE name = 'vector';`
    console.log('Vector extension info:', extensions)
  } catch (error) {
    console.error('❌ Failed to setup vector extension:', error)
    process.exit(1)
  }

  await sql.end()
  process.exit(0)
}

setupVector()
