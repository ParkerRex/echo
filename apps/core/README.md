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
# Run database migrations
bun db:migrate

# Start development server
bun dev

# Run tests
bun test

# Type checking
bun typecheck

# Linting
bun lint
```

### Project Structure

```
src/
├── index.ts           # Main server entry
├── context.ts         # tRPC context
├── trpc.ts           # tRPC setup
├── db/               # Database
│   ├── client.ts     # Drizzle client
│   ├── schema.ts     # Database schema
│   └── migrations/   # SQL migrations
├── routers/          # tRPC routers
│   ├── auth.router.ts
│   ├── user.router.ts
│   ├── video.router.ts
│   ├── jobs.router.ts
│   └── chat.router.ts
├── services/         # Business logic
│   ├── ai.service.ts
│   ├── storage.service.ts
│   └── video-processing.ts
├── lib/              # Utilities
│   ├── auth/         # Authentication
│   └── utils/        # Helpers
├── middleware/       # Hono middleware
└── types/           # TypeScript types
```

## API Routes

### tRPC Procedures

All API endpoints are available under `/trpc/*` and are fully typed.

#### Auth
- `auth.signIn` - Sign in with email/password
- `auth.signUp` - Create new account
- `auth.signOut` - Sign out
- `auth.resetPassword` - Request password reset

#### Videos
- `video.upload` - Upload a video
- `video.list` - List user's videos
- `video.getById` - Get video details
- `video.delete` - Delete a video

#### Jobs
- `jobs.list` - List processing jobs
- `jobs.getById` - Get job details
- `jobs.cancel` - Cancel a job
- `jobs.retry` - Retry failed job

#### Chat
- `chat.create` - Create new chat
- `chat.list` - List chats
- `chat.sendMessage` - Send message
- `chat.streamMessage` - Stream AI response

#### User
- `user.me` - Get current user
- `user.update` - Update profile
- `user.stats` - Get user statistics

## Environment Variables

See `.env.example` for all required environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_JWT_SECRET` - JWT secret for auth
- `GEMINI_API_KEY` - Google AI API key

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

### Production Build

```bash
# Build for production
bun build

# Start production server
bun start
```

## Migration from FastAPI

This is a complete rewrite from Python/FastAPI to TypeScript/Hono:

1. **Endpoints → tRPC Procedures**: REST endpoints are now type-safe tRPC procedures
2. **SQLAlchemy → Drizzle**: Database queries use Drizzle ORM
3. **Pydantic → Zod**: Runtime validation with Zod schemas
4. **FastAPI Dependencies → tRPC Context**: Shared dependencies via context

## License

MIT