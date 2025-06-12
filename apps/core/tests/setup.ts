// Bun automatically loads .env files
// Set test environment
process.env.NODE_ENV = 'test'

// Override certain environment variables for testing
if (process.env.TEST_DATABASE_URL) {
  process.env.DATABASE_URL = process.env.TEST_DATABASE_URL
}