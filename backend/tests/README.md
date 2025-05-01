# Testing Guide for Video Processor

This directory contains tests for the video processor service, organized in a modular structure to match the application architecture.

## Test Structure

```
tests/
├── conftest.py                # Common pytest fixtures
├── unit/                      # Unit tests for individual components
│   ├── test_audio_processor.py     # Tests for audio processing
│   ├── test_storage_service.py     # Tests for storage services
│   ├── test_video_processor.py     # Tests for video processing
│   └── test_api.py                 # Tests for API endpoints
├── integration/              # Integration tests between components
├── e2e/                      # End-to-end workflow tests
└── outdated/                 # Legacy tests that need to be migrated
```

## Running Tests

Run all tests:
```bash
cd backend
pytest
```

Run specific test categories:
```bash
# Unit tests only
pytest tests/unit

# Integration tests only
pytest tests/integration

# End-to-end tests only
pytest tests/e2e
```

## Test Coverage

To run tests with coverage report:
```bash
pytest --cov=video_processor
```

## Key Testing Features

1. **Dependency Injection Testing**
   - Mock service implementations are injected for testing
   - Isolated component testing with clear boundaries

2. **Interface-Based Testing**
   - Tests verify that components follow their interface contracts
   - Ensures implementation changes don't break behavior

3. **Consistent Fixture Usage**
   - Common test fixtures in conftest.py
   - Standardized mock objects and setup

## Adding New Tests

When adding new functionality:

1. Add unit tests for the new component in the appropriate subdirectory
2. Update integration tests if the component interacts with other components
3. Ensure all code paths are covered, including error handling
4. Follow the existing test naming and organization patterns

## Legacy Tests

The `outdated/` directory contains tests from the previous architecture that:
1. Need to be migrated to the new structure
2. May be obsolete due to architectural changes
3. Should be referenced when adding test coverage for components