# Development stage
FROM oven/bun:1 AS development

WORKDIR /app

# Copy package files
COPY package.json bun.lockb* ./

# Install all dependencies
RUN bun install

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Start development server
CMD ["bun", "run", "dev"]

# Build stage
FROM oven/bun:1 AS builder

WORKDIR /app

# Copy package files
COPY package.json bun.lockb* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN bun run build

# Production stage
FROM oven/bun:1-slim AS production

WORKDIR /app

# Copy package files and install production dependencies only
COPY package.json bun.lockb* ./
RUN bun install --production

# Copy built application
COPY --from=builder /app/dist ./dist

# Copy any static files or configs needed at runtime
COPY --from=builder /app/drizzle ./drizzle

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
USER nodejs

# Expose port
EXPOSE 8000

# Start the application
CMD ["bun", "run", "start"]