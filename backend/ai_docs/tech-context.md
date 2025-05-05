# Technical Context: Backend

## Core Technologies

### Programming Languages
- **Python 3.12+**: Primary backend language
- **TypeScript/JavaScript**: Used for cloud functions and some utilities

### Frameworks & Libraries
- **Flask**: Web framework for API endpoints
- **Google Cloud Functions**: Serverless computing for specific processes
- **Pytest**: Testing framework
- **FFmpeg**: Video processing and transformation

### Infrastructure & Cloud Services
- **Google Cloud Platform**
  - Cloud Storage: For video and asset storage
  - Cloud Functions: For serverless processing
  - Vertex AI: For AI/ML capabilities
  - Secret Manager: For managing secrets and credentials
- **Docker**: For containerization and consistent environments
- **Supabase**: For database and authentication

### Data Storage
- **PostgreSQL**: Primary relational database via Supabase
- **Google Cloud Storage**: Object storage for video files and assets

### AI & ML
- **Google Vertex AI**: For video analysis and content intelligence
- **Custom ML Models**: For specialized content analysis

## Development Environment

### Local Setup
- Python 3.12+ with virtual environment
- Docker for containerized services
- FFmpeg for local video processing
- Google Cloud SDK for cloud interaction
- Environment variables via .env files

### Preferred Tools
- Visual Studio Code with Python extensions
- Postman for API testing
- Docker Desktop for container management

### Environment Variables
Required in `.env` file:
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key
- `FLASK_ENV`: Development or production environment
- `FLASK_APP`: Path to Flask application entry point

## Deployment & CI/CD

### Environments
- **Development**: For active development and testing
- **Staging**: For pre-production validation
- **Production**: Live environment

### CI/CD Pipelines
- **GitHub Actions**: For automated testing and deployment
- **Docker**: For consistent build and deployment artifacts

### Deployment Process
1. Code pushed to GitHub repository
2. Automated tests run in CI environment
3. Docker image built and pushed to registry
4. Deployment to GCP services
5. Post-deployment verification

## Technical Constraints

### Performance Requirements
- Video processing within 2x real-time duration
- API response times < 200ms for non-processing endpoints
- Support for videos up to 4K resolution

### Security Requirements
- HTTPS for all endpoints
- JWT-based authentication
- Role-based access control
- Encryption for sensitive data at rest and in transit

### Scalability Goals
- Support concurrent processing of multiple videos
- Handle peak loads during high-traffic periods
- Automatic scaling based on demand 