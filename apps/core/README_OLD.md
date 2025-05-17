# Video Processor API

The Video Processor API is a service for processing videos, generating transcripts, and creating metadata using AI capabilities.

This service implements a clean architecture approach, separating concerns into distinct layers to improve modularity, testability, and maintainability.

## Architecture

The project follows a clean architecture with the following layers:

### Domain Layer

The core business logic and entities, independent of any external frameworks or technologies:

- `video_processor/domain/models/` - Core business objects
- `video_processor/domain/exceptions.py` - Domain-specific exceptions

### Application Layer

Application services that orchestrate the use cases of the system:

- `video_processor/application/services/` - Implement business use cases
- `video_processor/application/interfaces/` - Define abstractions for external services
- `video_processor/application/dtos/` - Data transfer objects for service boundaries

### Adapters Layer

Implements interfaces defined in the application layer, adapting external services to the application:

- `video_processor/adapters/ai/` - AI service adapters (e.g., Gemini, Vertex AI)
- `video_processor/adapters/storage/` - Storage adapters (e.g., GCS, local)
- `video_processor/adapters/publishing/` - Publishing adapters (e.g., YouTube)

### Infrastructure Layer

Framework-specific code, configuration, and external dependencies:

- `video_processor/infrastructure/api/` - FastAPI implementation
- `video_processor/infrastructure/config/` - Configuration management
- `video_processor/infrastructure/repositories/` - Data storage implementations
- `video_processor/infrastructure/messaging/` - Messaging systems
- `video_processor/infrastructure/monitoring.py` - Logging and metrics

## Setup and Installation

### Prerequisites

- Python 3.10+
- FFmpeg (for video processing)
- Google Cloud credentials (for GCS, Secret Manager, etc.)

### Local Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/echo.git
cd echo/api
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e ".[dev]"
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run pre-commit hooks installation:

```bash
pre-commit install
```

### Running the API

#### Development Mode

```bash
uvicorn video_processor.infrastructure.api.main:app --reload
```

#### Production Mode

```bash
gunicorn video_processor.infrastructure.api.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
```

### Docker

Build and run with Docker:

```bash
docker build -t video-processor-api .
docker run -p 8080:8080 video-processor-api
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run integration tests only
pytest tests/integration

# Run with coverage
pytest --cov=video_processor
```

### Test Configuration

Integration tests require some external services. You can set up test-specific credentials in `.env.test`.

## API Documentation

API documentation is available at `/docs` when the service is running. This includes detailed information about endpoints, request/response formats, and authentication requirements.

## Performance Optimization

The service includes several performance optimizations:

1. **AI Response Caching**: Cacheable AI responses are stored to reduce API calls and latency
2. **Parallel Processing**: Where applicable, operations are performed in parallel 
3. **Profiling Tools**: The service includes utilities to monitor performance and identify bottlenecks

## Authentication and Security

The service supports two authentication methods:

1. **JWT Tokens**: For user authentication
2. **API Keys**: For service-to-service communication

Role-based access control is implemented to restrict access to resources based on user roles.

## Deployment

The service is deployed to Google Cloud Run via the included Cloud Build configuration. The CI/CD pipeline includes:

1. Running tests
2. Building and pushing Docker images
3. Deployment to staging environment
4. Deployment verification
5. (For main branch) Deployment to production environment

## Architecture Diagrams

### High-Level Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Client Apps    │─────▶│  API Gateway    │─────▶│  Video Processor│
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           │
                         ┌─────────────────┐      ┌────────▼────────┐
                         │                 │      │                 │
                         │  Storage (GCS)  │◀─────│  AI Services    │
                         │                 │      │                 │
                         └─────────────────┘      └─────────────────┘
```

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Infrastructure Layer                                       │
│  (FastAPI, GCP Services, Database)                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Adapters Layer                                             │
│  (AI Adapters, Storage Adapters, Publishing Adapters)       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Application Layer                                          │
│  (Services, Use Cases, Interfaces)                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Domain Layer                                               │
│  (Models, Business Logic, Exceptions)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Contributing

1. Create a feature branch from `develop`
2. Make changes and add tests
3. Run tests and linters
4. Create a pull request

## License

Proprietary - All rights reserved.

# Quick setup command for developers:
source ./setup.sh
