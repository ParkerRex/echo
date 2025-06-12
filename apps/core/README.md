# Echo Core API - Hono + tRPC + Drizzle

A modern, type-safe API built with Hono, tRPC, and Drizzle ORM.

## Architecture

- **Hono**: Lightweight, fast web framework
- **tRPC**: End-to-end typesafe APIs
- **Drizzle**: TypeScript ORM with SQL-like syntax
- **Supabase**: Authentication, storage, and database
- **Zod**: Runtime validation

## Getting Started

### Prerequisites

- Bun 1.0+
- PostgreSQL (via Supabase)
- FFmpeg (for video processing)

### Installation

```bash
# Install dependencies
bun install

# Copy environment variables
cp .env.example .env

# Update .env with your configuration
```

### Development

```bash
# Install dependencies
bun install

# Start development server with auto-reload
bun dev

# Run database migrations
bun db:migrate

# Push schema changes to database
bun db:push

# Open Drizzle Studio for database exploration
bun db:studio

# Run tests
bun test

# Run tests with coverage
bun test:coverage

# Type checking
bun typecheck

# Linting and formatting
bun lint
bun format

# Combined checks
bun check
```

### Project Structure

```
src/
├── index.ts           # Main Hono server entry
├── context.ts         # tRPC context creation
├── trpc.ts           # tRPC setup
├── db/               # Database layer
│   ├── client.ts     # Drizzle client
│   ├── schema.ts     # Drizzle schema definitions
│   ├── migrate.ts    # Migration runner
│   └── migrations/   # SQL migration files
├── routers/          # tRPC routers
│   ├── index.ts      # Main router aggregation
│   ├── auth.router.ts
│   ├── user.router.ts
│   ├── video.router.ts
│   ├── video.router.improved.ts
│   ├── jobs.router.ts
│   ├── chat.router.ts
│   ├── analytics.router.ts
│   └── webhook.router.ts
├── services/         # Business logic services
│   ├── ai.service.ts
│   ├── storage.service.ts
│   └── video-processing.ts
├── lib/              # Utilities and adapters
│   ├── auth/         # Supabase authentication
│   ├── ai/           # AI service adapters
│   ├── storage/      # Storage abstractions
│   ├── utils/        # General utilities
│   ├── errors.ts     # Error handling
│   └── validation.ts # Zod schemas
├── middleware/       # Hono middleware
│   ├── auth.ts       # Authentication middleware
│   ├── error.ts      # Error handling
│   ├── logging.ts    # Request logging
│   └── rateLimit.ts  # Rate limiting
├── types/           # TypeScript type definitions
│   └── env.ts        # Environment validation
└── tests/           # Test files
    ├── setup.ts      # Test configuration
    └── routers/      # Router tests
```

## API Routes

### tRPC Procedures

All API endpoints are available under `/trpc/*` and are fully typed.

#### Auth
- `auth.signIn` - Sign in with email/password
- `auth.signUp` - Create new account
- `auth.signOut` - Sign out
- `auth.getSession` - Get current session
- `auth.resetPassword` - Request password reset

#### Videos (Improved Router)
- `video.upload` - Upload a video with metadata
- `video.list` - List user's videos with pagination
- `video.getById` - Get video details with metadata
- `video.updateMetadata` - Update video metadata
- `video.delete` - Delete a video and associated data
- `video.getUploadUrl` - Get signed upload URL

#### Jobs
- `jobs.list` - List processing jobs with filters
- `jobs.getById` - Get job details and status
- `jobs.cancel` - Cancel a running job
- `jobs.retry` - Retry failed job
- `jobs.getHistory` - Get job execution history

#### Chat
- `chat.create` - Create new chat session
- `chat.list` - List user's chat sessions
- `chat.sendMessage` - Send message to AI
- `chat.streamMessage` - Stream AI response
- `chat.getHistory` - Get chat message history

#### User
- `user.me` - Get current user profile
- `user.update` - Update user profile
- `user.getStats` - Get usage statistics
- `user.getPreferences` - Get user preferences

#### Analytics
- `analytics.getOverview` - Get dashboard overview
- `analytics.getUsage` - Get usage metrics
- `analytics.getPerformance` - Get performance data

#### Webhooks
- `webhook.stripe` - Handle Stripe webhook events
- `webhook.youtube` - Handle YouTube webhook events

## Environment Variables

See `.env.example` for all required environment variables:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `SUPABASE_JWT_SECRET` - JWT secret for auth validation
- `GEMINI_API_KEY` - Google AI API key

**Optional:**
- `NODE_ENV` - Environment (development/production)
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)
- `CORS_ORIGINS` - Allowed CORS origins
- `REDIS_URL` - Redis connection for caching
- `STORAGE_BACKEND` - Storage backend (local/gcs)
- `GCS_BUCKET_NAME` - Google Cloud Storage bucket

## Testing

```bash
# Run all tests
bun test

# Run with coverage
bun test:coverage

# Run specific test file
bun test video.router.test.ts
```

## Deployment

### Docker

```bash
# Build image
docker build -t echo-core-api .

# Run container
docker run -p 8000:8000 --env-file .env echo-core-api
```

### Production

```bash
# Build for production
bun run build

# Start production server
bun run start

# Health check
curl http://localhost:8000/

# Check tRPC endpoint
curl http://localhost:8000/trpc/
```

### Docker Support

The API includes Docker support for containerized deployment:

```bash
# Build Docker image
docker build -t echo-core-api .

# Run with environment file
docker run -p 8000:8000 --env-file .env echo-core-api

# Run with docker-compose (if available)
docker-compose up core
```

## Migration from FastAPI

This project has been completely rewritten from Python/FastAPI to TypeScript/Hono:

### Key Changes
1. **REST → tRPC**: Type-safe procedures instead of REST endpoints
2. **SQLAlchemy → Drizzle**: Modern TypeScript ORM with type inference
3. **Pydantic → Zod**: Runtime validation with TypeScript integration
4. **FastAPI Dependencies → tRPC Context**: Dependency injection via context
5. **Python Services → TypeScript Services**: Business logic rewritten in TypeScript

### Benefits
- **End-to-end Type Safety**: From database to frontend
- **Better Developer Experience**: Full IntelliSense and autocomplete
- **Faster Development**: Shared types across the entire stack
- **Modern Tooling**: Better debugging and development tools
- **Unified Language**: Single language (TypeScript) across the stack

## License

MIT