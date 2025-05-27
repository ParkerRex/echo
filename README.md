# Echo - AI YouTube Video Metadata Generator

## Overview

Echo helps users automatically generate metadata for YouTube videos (titles, subtitles, chapters, descriptions) using Google Gemini AI.

### Key Features
- 🎥 **Video Upload & Processing** - Upload videos and get AI-generated metadata
- 🤖 **AI-Powered Analysis** - Uses Google Gemini for transcription and content analysis  
- 🔐 **Secure Authentication** - Supabase auth with user data isolation
- ☁️ **Cloud Storage** - Google Cloud Storage for video files
- 📱 **Modern UI** - React frontend with TanStack Router

## Quick Start

### Prerequisites
- Python 3.10+ with [uv](https://github.com/astral-sh/uv)
- Node.js 18+ with [pnpm](https://pnpm.io/)
- [Supabase CLI](https://supabase.com/docs/guides/cli)
- Docker (for local Supabase)

### Setup

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd echo
cp .env.example .env
# Edit .env with your configuration
```

2. **Install dependencies:**
```bash
pnpm install
pnpm setup:python-env
```

3. **Start development environment:**
```bash
pnpm dev
```

That's it! This single command starts:
- Local Supabase database
- Python FastAPI backend (port 8000)
- TypeScript frontend (port 3000)

Visit `http://localhost:3000` to access the application.

## Architecture

```mermaid
graph TD
  A[React + TanStack Router] -->|calls| B(Supabase Auth)
  A -->|calls| C[FastAPI Backend]
  A -->|calls| D[Supabase DB]
  C -->|generates| E[Google Cloud Storage Signed URLs]
  C -->|processes with| F[Gemini (via Vertex AI)]
  C -->|writes metadata to| D
  A -->|fetches metadata from| D
```

### Tech Stack
- **Backend**: FastAPI with Python 3.10+
- **Frontend**: React with TanStack Router
- **Database**: PostgreSQL via Supabase
- **Storage**: Google Cloud Storage
- **AI**: Google Gemini via Vertex AI
- **Auth**: Supabase Auth

## User Workflow

1. **Upload Video** - User uploads video file through the web interface
2. **Processing** - FastAPI extracts audio and sends to Gemini for analysis
3. **AI Generation** - Gemini generates title, description, transcript, and chapters
4. **Results** - User views and can edit the generated metadata

## Documentation

For detailed information, see our comprehensive documentation:

- **[Developer Guide](./DEVELOPER_GUIDE.md)** - Complete development setup, architecture, and workflows
- **[Database Documentation](./DATABASE.md)** - Schema, migrations, and database management
- **[API Reference](./DEVELOPER_GUIDE.md#api-reference)** - Complete API endpoint documentation

## Development Commands

```bash
# Essential commands
pnpm dev                    # Start entire development environment
pnpm build                  # Build all applications
pnpm test                   # Run all tests and quality checks

# Database operations
pnpm db:start              # Start Supabase
pnpm db:stop               # Stop Supabase
pnpm db:push               # Push schema changes
pnpm db:reset              # Reset database

# Type generation
pnpm gen:types             # Generate all types
pnpm gen:types:supabase    # Generate Supabase types only

# Quality checks
pnpm typecheck             # Type check all applications
pnpm lint                  # Lint all applications
pnpm format                # Format all applications

# Targeted development
pnpm dev:web               # Frontend only
pnpm dev:core              # Backend only
```

## Project Structure

```
echo/
├── apps/
│   ├── core/           # FastAPI Backend
│   └── web/            # React Frontend
├── packages/
│   ├── db/             # Database utilities
│   └── supabase/       # Supabase configuration and migrations
├── DEVELOPER_GUIDE.md  # Comprehensive development documentation
├── DATABASE.md         # Database schema and management
└── README.md          # This file
```

## Contributing

1. Follow the development guidelines in [`.cursor/rules/`](./.cursor/rules/)
2. Run tests before submitting PRs
3. Use the provided scripts for database and type generation
4. Refer to the [Developer Guide](./DEVELOPER_GUIDE.md) for detailed workflows

## License

[Add your license information here]
