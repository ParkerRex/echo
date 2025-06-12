# FastAPI to Hono Migration Plan

> **⚠️ MIGRATION COMPLETED** - This document is kept for historical reference. The migration from FastAPI to Hono + tRPC was successfully completed in December 2025. See the [CHANGELOG.md](../../CHANGELOG.md) for details.

## 📋 Overview

This document outlined the comprehensive migration plan from FastAPI (Python) to Hono (TypeScript) for the Echo project's API core. The migration modernized the backend while maintaining API compatibility and improving performance.

## 🎯 Goals

- **Modernization**: Move from Python to TypeScript for better type safety and developer experience
- **Performance**: Leverage Hono's lightweight architecture for faster response times
- **Compatibility**: Maintain existing API contracts to avoid breaking frontend integration
- **Maintainability**: Improve code organization and reduce complexity
- **Ecosystem**: Better integration with the existing Node.js/TypeScript ecosystem

## 📊 Current State Analysis

### Existing FastAPI Structure
```
apps/core/
├── main.py                     # FastAPI app entry point
├── api/
│   ├── endpoints.py           # Main API routes (users, chats, messages)
│   └── endpoints/
│       ├── jobs_endpoints.py  # Job processing routes
│       └── video_processing_endpoints.py
├── services/                  # Business logic layer
│   ├── ai_service.py
│   ├── chat_service.py
│   ├── user_service.py
│   ├── job_service.py
│   └── video_processing_service.py
├── models/                    # Data models
├── operations/                # Repository layer
├── lib/                       # Utilities and integrations
└── tests/                     # Test suite
```

### Key Dependencies
- **FastAPI**: Web framework
- **Supabase**: Database and authentication
- **SQLAlchemy**: ORM
- **Google Cloud**: Storage, AI Platform, Secret Manager
- **OpenAI**: AI services
- **Redis**: Caching
- **FFmpeg**: Video processing

### API Endpoints Inventory
1. **Root**: `GET /` - Health check
2. **Upload**: `POST /test/upload` - File upload testing
3. **Users**: `GET /users/{user_id}` - User profile
4. **Chats**: CRUD operations for chat management
5. **Messages**: Message creation and retrieval
6. **Streaming**: Real-time AI chat responses
7. **Jobs**: Video processing job management
8. **Videos**: Video processing endpoints

## 🏗️ Target Hono Architecture

### New TypeScript Structure
```
apps/core/
├── src/
│   ├── index.ts               # Main Hono app
│   ├── routes/
│   │   ├── index.ts          # Route aggregation
│   │   ├── health.ts         # Health check routes
│   │   ├── upload.ts         # File upload routes
│   │   ├── users.ts          # User management
│   │   ├── chats.ts          # Chat functionality
│   │   ├── messages.ts       # Message handling
│   │   ├── streaming.ts      # AI streaming responses
│   │   ├── jobs.ts           # Job processing
│   │   └── videos.ts         # Video processing
│   ├── middleware/
│   │   ├── auth.ts           # Supabase authentication
│   │   ├── cors.ts           # CORS configuration
│   │   ├── logger.ts         # Request logging
│   │   ├── error-handler.ts  # Global error handling
│   │   └── validation.ts     # Request validation
│   ├── services/             # Business logic (converted)
│   │   ├── ai-service.ts
│   │   ├── chat-service.ts
│   │   ├── user-service.ts
│   │   ├── job-service.ts
│   │   └── video-service.ts
│   ├── repositories/         # Data access layer
│   │   ├── chat-repository.ts
│   │   ├── user-repository.ts
│   │   ├── job-repository.ts
│   │   └── video-repository.ts
│   ├── lib/
│   │   ├── database/
│   │   │   ├── supabase.ts   # Supabase client
│   │   │   └── connection.ts # Database utilities
│   │   ├── auth/
│   │   │   ├── middleware.ts # Auth middleware
│   │   │   └── utils.ts      # Auth utilities
│   │   ├── storage/
│   │   │   ├── google-cloud.ts
│   │   │   └── file-upload.ts
│   │   ├── ai/
│   │   │   ├── openai.ts
│   │   │   └── google-ai.ts
│   │   ├── cache/
│   │   │   └── redis.ts
│   │   └── utils/
│   │       ├── validation.ts
│   │       ├── errors.ts
│   │       └── helpers.ts
│   ├── types/
│   │   ├── api.ts            # API request/response types
│   │   ├── database.ts       # Database entity types
│   │   ├── auth.ts           # Authentication types
│   │   ├── services.ts       # Service layer types
│   │   └── external.ts       # External API types
│   ├── schemas/              # Zod validation schemas
│   │   ├── auth.ts
│   │   ├── chat.ts
│   │   ├── message.ts
│   │   ├── job.ts
│   │   └── video.ts
│   └── config/
│       ├── environment.ts    # Environment configuration
│       ├── database.ts       # Database configuration
│       └── services.ts       # Service configuration
├── package.json
├── tsconfig.json
├── Dockerfile                # Updated for Node.js
└── [existing Python files]   # Kept during transition
```

