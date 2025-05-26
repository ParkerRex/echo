# Multi-stage Dockerfile for Echo Frontend Web App
FROM node:20-alpine as base

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/
COPY packages/supabase/package.json ./packages/supabase/

# Development stage
FROM base as development

# Install all dependencies (including dev dependencies)
RUN pnpm install --frozen-lockfile

# Copy source code
COPY apps/web/ ./apps/web/
COPY packages/ ./packages/

# Set working directory to web app
WORKDIR /app/apps/web

# Expose port
EXPOSE 3000

# Default command for development
CMD ["pnpm", "dev", "--host", "0.0.0.0"]

# Build stage
FROM base as build

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY apps/web/ ./apps/web/
COPY packages/ ./packages/

# Set working directory to web app
WORKDIR /app/apps/web

# Build the application
RUN pnpm build

# Production stage
FROM nginx:alpine as production

# Copy built application
COPY --from=build /app/apps/web/dist /usr/share/nginx/html

# Copy nginx configuration
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 