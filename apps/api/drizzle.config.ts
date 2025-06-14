import * as dotenv from 'dotenv'
import type { Config } from 'drizzle-kit'

// Load environment variables
dotenv.config()

export default {
  schema: ['./src/db/schema.ts', './src/db/schema-mvp.ts'],
  out: './src/db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
} satisfies Config
