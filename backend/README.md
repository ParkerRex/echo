# Video Processor Backend

## Development Setup (Mac)

1. **Python Version Management with pyenv**:
   ```bash
   # Ensure you're using the correct Python version
   pyenv install 3.12.7  # If not already installed
   pyenv local 3.12.7    # Sets Python version for this directory
   ```

2. **Virtual Environment Setup**:
   ```bash
   # Create venv using pyenv's Python
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   make install-dev
   ```

## VS Code Python Interpreter Setup

When VS Code asks you to select a Python interpreter:

1. **For Mac Users**:
   - Select the interpreter that shows "(pyenv)" in its path
   - It should be `.../pyenv/versions/3.12.7/bin/python`
   - This ensures you're using the pyenv-managed Python version
   - DO NOT select system Python or other versions

2. **After pyenv selection**:
   - VS Code will automatically find the virtual environment in `backend/venv`
   - You'll see "venv" in the status bar once it's properly configured

## Development Tools

We use specific versions of development tools to ensure consistency:

1. **Python Version**:
   - Python 3.12.7 (managed via pyenv)
   - Used for all backend development

2. **Code Quality Tools**:
   - Black v24.1.1 (formatter)
   - Ruff v0.2.1 (linter)
   - pytest 7.4.0 (testing)

These versions are pinned in requirements.txt for consistency across the team.

### Available Commands

Use `make` commands to run code quality tools:

```bash
# Format code (Black + Ruff)
make format

# Run linter checks
make lint

# Run tests
make test

# Run all checks (format, lint, test)
make check
```

### Tool Configuration

- Black and Ruff configurations are in `pyproject.toml`
- VS Code settings are in `.vscode/settings.json`
- Extension recommendations are in `.vscode/extensions.json`

## Troubleshooting

If you encounter Python/VS Code issues:

1. **Wrong Python Version**:
   ```bash
   # Check your current Python version
   python --version  # Should show 3.12.7
   
   # If incorrect, ensure pyenv is set:
   pyenv local 3.12.7
   ```

2. **Virtual Environment Issues**:
   ```bash
   # Recreate the virtual environment if needed
   deactivate  # If already in a venv
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **VS Code Integration**:
   - Command Palette → "Python: Select Interpreter"
   - Choose the pyenv version (3.12.7) from the list
   - Look for the path containing "pyenv/versions/3.12.7"
   - VS Code should then detect and use the venv automatically
   - Reload VS Code if settings aren't taking effect

# Video Processing Pipeline

This backend service is responsible for processing video files, generating metadata, and publishing to various platforms.

## Architecture

This project follows a clean architecture approach with clear separation of concerns:

- **Domain Layer**: Core business entities and rules
- **Application Layer**: Use cases and orchestration
- **Adapters Layer**: External service integrations
- **Infrastructure Layer**: Framework-specific code

## Getting Started

### Prerequisites

- Python 3.12+
- FFmpeg
- Google Cloud SDK (for GCS and Pub/Sub)
- API keys for:
  - Google AI (Gemini/Vertex AI)
  - YouTube API

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

## Running the Service

### Development Mode

```bash
python -m video_processor.main
```

### Docker

```bash
# Build the Docker image
docker build -t video-processor .

# Run the container
docker run -p 8080:8080 --env-file .env video-processor
```

## Testing

The project includes comprehensive tests at different levels:

### Running Tests

Using the test script:

```bash
# Run all tests
./run_tests.sh

# Run specific test types
./run_tests.sh unit     # Unit tests
./run_tests.sh integration  # Integration tests
./run_tests.sh e2e      # End-to-end tests
./run_tests.sh coverage # Tests with coverage report
```

Manual test execution:

```bash
# From the backend directory
cd backend
pytest               # Run all tests
pytest tests/unit/   # Run only unit tests
pytest --cov=video_processor  # Run with coverage
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

## Project Structure

```
video_processor/
├── domain/         # Domain entities and business rules
├── application/    # Use cases and service interfaces
├── adapters/       # External service implementations
├── infrastructure/ # Framework code and configuration
├── utils/          # Utility functions
└── main.py         # Application entry point
```

## Documentation

Additional documentation:

- [Implementation Tasks](docs/implementation-tasks.md): Detailed task breakdown
- [API Documentation](docs/api.md): API usage guide
- [Architecture Overview](docs/overview.md): Architecture details

## License

This project is proprietary and confidential.

## Contributing

Please follow the established coding conventions and test your changes before submitting.
