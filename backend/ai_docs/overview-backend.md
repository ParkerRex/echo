# Video Processing Pipeline - Clean Architecture Overview

This document provides a brief overview of the clean architecture approach and the example implementations provided in the `backend/docs/examples` directory.

## Clean Architecture Principles

Our implementation follows the clean architecture principles introduced by Robert C. Martin, which emphasize:

1. **Separation of Concerns**: Clear boundaries between different layers of the application
2. **Dependency Rule**: Dependencies always point inward, with the domain at the center
3. **Abstraction**: High-level modules don't depend on low-level modules; both depend on abstractions
4. **Testability**: Business logic is isolated from external concerns for better testing
5. **Framework Independence**: Core business logic doesn't depend on frameworks or external services

## Architecture Layers

Our implementation divides the application into the following layers:

### 1. Domain Layer

The domain layer contains the core business entities, value objects, and business rules. It has no dependencies on other layers or external frameworks.

Key components:
- Domain entities (e.g., `Video`, `Job`)
- Value objects
- Domain exceptions

### 2. Application Layer

The application layer contains the use cases and business logic that orchestrates the domain entities. It defines interfaces that will be implemented by the adapters layer.

Key components:
- Application services (e.g., `TranscriptionService`, `VideoProcessorService`)
- Service interfaces (e.g., `StorageInterface`, `AIServiceInterface`)
- Data Transfer Objects (DTOs)

### 3. Adapters Layer

The adapters layer contains implementations of the interfaces defined in the application layer. These adapters translate between the application layer and external systems.

Key components:
- Storage adapters (e.g., `GCSStorageAdapter`)
- AI service adapters (e.g., `GeminiAIAdapter`)
- Publishing adapters (e.g., `YouTubeAdapter`)

### 4. Infrastructure Layer

The infrastructure layer contains framework-specific code, configurations, and other technical details.

Key components:
- API implementation (e.g., FastAPI or Flask routes)
- Dependency injection container
- Database repositories
- Configuration management

## Example Implementations

The `backend/docs/examples` directory contains sample implementations of key components in the new architecture:

### 1. Application Interfaces

The `application/interfaces/storage.py` file demonstrates a clean interface definition for storage operations:

- Defines a clear contract through abstract methods
- Uses domain-specific exceptions
- Is independent of any specific storage provider
- Provides comprehensive documentation for implementers

### 2. Adapter Implementation

The `adapters/storage/gcs.py` file shows how to implement the storage interface for Google Cloud Storage:

- Implements all methods defined in the interface
- Handles GCS-specific concerns (like path formats, authentication)
- Translates between domain exceptions and provider-specific exceptions
- Uses asynchronous programming with thread pooling for non-blocking I/O

### 3. Dependency Injection

The `infrastructure/config/container.py` file demonstrates a flexible dependency injection approach:

- Provides a container for managing service instances
- Supports both singleton and transient lifetimes
- Allows easy swapping of implementations (e.g., for testing)
- Centralizes configuration of all application services

### 4. Application Entry Point

The `main.py` file shows how all components come together in the application entry point:

- Sets up the dependency injection container
- Configures services based on environment variables
- Provides Cloud Function handlers for event processing
- Includes a local development entry point for testing

## Benefits of This Approach

1. **Maintainability**: Smaller, focused components with clear responsibilities
2. **Testability**: Business logic can be tested without external dependencies
3. **Flexibility**: Implementation details can be changed without affecting core logic
4. **Scalability**: Components can be evolved or replaced independently
5. **Clarity**: Clear dependencies and service boundaries

## Implementation Strategy

To migrate the existing monolithic code to this architecture:

1. Start by defining domain models and interfaces
2. Implement adapters for existing external services
3. Refactor business logic into application services
4. Set up the dependency injection container
5. Update the main entry point to use the new architecture

This can be done incrementally, allowing the application to continue functioning during the migration.

## Further Reading

For more details about the implementation plan and file structures:

- `backend/docs/be-prd.txt` - Product Requirements Document
- `backend/docs/file-structure-comparison.md` - Current vs. Proposed File Structure
- `backend/docs/implementation-tasks.md` - Detailed Implementation Tasks 