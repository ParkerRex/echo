# ---- Build Stage ----
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy pyproject.toml
COPY pyproject.toml .

# Install build tools
RUN pip install --no-cache-dir build wheel

# Copy source code
COPY video_processor/ ./video_processor/

# Build wheel package
RUN pip wheel --no-cache-dir --wheel-dir /wheels -e .

# ---- Runtime Stage ----
FROM python:3.11-slim

# Install ffmpeg system package
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Install application and dependencies
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy necessary files for running
COPY tests/ /app/tests/
COPY scripts/ /app/scripts/
COPY video_processor/infrastructure/api/server.py /app/server.py
COPY video_processor/main.py /app/main.py

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE ${PORT}

# Switch to non-root user
USER appuser

# Create runtime configuration - FastAPI server by default
CMD exec gunicorn --bind :${PORT} --workers 1 --threads 8 --timeout 0 \
    --worker-class uvicorn.workers.UvicornWorker \
    "server:create_app()"
