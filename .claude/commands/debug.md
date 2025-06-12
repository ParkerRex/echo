# Debug Commands

Common debugging commands and workflows for the Echo project.

## Backend Debugging

### Server Health Check
```bash
# Check if API server is running
curl http://localhost:8000/

# Check tRPC endpoint
curl http://localhost:8000/trpc/
```

### Database Debugging
```bash
# Check database connection
bun db:start

# Open Drizzle Studio for database exploration
cd apps/core && bun db:studio

# View migration status
cd packages/supabase && supabase migration list

# Check database schema
cd packages/supabase && supabase db diff
```

### Logs and Monitoring
```bash
# View API server logs
cd apps/core && bun dev

# View detailed request logs
# Logs automatically include request IDs for tracing

# Check environment variables
cd apps/core && bun run src/types/env.ts
```

## Frontend Debugging

### Next.js Development
```bash
# Start with verbose logging
cd apps/website && NEXT_DEBUG=1 bun dev

# Build and analyze bundle
cd apps/website && bun build && bun analyze
```

### tRPC Client Debugging
```bash
# Enable tRPC logging in development
# Add to your component:
# const utils = api.useUtils()
# console.log('tRPC context:', utils)
```

## Environment Issues

### Missing Environment Variables
```bash
# Check required variables
grep -E "^[A-Z_]+=" .env.example

# Validate environment in backend
cd apps/core && bun run -e "import('./src/types/env.js').then(m => m.validateEnv())"
```

### Supabase Connection Issues
```bash
# Check Supabase status
cd packages/supabase && supabase status

# Restart Supabase
bun db:stop && bun db:start

# Reset Supabase database
bun db:reset
```

## Performance Debugging

### Bundle Analysis
```bash
# Analyze frontend bundle
cd apps/website && bun build && bun analyze

# Check backend performance
cd apps/core && bun --inspect dev
```

### Database Performance
```bash
# View slow queries in Drizzle Studio
cd apps/core && bun db:studio

# Check database indexes
cd packages/supabase && supabase db diff --schema public
```

## Testing and Quality

### Type Checking Issues
```bash
# Check types across all packages
bun typecheck

# Check specific package
cd apps/core && bun typecheck
cd apps/website && bun typecheck
```

### Linting and Formatting
```bash
# Fix linting issues
bun lint
bun format

# Check specific package
cd apps/core && bun check
```

## Common Error Solutions

### "Module not found" errors
```bash
# Clear all caches and reinstall
bun clean && bun install

# Check package resolution
bun run --bun node_modules/.bin/tsc --showConfig
```

### tRPC type errors
```bash
# Regenerate tRPC types
cd apps/core && bun typecheck
cd apps/website && bun typecheck

# Check router exports
cd apps/core && bun run -e "console.log(Object.keys(require('./src/routers/index.js')))"
```

### Database connection errors
```bash
# Check Supabase connection
cd packages/supabase && supabase db ping

# Verify environment variables
echo $SUPABASE_URL
echo $DATABASE_URL
```

### Build errors
```bash
# Clean build artifacts
bun clean

# Clear Next.js cache
cd apps/website && rm -rf .next

# Clear Turbo cache
rm -rf .turbo
```

## Debug Tools

### Browser DevTools
- React DevTools for component debugging
- Network tab for API calls
- Console for client-side errors
- Performance tab for optimization

### VS Code Extensions
- TypeScript Hero for import management
- Prettier for code formatting
- ESLint for code quality
- Thunder Client for API testing

### Useful Commands
```bash
# Monitor file changes
watch -n 1 'find . -name "*.ts" -o -name "*.tsx" | wc -l'

# Check port usage
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :54321 # Supabase

# Memory usage
ps aux | grep node
ps aux | grep bun
```