## 🔧 Technical Implementation Plan

### Phase 1: Foundation Setup (Week 1)

#### 1.1 Project Structure
- [ ] Create `src/` directory structure
- [ ] Set up TypeScript configuration
- [ ] Configure build and development scripts
- [ ] Set up linting and formatting (ESLint, Prettier)

#### 1.2 Dependencies Installation
```json
{
  "dependencies": {
    "hono": "^4.0.0",
    "@hono/node-server": "^1.8.0",
    "@hono/zod-validator": "^0.2.0",
    "zod": "^3.22.0",
    "@supabase/supabase-js": "^2.39.0",
    "@google-cloud/storage": "^7.7.0",
    "@google-cloud/aiplatform": "^3.15.0",
    "@google-cloud/secret-manager": "^5.0.0",
    "openai": "^4.24.0",
    "redis": "^4.6.0",
    "multer": "^1.4.5-lts.1",
    "uuid": "^9.0.0",
    "dotenv": "^16.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/multer": "^1.4.11",
    "@types/uuid": "^9.0.7",
    "tsx": "^4.6.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0",
    "@types/jest": "^29.5.0"
  }
}
```

#### 1.3 Basic Hono App Setup
- [ ] Create main `src/index.ts` with basic Hono app
- [ ] Set up development server with hot reload
- [ ] Configure basic middleware (CORS, logging)
- [ ] Test basic health check endpoint

### Phase 2: Core Infrastructure (Week 2)

#### 2.1 Authentication Middleware
- [ ] Convert Supabase auth from Python to TypeScript
- [ ] Implement JWT token validation
- [ ] Create auth middleware for protected routes
- [ ] Set up user context management

#### 2.2 Database Integration
- [ ] Set up Supabase TypeScript client
- [ ] Create database connection utilities
- [ ] Implement basic repository patterns
- [ ] Test database connectivity

#### 2.3 External Service Integration
- [ ] Google Cloud Storage client setup
- [ ] Google AI Platform integration
- [ ] OpenAI client configuration
- [ ] Redis cache client setup

### Phase 3: API Endpoint Migration (Week 3-4)

#### 3.1 Core Routes Migration
- [ ] Health check endpoint (`GET /`)
- [ ] User routes (`GET /users/{id}`)
- [ ] Authentication routes (if needed)

#### 3.2 Chat System Migration
- [ ] Chat CRUD operations
- [ ] Message creation and retrieval
- [ ] Chat history endpoints
- [ ] User chat filtering

#### 3.3 Streaming Endpoints
- [ ] AI chat streaming (`POST /chat`)
- [ ] Message streaming (`POST /stream-message`)
- [ ] Vercel AI SDK compatibility
- [ ] WebSocket support (if needed)

#### 3.4 File Upload System
- [ ] Test upload endpoint (`POST /test/upload`)
- [ ] Multipart file handling
- [ ] File validation and processing
- [ ] Storage integration

### Phase 4: Advanced Features (Week 5)

#### 4.1 Job Processing System
- [ ] Job creation endpoints
- [ ] Job status tracking
- [ ] Job filtering and pagination
- [ ] Background job integration

#### 4.2 Video Processing
- [ ] Video upload endpoints
- [ ] Processing pipeline integration
- [ ] Metadata extraction
- [ ] Progress tracking

#### 4.3 Service Layer Migration
- [ ] AI service conversion
- [ ] Chat service logic
- [ ] User service operations
- [ ] Job service functionality
- [ ] Video processing service

### Phase 5: Testing & Optimization (Week 6)

#### 5.1 Testing Suite
- [ ] Unit tests for services
- [ ] Integration tests for API endpoints
- [ ] Authentication flow testing
- [ ] File upload testing
- [ ] Streaming functionality testing

#### 5.2 Performance Optimization
- [ ] Response time optimization
- [ ] Memory usage analysis
- [ ] Caching strategy implementation
- [ ] Database query optimization

#### 5.3 Error Handling
- [ ] Global error handler middleware
- [ ] Structured error responses
- [ ] Logging and monitoring
- [ ] Graceful degradation

