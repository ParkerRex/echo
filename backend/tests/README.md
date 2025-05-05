# Video Processor Testing Guide

This directory contains the test suite for the Video Processing Pipeline. The tests follow a clean architecture approach, mirroring the structure of the main application.

## Test Structure

```
tests/
├── conftest.py            # Shared test fixtures and configurations
├── mocks/                 # Mock implementations of external dependencies
│   ├── ai.py              # Mock AI service adapter
│   ├── publishing.py      # Mock publishing adapter
│   └── storage.py         # Mock storage adapter
├── unit/                  # Unit tests for isolated components
│   ├── domain/            # Tests for domain models
│   ├── application/       # Tests for application services
│   └── adapters/          # Tests for adapter implementations
├── integration/           # Integration tests for component combinations
│   ├── api/               # API integration tests
│   ├── storage/           # Storage integration tests
│   └── ai/                # AI service integration tests
└── e2e/                   # End-to-end tests for complete workflows
```

## Running Tests

### Running All Tests

```bash
pytest
```

### Running Specific Test Types

```bash
# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run end-to-end tests only
pytest tests/e2e/
```

### Running Tests with Coverage

```bash
# Run tests with coverage report
pytest --cov=video_processor

# Generate HTML coverage report
pytest --cov=video_processor --cov-report=html
```

## Test Categories

### Unit Tests

Unit tests focus on testing individual components in isolation, using mock objects for dependencies. These tests ensure that each component behaves as expected on its own.

### Integration Tests

Integration tests verify that combinations of components work together correctly. These tests may use real external services in test environments.

### End-to-End Tests

End-to-end tests validate complete system workflows from start to finish. These tests ensure that the entire video processing pipeline functions correctly as a whole.

## Mock Objects

The `mocks/` directory contains mock implementations of external dependencies, such as storage, AI services, and publishing services. These mocks allow for reliable testing without requiring access to real external services.

## Test Fixtures

Common test fixtures are defined in `conftest.py`. These fixtures provide test data and mock objects that can be reused across multiple tests. 