# Multi-stage Dockerfile for Echo Backend API
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy Python project files
COPY apps/core/pyproject.toml apps/core/uv.lock ./

# Development stage
FROM base as development

# Install development dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e ".[dev]"

# Copy source code
COPY apps/core/ ./
COPY packages/ /packages/

# Expose port
EXPOSE 8000

# Default command for development (can be overridden in docker-compose)
CMD [".venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Install only production dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install .

# Copy source code
COPY apps/core/ ./
COPY packages/ /packages/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Production command
CMD [".venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 