## 🔄 Migration Strategy

### Parallel Development Approach
1. **Keep FastAPI running** during development
2. **Develop Hono API** on different port (8001)
3. **Test endpoints** individually before switching
4. **Gradual migration** of frontend calls
5. **Complete switchover** once all endpoints are verified

### API Compatibility Matrix
| Endpoint                    | FastAPI | Hono | Status  | Notes          |
| --------------------------- | ------- | ---- | ------- | -------------- |
| `GET /`                     | ✅       | 🔄    | Pending | Health check   |
| `POST /test/upload`         | ✅       | 🔄    | Pending | File upload    |
| `GET /users/{id}`           | ✅       | 🔄    | Pending | User profile   |
| `GET /chats/`               | ✅       | 🔄    | Pending | Chat list      |
| `POST /chats/`              | ✅       | 🔄    | Pending | Create chat    |
| `GET /chats/{id}`           | ✅       | 🔄    | Pending | Chat details   |
| `PUT /chats/{id}`           | ✅       | 🔄    | Pending | Update chat    |
| `DELETE /chats/{id}`        | ✅       | 🔄    | Pending | Delete chat    |
| `POST /messages/`           | ✅       | 🔄    | Pending | Create message |
| `GET /chats/{id}/messages/` | ✅       | 🔄    | Pending | Chat messages  |
| `POST /chat`                | ✅       | 🔄    | Pending | Streaming chat |
| `POST /stream-message`      | ✅       | 🔄    | Pending | Stream message |
| `GET /api/v1/jobs/`         | ✅       | 🔄    | Pending | Job list       |

## 📝 Implementation Examples

### Authentication Middleware
```typescript
// src/middleware/auth.ts
import { createMiddleware } from 'hono/factory'
import { supabase } from '../lib/database/supabase'

export const authMiddleware = createMiddleware(async (c, next) => {
  const authHeader = c.req.header('Authorization')
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  const token = authHeader.replace('Bearer ', '')
  const { data: { user }, error } = await supabase.auth.getUser(token)
  
  if (error || !user) {
    return c.json({ error: 'Invalid token' }, 401)
  }

  c.set('user', user)
  await next()
})
```

### Route Example
```typescript
// src/routes/chats.ts
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { authMiddleware } from '../middleware/auth'
import { chatSchema } from '../schemas/chat'
import { ChatService } from '../services/chat-service'

const app = new Hono()

app.use('*', authMiddleware)

app.get('/', async (c) => {
  const skip = parseInt(c.req.query('skip') || '0')
  const limit = parseInt(c.req.query('limit') || '20')
  const user = c.get('user')
  
  const chatService = new ChatService()
  const chats = await chatService.getChats(user.id, skip, limit)
  
  return c.json(chats)
})

app.post('/', zValidator('json', chatSchema), async (c) => {
  const chatData = c.req.valid('json')
  const user = c.get('user')
  
  const chatService = new ChatService()
  const chat = await chatService.createChat(user.id, chatData)
  
  return c.json(chat, 201)
})

export default app
```

## 🚀 Deployment Considerations

### Docker Configuration
- Update Dockerfile to use Node.js base image
- Configure multi-stage build for production
- Optimize image size and security

### Environment Variables
- Migrate Python environment variables to Node.js format
- Update secret management
- Configure different environments (dev, staging, prod)

### CI/CD Pipeline
- Update build scripts for TypeScript
- Configure testing pipeline
- Set up deployment automation

## 📊 Success Metrics

### Performance Targets
- **Response Time**: < 100ms for simple endpoints
- **Throughput**: > 1000 requests/second
- **Memory Usage**: < 512MB baseline
- **Startup Time**: < 5 seconds

### Quality Metrics
- **Test Coverage**: > 80%
- **Type Safety**: 100% TypeScript coverage
- **API Compatibility**: 100% endpoint parity
- **Error Rate**: < 1%

## 🔍 Risk Assessment

### High Risk
- **Data Migration**: Ensure no data loss during transition
- **Authentication**: Maintain security during auth system migration
- **Streaming**: Complex streaming functionality migration

### Medium Risk
- **File Uploads**: Large file handling differences
- **External APIs**: Service integration compatibility
- **Performance**: Meeting performance targets

### Low Risk
- **Basic CRUD**: Standard endpoint migration
- **Configuration**: Environment setup
- **Testing**: Test suite establishment

## 📅 Timeline Summary

