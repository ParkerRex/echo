# 🐳 Docker Development Environment

This guide explains our updated Docker development environment, which provides a consistent, reliable way to run both the frontend and backend services together. This setup ensures your local development environment closely matches production.

## 🌟 Key Features

- **Unified Environment**: Run frontend (React/Vite), backend (Python/Flask), and optional mock services together
- **Simple Commands**: Start, stop, and monitor all services with easy-to-use scripts
- **Real-time Development**: Changes to your code are automatically detected and applied
- **Consistent Setup**: Same environment for all team members, regardless of local machine setup
- **Integrated Testing**: Comprehensive testing tools that validate the entire application flow

## 📋 Prerequisites

- **Docker**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop) (Mac/Windows) or Docker Engine (Linux)
- **Git**: For version control
- **Text Editor**: VS Code or your preferred editor
- **Terminal**: For running commands

## 🚀 Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Automations.git
cd Automations
```

### Step 2: Set Up Credentials

Place your Google Cloud service account JSON file at:

```
./@credentials/service_account.json
```

> 💡 If you don't have credentials yet, the `docker-start.sh` script will offer to create mock credentials for testing purposes.

### Step 3: Start the Services

Start both frontend and backend services with a single command:

```bash
./docker-start.sh
```

When started successfully, you'll see:
```
✅ Services started successfully!
Frontend: http://localhost:3000
Backend:  http://localhost:8080
```

## 🛠️ Available Commands

### Service Management

```bash
# Start services (frontend and backend)
./docker-start.sh

# Rebuild containers (after dependency changes)
./docker-start.sh --rebuild

# Include mock GCS service for testing
./docker-start.sh --with-mock

# Stop services (keep containers)
./docker-stop.sh

# Stop and remove containers
./docker-stop.sh --remove
```

### Monitoring and Logs

```bash
# View all logs
./docker-logs.sh

# View logs for a specific service
./docker-logs.sh --service frontend
./docker-logs.sh --service backend

# View logs without following
./docker-logs.sh --no-follow
```

### Testing

```bash
# Run comprehensive tests
./docker-test.sh

# Clean test directories first
./docker-test.sh --clean

# Test with a specific video file
./docker-test.sh --video "my-test-video.mp4"
```

### Production Monitoring

```bash
# Monitor deployed services
./monitor-services.sh
```

## 📂 Project Structure

The Docker environment maps local directories to containers:

```
Automations/
├── frontend/                # React frontend code (mapped to frontend container)
│   ├── app/                 # React application code
│   ├── package.json         # Frontend dependencies
│   └── ...
├── backend/                 # Python backend code (mapped to backend container)
│   ├── video_processor/     # Core video processing code
│   ├── requirements.txt     # Backend dependencies
│   └── ...
├── docker-compose.yml       # Docker services configuration
├── docker-start.sh          # Script to start services
├── docker-stop.sh           # Script to stop services
├── docker-logs.sh           # Script to view logs
└── docker-test.sh           # Script to run tests
```

## 🔄 Development Workflow

1. **Start the environment**: `./docker-start.sh`
2. **Make changes** to frontend or backend code
3. **Watch changes automatically apply**:
   - Frontend changes refresh in the browser
   - Backend changes trigger automatic reload
4. **View logs** to troubleshoot: `./docker-logs.sh`
5. **Run tests** to verify: `./docker-test.sh`
6. **Stop when done**: `./docker-stop.sh`

## 📝 Configuration

### Docker Compose

The `docker-compose.yml` file defines all services:

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    # ...

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    volumes:
      - ./backend:/app
    # ...

  mock-gcs:
    build: ./scripts/mock_gcs
    ports:
      - "8081:8081"
    # ... (only used when started with --with-mock)
```

### Environment Variables

* **Frontend**:
  - `VITE_API_URL`: URL for the backend API (automatically set)

* **Backend**:
  - `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account credentials
  - `GCS_UPLOAD_BUCKET`: Target GCS bucket name
  - `TESTING_MODE`: Enable/disable testing mode

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check if anything is using the required ports
   lsof -i :3000  # Frontend port
   lsof -i :8080  # Backend port
   ```

2. **Container fails to start**:
   ```bash
   # View detailed logs for the failing service
   ./docker-logs.sh --service backend
   ```

3. **Dependencies not updated**:
   ```bash
   # Rebuild containers after adding new dependencies
   ./docker-start.sh --rebuild
   ```

4. **Firestore connection issues**:
   ```bash
   # Verify Firebase configuration in frontend/firebase.ts
   ```

### Accessing Container Shell

For advanced debugging:

```bash
# Access backend container shell
docker exec -it automations-backend bash

# Access frontend container shell
docker exec -it automations-frontend sh
```

## 🌐 Additional Resources

- [Testing Guide](TESTING_GUIDE.md): Detailed testing procedures
- [Monitoring Guide](MONITORING_GUIDE.md): How to monitor the application
- [Project Structure](PROJECT_STRUCTURE.md): Overview of project organization