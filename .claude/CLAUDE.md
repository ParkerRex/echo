# Echo Development Guidelines

## Package Manager & Runtime
- **Always use Bun** instead of npm, yarn, or pnpm
- All scripts and tests should use Bun runtime
- Use `bun run` for script execution
- Use `bun test` for testing

## Architecture Overview
Echo uses a modern TypeScript monorepo with:
- **Backend**: Hono + tRPC + Drizzle ORM
- **Frontend**: Next.js + tRPC client
- **Database**: PostgreSQL via Supabase
- **Build System**: Turbo monorepo

## Type System Guidelines

**Avoid using `any`. Here's how to use our type system correctly:**

### Use Drizzle Types When:
- Writing backend database queries and mutations
- Creating or modifying database schema definitions
- Implementing repository patterns and data access layers
- Building complex business logic that interacts with the database
- Working with database transactions and migrations

### Use tRPC Types When:
- Creating API procedures (queries and mutations)
- Building frontend components that call the API
- Implementing form submissions and data fetching
- Type-safe API calls between frontend and backend
- All client-server communication

### Use Supabase Types When:
- Working directly with Supabase client for auth
- Implementing authentication flows and user management
- Using Supabase storage for file operations
- Setting up real-time subscriptions
- Database type generation (`bun gen:types:db`)

### Use Zod Schemas When:
- Validating user input in forms and API endpoints
- Defining runtime validation for tRPC procedures
- Creating type-safe environment variable validation
- Transforming and parsing external data
- API input/output validation

## Development Workflow

### Database-First Development:
1. **Design schema changes** in Drizzle schema files
2. **Generate migrations** using `bun db:push`
3. **Update types** with `bun gen:types:db`
4. **Implement backend** using generated Drizzle types
5. **Create tRPC procedures** with proper Zod validation
6. **Build frontend** using tRPC client types

### Testing Requirements:
- Write unit tests for all services and utilities
- Create integration tests for tRPC procedures
- Use Bun's built-in test runner
- Mock external dependencies (Supabase, AI services)
- Test error handling and edge cases

### Code Quality Standards:
- All code must pass TypeScript type checking (`bun typecheck`)
- Use Biome for linting and formatting (`bun lint`, `bun format`)
- Follow tRPC best practices for procedure organization
- Use proper error handling with tRPC error codes
- Implement proper logging and monitoring