| Phase | Duration | Key Deliverables                  |
| ----- | -------- | --------------------------------- |
| 1     | Week 1   | Project setup, basic Hono app     |
| 2     | Week 2   | Auth, database, external services |
| 3     | Week 3-4 | Core API endpoints migration      |
| 4     | Week 5   | Advanced features, services       |
| 5     | Week 6   | Testing, optimization, deployment |

**Total Estimated Duration**: 6 weeks

## 🎯 Next Steps

1. **Approval**: Get stakeholder approval for migration plan
2. **Setup**: Create development branch and initial structure
3. **Dependencies**: Install and configure required packages
4. **Foundation**: Implement basic Hono app with health check
5. **Authentication**: Migrate auth system first (critical path)
6. **Incremental**: Begin endpoint-by-endpoint migration

## 🛠️ Development Tools & Setup

### Required Tools
- **Node.js**: v18+ (LTS recommended)
- **Bun**: Package manager (already configured)
- **TypeScript**: v5.3+
- **VSCode**: Recommended IDE with extensions:
  - TypeScript Importer
  - Hono Extension
  - Zod Schema Validator
  - Supabase Extension

### Development Environment
```bash
# Install dependencies
bun install

# Start development server
bun dev:hono

# Run tests
bun test

# Type checking
bun typecheck

# Linting
bun lint
```

### Code Quality Standards
- **TypeScript**: Strict mode enabled
- **ESLint**: Airbnb configuration with Hono-specific rules
- **Prettier**: Consistent code formatting
- **Husky**: Pre-commit hooks for quality checks
- **Conventional Commits**: Standardized commit messages

## 🔐 Security Considerations

### Authentication Security
- JWT token validation with Supabase
- Rate limiting on auth endpoints
- Secure cookie handling for sessions
- CORS configuration for allowed origins

### Data Protection
- Input validation with Zod schemas
- SQL injection prevention (Supabase handles this)
- File upload security (type validation, size limits)
- Sensitive data encryption in transit and at rest

### API Security
- Request rate limiting
- API key validation for external services
- HTTPS enforcement
- Security headers (HSTS, CSP, etc.)

## 📚 Learning Resources

