# Development stage
FROM oven/bun:1 AS development

WORKDIR /app

# Copy package files from workspace root and current app
COPY package.json bun.lockb* ./
COPY apps/website/package.json ./apps/website/

# Install all dependencies
RUN bun install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["bun", "run", "dev"]

# Dependencies stage
FROM oven/bun:1 AS deps

WORKDIR /app

# Copy package files
COPY package.json bun.lockb* ./
COPY apps/website/package.json ./apps/website/

# Install production dependencies
RUN bun install --frozen-lockfile

# Builder stage
FROM oven/bun:1 AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/bun.lockb ./bun.lockb

# Copy source code
COPY . .

# Build the Next.js application
ENV NEXT_TELEMETRY_DISABLED=1
RUN bun run build

# Production stage
FROM oven/bun:1-slim AS production

WORKDIR /app

# Set environment to production
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set ownership
RUN chown -R nodejs:nodejs .

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Start the Next.js server
CMD ["node", "server.js"]