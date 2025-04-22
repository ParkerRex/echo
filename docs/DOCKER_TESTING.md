# Docker Testing Guide

This guide explains how to run Docker-based tests for the Video Processor application.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11 or later
- Test video file in the `test_data` directory
- Service account credentials in `credentials/service_account.json` (for real API tests)

## Running the Docker Test

The Docker test script automates the process of testing the application with Docker. It:

1. Sets up the test environment
2. Starts the Docker containers
3. Sends a test event
4. Verifies that the outputs are generated correctly
5. Cleans up the containers

### Basic Usage

```bash
# Make the script executable (only needed once)
chmod +x scripts/docker_test.sh

# Run the test with default settings
./scripts/docker_test.sh
```

### Options

- `--clean`: Clean the test directories before running the test
- `--video`: Specify a custom video file to use for testing

```bash
# Clean test directories before running
./scripts/docker_test.sh --clean

# Use a specific video file
./scripts/docker_test.sh --video "my-test-video.mp4"
```

## What to Look For

The test will output information about each step of the process. Look for:

- "✅ Test passed! All outputs were generated correctly." - Indicates the test was successful
- Content previews for each output file
- "Test completed successfully!" - Final confirmation of success

If the test fails, you'll see:
- "❌ Test failed!" followed by details about what went wrong

## Real API Testing

For testing with real API calls instead of mocks, use the `real_api_test.py` script:

```bash
# Make the script executable (only needed once)
chmod +x scripts/real_api_test.py

# Run the test with real API calls
python scripts/real_api_test.py --clean
```

### Service Account Credentials

Real API tests require valid Google Cloud service account credentials:

1. Place your service account JSON file at `credentials/service_account.json`

2. The service account should have the necessary permissions:
   - Storage Object Admin for GCS access
   - Vertex AI User for Gemini API access

If the service account file is not found in either location, the Docker test will create a mock file for testing purposes, but real API calls will fail.

## Troubleshooting

### Common Issues

1. **Docker not running**
   - Make sure Docker is installed and running
   - Run `docker --version` to verify

2. **Missing test video file**
   - Ensure you have a test video file in the `test_data` directory
   - The default test looks for "Satya Nadella on Vibe Coding.mp4"

3. **Port conflicts**
   - If ports 8080 or 8081 are already in use, stop the services using them
   - You can modify the port mappings in `docker-compose.yml` if needed

4. **Container startup issues**
   - Check the Docker logs: `docker-compose logs`
   - Increase the wait time in the script if needed

5. **Authentication failures in real API tests**
   - Verify that `docs/service_account.json` contains valid credentials
   - Check that the service account has the necessary permissions
   - Ensure the project ID in the service account matches the one in the code

## CI/CD Integration

The Docker test is integrated into the GitHub Actions workflow in `.github/workflows/deploy.yml`. It runs after the lint and unit tests, and before the build and deploy steps.

This ensures that the application works correctly with Docker before it's deployed to production.