### Hono Documentation
- [Official Hono Docs](https://hono.dev/)
- [Hono Middleware Guide](https://hono.dev/middleware)
- [Hono Best Practices](https://hono.dev/guides/best-practices)

### TypeScript Resources
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Zod Documentation](https://zod.dev/)
- [Supabase TypeScript Guide](https://supabase.com/docs/reference/javascript)

### Migration Guides
- [FastAPI to Express Migration](https://example.com) (similar patterns)
- [Python to TypeScript Conversion Guide](https://example.com)
- [API Migration Best Practices](https://example.com)

## 🐛 Troubleshooting Guide

### Common Issues

#### 1. Authentication Errors
**Problem**: JWT token validation fails
**Solution**:
- Check Supabase project configuration
- Verify JWT secret in environment variables
- Ensure token format is correct (Bearer token)

#### 2. File Upload Issues
**Problem**: Large file uploads fail
**Solution**:
- Increase request size limits in Hono
- Configure proper multipart handling
- Check storage service permissions

#### 3. Database Connection Issues
**Problem**: Supabase connection timeouts
**Solution**:
- Verify connection string format
- Check network connectivity
- Review connection pool settings

#### 4. Streaming Response Problems
**Problem**: AI streaming responses break
**Solution**:
- Ensure proper headers are set
- Check streaming implementation
- Verify client-side handling

### Debug Configuration
```typescript
// src/config/debug.ts
export const debugConfig = {
  logLevel: process.env.LOG_LEVEL || 'info',
  enableRequestLogging: process.env.NODE_ENV !== 'production',
  enableErrorStack: process.env.NODE_ENV === 'development',
  enablePerformanceMetrics: true
}
```

## 📊 Monitoring & Observability

### Metrics to Track
- **Response Times**: P50, P95, P99 latencies
- **Error Rates**: 4xx and 5xx response percentages
- **Throughput**: Requests per second
- **Resource Usage**: CPU, memory, disk I/O
- **Database Performance**: Query times, connection pool usage

### Logging Strategy
```typescript
// src/lib/utils/logger.ts
import { createLogger, format, transports } from 'winston'

export const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  transports: [
    new transports.Console(),
    new transports.File({ filename: 'logs/error.log', level: 'error' }),
    new transports.File({ filename: 'logs/combined.log' })
  ]
})
```

### Health Checks
```typescript
// src/routes/health.ts
import { Hono } from 'hono'
import { supabase } from '../lib/database/supabase'
import { redis } from '../lib/cache/redis'

const app = new Hono()

app.get('/health', async (c) => {
  const checks = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    services: {
      database: await checkDatabase(),
      cache: await checkRedis(),
      storage: await checkStorage()
    }
  }

  const allHealthy = Object.values(checks.services).every(s => s.status === 'ok')
  return c.json(checks, allHealthy ? 200 : 503)
})

async function checkDatabase() {
  try {
    const { error } = await supabase.from('users').select('count').limit(1)
    return { status: error ? 'error' : 'ok', message: error?.message }
  } catch (err) {
    return { status: 'error', message: err.message }
  }
}
```

## 🔄 Rollback Strategy

### Rollback Triggers
- Error rate > 5% for 5 minutes
- Response time P95 > 500ms for 10 minutes
- Critical functionality failure
- Security vulnerability discovered

### Rollback Process
1. **Immediate**: Switch traffic back to FastAPI
2. **Investigation**: Analyze logs and metrics
3. **Fix**: Address issues in Hono implementation
4. **Re-deploy**: Test and re-attempt migration
5. **Post-mortem**: Document lessons learned

### Rollback Checklist
- [ ] Database state is consistent
- [ ] No data loss occurred
- [ ] All services are functional
- [ ] Frontend integration works
- [ ] User sessions are preserved

## 📋 Testing Strategy

### Test Types
1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: API endpoints with real dependencies
3. **Contract Tests**: API compatibility with existing clients
4. **Performance Tests**: Load and stress testing
5. **Security Tests**: Authentication and authorization

### Test Structure
```
tests/
├── unit/
│   ├── services/
│   ├── middleware/
│   └── utils/
├── integration/
│   ├── routes/
│   ├── auth/
│   └── database/
├── e2e/
│   ├── api-compatibility/
│   └── user-flows/
└── performance/
    ├── load-tests/
    └── stress-tests/
```

### Test Examples
```typescript
// tests/integration/routes/chats.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { testClient } from '../helpers/test-client'

describe('Chat Routes', () => {
  beforeEach(async () => {
    await setupTestDatabase()
  })

  it('should create a new chat', async () => {
    const response = await testClient.post('/chats', {
      json: { title: 'Test Chat' },
      headers: { Authorization: 'Bearer test-token' }
    })

    expect(response.status).toBe(201)
    expect(response.json()).toMatchObject({
      id: expect.any(String),
      title: 'Test Chat'
    })
  })
})
```

## 🚀 Deployment Guide

### Production Deployment
```dockerfile
# Dockerfile.hono
FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

EXPOSE 8000
CMD ["node", "dist/index.js"]
```

### Environment Configuration
```bash
# Production environment variables
NODE_ENV=production
PORT=8000
LOG_LEVEL=info

# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket

# OpenAI
OPENAI_API_KEY=your-openai-key

# Redis
REDIS_URL=your-redis-url
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy-hono.yml
name: Deploy Hono API

on:
  push:
    branches: [main]
    paths: ['apps/core/src/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun test
      - run: bun typecheck

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and deploy
        run: |
          docker build -f Dockerfile.hono -t echo-api:latest .
          # Deploy to your infrastructure
```

## 📈 Performance Optimization

### Optimization Strategies
1. **Response Caching**: Cache frequently accessed data
2. **Database Optimization**: Efficient queries and indexing
3. **Connection Pooling**: Optimize database connections
4. **Compression**: Enable gzip compression
5. **CDN**: Use CDN for static assets

### Performance Monitoring
```typescript
// src/middleware/performance.ts
import { createMiddleware } from 'hono/factory'

export const performanceMiddleware = createMiddleware(async (c, next) => {
  const start = Date.now()

  await next()

  const duration = Date.now() - start
  c.header('X-Response-Time', `${duration}ms`)

  // Log slow requests
  if (duration > 1000) {
    console.warn(`Slow request: ${c.req.method} ${c.req.url} - ${duration}ms`)
  }
})
```

## 🎯 Success Criteria

### Technical Success Metrics
- [ ] All API endpoints migrated and functional
- [ ] Response times improved by 20%
- [ ] Memory usage reduced by 30%
- [ ] 100% test coverage for critical paths
- [ ] Zero data loss during migration
- [ ] Security audit passed

### Business Success Metrics
- [ ] Zero downtime during migration
- [ ] No user-facing issues reported
- [ ] Frontend integration seamless
- [ ] Development velocity maintained
- [ ] Team satisfaction with new stack

---

*This document will be updated as the migration progresses with actual implementation details, lessons learned, and any plan adjustments.*
