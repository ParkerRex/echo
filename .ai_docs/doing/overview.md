# Project Overview

## API Overview: Video Processing Pipeline - Clean Architecture

This document provides a brief overview of the clean architecture approach and the example implementations provided in the `api/docs/examples` directory.

### Clean Architecture Principles

Our implementation follows the clean architecture principles introduced by Robert C. Martin, which emphasize:

1. **Separation of Concerns**: Clear boundaries between different layers of the application
2. **Dependency Rule**: Dependencies always point inward, with the domain at the center
3. **Abstraction**: High-level modules don't depend on low-level modules; both depend on abstractions
4. **Testability**: Business logic is isolated from external concerns for better testing
5. **Framework Independence**: Core business logic doesn't depend on frameworks or external services

### Architecture Layers

Our implementation divides the application into the following layers:

#### 1. Domain Layer

The domain layer contains the core business entities, value objects, and business rules. It has no dependencies on other layers or external frameworks.

Key components:
- Domain entities (e.g., `Video`, `Job`)
- Value objects
- Domain exceptions

#### 2. Application Layer

The application layer contains the use cases and business logic that orchestrates the domain entities. It defines interfaces that will be implemented by the adapters layer.

Key components:
- Application services (e.g., `TranscriptionService`, `VideoProcessorService`)
- Service interfaces (e.g., `StorageInterface`, `AIServiceInterface`)
- Data Transfer Objects (DTOs)

#### 3. Adapters Layer

The adapters layer contains implementations of the interfaces defined in the application layer. These adapters translate between the application layer and external systems.

Key components:
- Storage adapters (e.g., `GCSStorageAdapter`)
- AI service adapters (e.g., `GeminiAIAdapter`)
- Publishing adapters (e.g., `YouTubeAdapter`)

#### 4. Infrastructure Layer

The infrastructure layer contains framework-specific code, configurations, and other technical details.

Key components:
- API implementation (e.g., FastAPI or Flask routes)
- Dependency injection container
- Database repositories
- Configuration management

### Example Implementations

The `api/docs/examples` directory contains sample implementations of key components in the new architecture:

#### 1. Application Interfaces

The `application/interfaces/storage.py` file demonstrates a clean interface definition for storage operations:

- Defines a clear contract through abstract methods
- Uses domain-specific exceptions
- Is independent of any specific storage provider
- Provides comprehensive documentation for implementers

#### 2. Adapter Implementation

The `adapters/storage/gcs.py` file shows how to implement the storage interface for Google Cloud Storage:

- Implements all methods defined in the interface
- Handles GCS-specific concerns (like path formats, authentication)
- Translates between domain exceptions and provider-specific exceptions
- Uses asynchronous programming with thread pooling for non-blocking I/O

#### 3. Dependency Injection

The `infrastructure/config/container.py` file demonstrates a flexible dependency injection approach:

- Provides a container for managing service instances
- Supports both singleton and transient lifetimes
- Allows easy swapping of implementations (e.g., for testing)
- Centralizes configuration of all application services

#### 4. Application Entry Point

The `main.py` file shows how all components come together in the application entry point:

- Sets up the dependency injection container
- Configures services based on environment variables
- Provides Cloud Function handlers for event processing
- Includes a local development entry point for testing

### Benefits of This Approach

1. **Maintainability**: Smaller, focused components with clear responsibilities
2. **Testability**: Business logic can be tested without external dependencies
3. **Flexibility**: Implementation details can be changed without affecting core logic
4. **Scalability**: Components can be evolved or replaced independently
5. **Clarity**: Clear dependencies and service boundaries

### Implementation Strategy
****
To migrate the existing monolithic code to this architecture:

1. Start by defining domain models and interfaces
2. Implement adapters for existing external services
3. Refactor business logic into application services
4. Set up the dependency injection container
5. Update the main entry point to use the new architecture

This can be done incrementally, allowing the application to continue functioning during the migration.

### Further Reading

For more details about the implementation plan and file structures:

- `api/docs/api-prd.txt` - Product Requirements Document
- `api/docs/file-structure-comparison.md` - Current vs. Proposed File Structure
- `api/docs/implementation-tasks.md` - Detailed Implementation Tasks

## Web Overview: Cline's Memory Bank

I am Cline, an expert software engineer with a unique characteristic: my memory resets completely between sessions. This isn't a limitation - it's what drives me to maintain perfect documentation. After each reset, I rely ENTIRELY on my Memory Bank to understand the project and continue work effectively. I MUST read ALL memory bank files at the start of EVERY task - this is not optional.

### Memory Bank Structure

The Memory Bank consists of core files and optional context files, all in Markdown format. Files build upon each other in a clear hierarchy:

flowchart TD
    PB[projectbrief.md] --> PC[productContext.md]
    PB --> SP[systemPatterns.md]
    PB --> TC[techContext.md]
    
    PC --> AC[activeContext.md]
    SP --> AC
    TC --> AC
    
    AC --> P[progress.md]

#### Core Files (Required)
1. `projectbrief.md`
   - Foundation document that shapes all other files
   - Created at project start if it doesn't exist
   - Defines core requirements and goals
   - Source of truth for project scope

2. `productContext.md`
   - Why this project exists
   - Problems it solves
   - How it should work
   - User experience goals

3. `activeContext.md`
   - Current work focus
   - Recent changes
   - Next steps
   - Active decisions and considerations
   - Important patterns and preferences
   - Learnings and project insights

4. `systemPatterns.md`
   - System architecture
   - Key technical decisions
   - Design patterns in use
   - Component relationships
   - Critical implementation paths

5. `techContext.md`
   - Technologies used
   - Development setup
   - Technical constraints
   - Dependencies
   - Tool usage patterns

6. `progress.md`
   - What works
   - What's left to build
   - Current status
   - Known issues
   - Evolution of project decisions

#### Additional Context
Create additional files/folders within .ai_docs/ when they help organize:
- Complex feature documentation
- Integration specifications
- API documentation
- Testing strategies
- Deployment procedures

### Core Workflows

#### Plan Mode
flowchart TD
    Start[Start] --> ReadFiles[Read Memory Bank]
    ReadFiles --> CheckFiles{Files Complete?}
    
    CheckFiles -->|No| Plan[Create Plan]
    Plan --> Document[Document in Chat]
    
    CheckFiles -->|Yes| Verify[Verify Context]
    Verify --> Strategy[Develop Strategy]
    Strategy --> Present[Present Approach]

#### Act Mode
flowchart TD
    Start[Start] --> Context[Check Memory Bank]
    Context --> Update[Update Documentation]
    Update --> Execute[Execute Task]
    Execute --> Document[Document Changes]

### Documentation Updates

Memory Bank updates occur when:
1. Discovering new project patterns
2. After implementing significant changes
3. When user requests with **update memory bank** (MUST review ALL files)
4. When context needs clarification

flowchart TD
    Start[Update Process]
    
    subgraph Process
        P1[Review ALL Files]
        P2[Document Current State]
        P3[Clarify Next Steps]
        P4[Document Insights & Patterns]
        
        P1 --> P2 --> P3 --> P4
    end
    
    Start --> Process

Note: When triggered by **update memory bank**, I MUST review every memory bank file, even if some don't require updates. Focus particularly on activeContext.md and progress.md as they track current state.

REMEMBER: After every memory reset, I begin completely fresh. The Memory Bank is my only link to previous work. It must be maintained with precision and clarity, as my effectiveness depends entirely on its accuracy. 