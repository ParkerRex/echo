# 🎬 Video Upload + AI Metadata Pipeline

This repo powers the automation pipeline for uploading `.mp4` files to YouTube with AI-generated transcripts, titles, chapters, and descriptions — using Google Cloud Run + Gemini via Vertex AI.

## 🌟 Project Overview

The Video Upload + AI Metadata Pipeline automates the process of preparing video content for YouTube. It takes raw video files, processes them using AI to generate high-quality metadata, and uploads them to YouTube. This system dramatically reduces the manual work involved in video publishing while ensuring consistent, high-quality metadata.

### Key Features

- **Automated Video Processing**: Upload videos to GCS buckets and trigger automatic processing
- **AI-Generated Metadata**: Generate transcripts, titles, descriptions, and chapters using Gemini AI
- **Flexible Processing Paths**: Support for both daily content and main channel content
- **YouTube Integration**: Automatic upload to YouTube with proper metadata and captions
- **Comprehensive Testing**: Robust test suite for reliable operation
- **Scalable Architecture**: Cloud-native design that scales with your content needs

---
## Deployment Workflows

There are two primary ways to deploy this application to Cloud Run:

**1. Direct Source Deployment (Current Method):**

This is the simplest method for quick deployments directly from your local source code. Google Cloud Build handles the container building and pushing behind the scenes.

-   **Command:** `gcloud run deploy process-uploaded-video --source . --region <your-region>`
-   **Pros:** Simple, fewer manual steps.
-   **Cons:** Less control over the build process, can potentially lead to architecture mismatches (like the `exec format error` if building on ARM and deploying to x86) if not careful.

```mermaid
flowchart TD
    subgraph "Local Development"
        A[📝 Code (main.py, etc.)] --> B(📄 Dockerfile);
        C[📋 requirements.txt] --> B;
    end

    subgraph "Google Cloud Build (Triggered by gcloud run deploy --source)"
        A & B & C -- gcloud run deploy --source . --> D[Builds Image];
        D --> E[Pushes to Ephemeral Registry];
    end

    subgraph "Google Cloud Run"
        E -- Implicitly --> F[🚀 Cloud Run Service];
        F -- Pulls Image & Runs --> G[🏃 Container Instance(s)];
    end

    G --> H[👂 Listens for Events (e.g., GCS Upload)];
```

**2. Build & Push to Artifact Registry (Recommended):**

This method gives you more control, ensures architecture compatibility, and is the standard for production environments.

1.  **`Dockerfile` (Blueprint):** Defines how to build the container image.
2.  **`docker buildx build --platform linux/amd64 ... --push` (Factory & Delivery):** Builds the image specifically for Cloud Run's `linux/amd64` architecture and pushes it to Artifact Registry.
3.  **Artifact Registry (Warehouse):** Stores your versioned Docker images.
4.  **`gcloud run deploy --image ...` (Runner):** Tells Cloud Run to pull a specific image tag from Artifact Registry and run it.

```mermaid
flowchart TD
    subgraph "Local Development"
        AA[📝 Code (main.py, etc.)] --> BB(📄 Dockerfile);
        CC[📋 requirements.txt] --> BB;
        BB -- docker buildx build --platform linux/amd64 --> DD[📦 Docker Image (amd64)];
    end

    subgraph "Google Cloud"
        DD -- docker push --> EE[🏪 Artifact Registry];
        EE -- gcloud run deploy --image --> FF[🚀 Cloud Run Service];
        FF -- Pulls Image & Runs --> GG[🏃 Container Instance(s)];
    end

    GG --> HH[👂 Listens for Events (e.g., GCS Upload)];

    AA --> CC;
```

**Important Note: CPU Architecture Mismatch (ARM64 vs. AMD64)**

-   **The Problem:** Google Cloud Run instances typically use the `linux/amd64` (also known as x86_64) CPU architecture. However, modern Macs with Apple Silicon (M1/M2/M3) use the `linux/arm64` (or aarch64) architecture.
-   **The Error:** If you build a Docker image *without* specifying the platform on an ARM-based Mac, Docker defaults to building an `arm64` image. Trying to run this `arm64` image on Cloud Run's `amd64` environment results in an `exec format error` because the underlying operating system doesn't understand the compiled code's instruction set.
-   **Workflow A Solution:** The `docker buildx build --platform linux/amd64 ...` command explicitly tells Docker (even on your ARM Mac) to cross-compile and build the image for the `linux/amd64` architecture that Cloud Run requires. This guarantees compatibility.
-   **Workflow B Caveat:** While `gcloud run deploy --source .` usually lets Cloud Build handle this correctly behind the scenes, subtle build environment issues can sometimes occur. Using Workflow A (Build & Push) provides more direct control and was used in this project's troubleshooting to definitively resolve the `exec format error`.

## Current Workflow Diagram (GCS -> Cloud Run -> Processing -> YouTube)

```mermaid
flowchart TD
  A[📤 Upload .mp4 to daily-raw/ or main-raw/] --> B[🗂️ GCS Bucket]

  B --> C[🔔 Eventarc Trigger]
  C --> D[🚀 Cloud Run (process-uploaded-video)]

  D --> E[📥 app.py handles POST /]
  E --> F[🧠 process_uploaded_video.py]

  F --> G[🔊 Extract audio via ffmpeg]
  G --> H[🤖 Gemini (Vertex AI)
transcript + metadata]

  H --> I[📂 processed-daily/ or processed-main/
transcript.txt, title.txt, etc.]

  I --> J[🔔 Eventarc Trigger]
  J --> K[⬆️ Upload to YouTube (via Cloud Function)]
```


## 🧠 Architecture Overview

### Complete System Architecture

```mermaid
flowchart TD
  %% User Actions
  User([Content Creator]) -->|Uploads| A[.mp4 Video File]
  A -->|Placed in| B[GCS Bucket]

  %% Storage Paths
  B -->|For daily content| B1[daily-raw/]
  B -->|For main channel| B2[main-raw/]

  %% Event Triggering
  B1 & B2 -->|Triggers| C[Eventarc]
  C -->|Invokes| D[Cloud Run Service]

  %% Video Processing Module
  subgraph "Video Processor Module"
    D -->|Handles request| E[app.py]
    E -->|Calls| F[process_uploaded_video.py]
    F -->|Downloads video| G[Temporary Storage]
    G -->|Extracts audio| H[ffmpeg]
    H -->|Creates| I[WAV Audio File]

    %% AI Processing
    I -->|Sent to| J[Vertex AI]
    J -->|Processes with| K[Gemini 2.0 Model]

    %% Generated Outputs
    K -->|Generates| L1[Transcript]
    K -->|Generates| L2[VTT Subtitles]
    K -->|Generates| L3[Shownotes]
    K -->|Generates| L4[Chapters JSON]
    K -->|Generates| L5[Title & Keywords]

    %% Output Processing
    L1 & L2 & L3 & L4 & L5 -->|Formatted as| M[Output Files]
    M -->|Uploaded to| N[GCS Bucket]
  end

  %% Output Storage
  N -->|For daily content| N1[processed-daily/]
  N -->|For main channel| N2[processed-main/]

  %% YouTube Upload
  N1 & N2 -->|Triggers| O[YouTube Upload Function]
  O -->|Authenticates with| P[YouTube API]
  P -->|Creates| Q[YouTube Video]
  O -->|Uploads| R[Captions/Subtitles]

  %% Testing & Monitoring
  subgraph "Testing & Monitoring"
    S1[pytest Suite] -->|Verifies| F
    S2[Cloud Monitoring] -->|Tracks| D
    S3[Error Logging] -->|Captures| U[System Errors]
  end

  %% Styling
  classDef storage fill:#f9f,stroke:#333,stroke-width:2px;
  classDef processing fill:#bbf,stroke:#333,stroke-width:2px;
  classDef ai fill:#bfb,stroke:#333,stroke-width:2px;
  classDef output fill:#fbb,stroke:#333,stroke-width:2px;

  class B,B1,B2,G,N,N1,N2 storage;
  class D,E,F,H,O storage;
  class J,K ai;
  class L1,L2,L3,L4,L5,M,Q,R output;
```

### Core Processing Flow

```mermaid
flowchart TD
  subgraph User
    A[Drop .mp4 into daily-raw/ or main-raw/]
  end

  subgraph GCS
    B[daily-raw/] --> C[Eventarc Trigger]
    D[main-raw/] --> C
  end

  subgraph CloudRun
    C --> E[process-uploaded-video Service]
    E --> F[Extract Audio with ffmpeg]
    F --> G[Transcribe + Summarize with Gemini]
    G --> H1[transcript.txt]
    G --> H2[description.txt]
    G --> H3[title.txt]
    G --> H4[chapters.txt]
    G --> H5[subtitles.vtt]
    H1 & H2 & H3 & H4 & H5 --> I[processed-daily/ or processed-main/]
  end

  subgraph YouTubeUploader
    I --> J[Eventarc Trigger]
    J --> K[upload_to_youtube Cloud Function]
    K --> L[YouTube Upload Complete ✅]
  end
```

### Video Processor Module Detail

```mermaid
flowchart TD
  A[GCS Event] --> B[Cloud Run Service]
  B --> C[app.py]
  C --> D[process_uploaded_video.py]

  D --> E{Valid MP4?}
  E -->|No| F[Skip Processing]
  E -->|Yes| G[Download Video]

  G --> H[Extract Audio]
  H --> I[Create Part Object]

  I --> J1[generate_transcript]
  I --> J2[generate_vtt]
  I --> J3[generate_shownotes]
  I --> J4[generate_chapters]
  I --> J5[generate_titles]

  J1 & J2 & J3 & J4 & J5 --> K[Upload Results to GCS]
  K --> L[Move Original to Processed Folder]
```

---

## 🔧 Components

### Core Components

All components are now organized in the `video_processor/` directory for better modularity and containerization:

| Component                                   | Description                                            |
| ------------------------------------------- | ------------------------------------------------------ |
| `video_processor/process_uploaded_video.py` | Core module that extracts audio and uses Gemini        |
| `video_processor/main.py`                   | Cloud Run service entry point for handling GCS events  |
| `video_processor/app.py`                    | Flask app for the video processor service              |
| `video_processor/youtube_uploader.py`       | Cloud Function for uploading videos to YouTube         |
| `video_processor/generate_youtube_token.py` | Utility for generating YouTube API OAuth tokens        |
| `video_processor/tests/`                    | Comprehensive test suite for all functionality         |
| `Dockerfile`                                | Custom container to support ffmpeg and Vertex          |
| Eventarc trigger                            | Links GCS uploads to Cloud Run                         |
| Vertex AI (Gemini 2.0)                      | Handles transcription, title generation, and summaries |

### Testing Framework

The project includes a comprehensive testing framework to ensure reliability:

| Component                                              | Description                                |
| ------------------------------------------------------ | ------------------------------------------ |
| `video_processor/tests/conftest.py`                    | Common pytest fixtures for testing         |
| `video_processor/tests/test_*_generation.py`           | Unit tests for each generation function    |
| `video_processor/tests/test_process_video_event.py`    | Tests for the main processing function     |
| `video_processor/tests/test_main.py`                   | Tests for the Flask app and event handling |
| `video_processor/tests/test_youtube_uploader.py`       | Tests for YouTube upload functionality     |
| `video_processor/tests/test_generate_youtube_token.py` | Tests for OAuth token generation           |
| `video_processor/test_audio_processing.py`             | Standalone test for audio processing       |
| `video_processor/test_process_video.py`                | Standalone test for end-to-end processing  |

---

## 🐛 Recent Bug Fixes & Improvements

### Code Reorganization and Improved Testability

We've recently reorganized the codebase to improve modularity, testability, and containerization:

1. **Unified Module Structure:** Moved all code into the `video_processor/` directory for better organization
2. **Improved Testability:** Refactored `main.py` to use dependency injection for better testing
3. **Consolidated Docker Setup:** Combined multiple Dockerfiles into a single, optimized container definition
4. **Comprehensive Testing:** Added tests for all components, including YouTube integration

### Audio Format for Gemini API

We recently fixed an issue where raw binary WAV audio data was being passed directly to the Gemini API, which expects a properly formatted Part object with the correct MIME type.

#### Problem
The error occurred when trying to process audio data with Gemini API:
```
ERROR:root:Gemini API call failed: Unexpected item type: b'RIFF\xf0j=\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00LIST\x1a\x00\x00\x00INFOISFT\x0e\x00\x00\x00Lavf59.27.100\x00data\xaaj=\x00...
```

#### Solution
1. Modified the code to use the `Part.from_data()` method to properly format the audio data with the correct MIME type
2. Updated all Gemini API functions to accept the properly formatted audio part
3. Fixed environment variable issues by using hardcoded project ID instead of relying on environment variables
4. Added comprehensive test suite to prevent similar issues in the future

### Comprehensive Test Suite

We've added a robust test suite to ensure the reliability of the video processing pipeline:

1. **Unit Tests:** Tests for each generation function in isolation
2. **Integration Tests:** Tests for the end-to-end processing workflow
3. **Mocking:** Proper mocking of external dependencies like Vertex AI, GCS, and YouTube API
4. **Dependency Injection:** Refactored code to use dependency injection for better testability
5. **Documentation:** Detailed documentation on how to run tests and what to look for

See the `video_processor/README.md` file for more details on the testing framework.

---

## 🔜 Future Development

See the [ROADMAP.md](./ROADMAP.md) file for a detailed list of planned features and improvements, ranked by impact vs. effort.

---

## 📝 Usage & Expected Outcomes

1.  **Upload:** Drop your `.mp4` video file into the GCS bucket `automations-youtube-videos-2025`.
2.  **Trigger:** The Eventarc trigger detects the new file and invokes the `video-processor` Cloud Run service.
3.  **Processing:**
    *   Cloud Run downloads the video.
    *   `ffmpeg` extracts the audio into a `.wav` file.
    *   The audio is sent to Gemini (Vertex AI) for processing.
    *   Gemini returns the transcript, description, titles, and chapters.
4.  **Output:** The service writes the following files back to the GCS bucket:
    *   `transcript.txt`: Full text transcript of the video.
    *   `description.txt`: A short, engaging YouTube description.
    *   `title.txt`: Suggested clickbaity title.
    *   `chapters.txt`: Timestamped chapters for the video.
    *   `subtitles.vtt`: WebVTT format subtitles with timestamps.
5.  **YouTube Upload:** The service uploads the video to YouTube with the generated metadata and captions using the integrated YouTube uploader module.

---

## 🧪 Testing Framework

The project includes a comprehensive testing framework to ensure reliability and maintainability. The testing approach combines unit tests, integration tests, and standalone test scripts.

### Testing Architecture

```mermaid
flowchart TD
    A[pytest Test Suite] --> B1[Unit Tests]
    A --> B2[Integration Tests]
    B1 --> C1[Transcript Generation]
    B1 --> C2[VTT Generation]
    B1 --> C3[Chapters Generation]
    B1 --> C4[Titles Generation]
    B1 --> C5[Process Video Event]
    B2 --> D1[Audio Processing]
    B2 --> D2[End-to-End Processing]
    C1 & C2 & C3 & C4 & C5 --> E[Mock Gemini API]
    D1 --> F1[Real ffmpeg]
    D2 --> F1
    D1 --> F2[Mock Gemini API]
    D2 --> F3[Mock GCS]
```

### Implemented Tests

1. **Unit Tests (`pytest`):**
   * Tests for each generation function in isolation:
     * `test_transcript_generation.py`
     * `test_vtt_generation.py`
     * `test_chapters_generation.py`
     * `test_titles_generation.py`
   * Tests for the main processing function:
     * `test_process_video_event.py`
   * Tests for the main application:
     * `test_main.py`: Tests the Flask app and event handling
   * Tests for YouTube integration:
     * `test_youtube_uploader.py`: Tests YouTube upload functionality
     * `test_generate_youtube_token.py`: Tests OAuth token generation
   * **Mocking:** Uses `unittest.mock` to mock external dependencies:
     * `google.cloud.storage`: Mocks `storage.Client`, `bucket`, and `blob` interactions
     * `vertexai`: Mocks `GenerativeModel` and its `generate_content` method
     * `subprocess.run`: Mocks the `ffmpeg` call
     * `google.oauth2.credentials`: Mocks YouTube API credentials
     * `googleapiclient.discovery`: Mocks YouTube API service
     * `google.cloud.secretmanager`: Mocks Secret Manager client
   * **Test Cases:**
     * Normal operation with valid inputs
     * Edge cases with unusual inputs
     * Error handling for API failures
     * Handling of non-MP4 files or files in wrong directories
     * YouTube upload success and failure scenarios
     * OAuth token generation and storage

2. **Standalone Test Scripts:**
   * `test_audio_processing.py`: Tests audio extraction and processing with Gemini API
   * `test_process_video.py`: Tests the end-to-end video processing workflow

### Running Tests

```bash
# Navigate to the video_processor directory
cd video_processor

# Install test dependencies
pip install pytest pytest-mock pytest-cov

# Run all tests with coverage report
pytest

# Run specific test file
pytest tests/test_transcript_generation.py

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=. --cov-report=term-missing
```

### Common Testing Issues and Solutions

See the `video_processor/README.md` file for detailed information on common testing issues and solutions, including:

1. Mocking Vertex AI Part objects
2. Handling newline characters in tests
3. Patching the correct import paths
4. Debugging test failures

---

## 🚀 Deployment

The application is deployed as a Cloud Run service that responds to GCS events via Eventarc:

1. **Cloud Run Service**: Handles the video processing and AI integration
2. **Eventarc Trigger**: Connects GCS upload events to the Cloud Run service
3. **YouTube Uploader**: Integrated into the main service for video uploads

### Deployment Architecture

```mermaid
flowchart TD
    A[GCS Bucket] -->|Upload Video| B[Eventarc Trigger]
    B -->|Event Notification| C[Cloud Run Service]
    C -->|Process Video| D[Vertex AI Gemini]
    D -->|Return Metadata| C
    C -->|Store Results| A
    C -->|Upload Video| E[YouTube API]
```

### Deployment Steps

1. Run the deployment script to build and deploy the Cloud Run service:
   ```bash
   ./deploy.sh
   ```

   This script:
   - Runs tests to ensure everything is working
   - Builds a Docker image with the current code
   - Deploys the image to Cloud Run
   - Sets up Eventarc triggers if needed

2. Alternatively, deploy directly from source code:
   ```bash
   gcloud run deploy video-processor \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 3600 \
     --concurrency 10
   ```

3. Set up the Eventarc trigger:
   ```bash
   gcloud eventarc triggers create video-processor-trigger \
     --location=us-east1 \
     --destination-run-service=video-processor \
     --destination-run-region=us-central1 \
     --event-filters="type=google.cloud.storage.object.v1.finalized" \
     --event-filters="bucket=automations-youtube-videos-2025" \
     --service-account="vps-automations@automations-457120.iam.gserviceaccount.com"
   ```

---

## 🚀 CI/CD Setup (GitHub Actions)

A GitHub Actions workflow (`.github/workflows/deploy.yml`) can automate testing and deployment:

1.  **Trigger:** On push/merge to the `main` branch.

2.  **Jobs:**
    *   **`lint`:**
        *   Checkout code.
        *   Set up Python.
        *   Install dependencies (`requirements.txt`).
        *   Run linters (`flake8`, `black --check`).
    *   **`test`:**
        *   Checkout code.
        *   Set up Python.
        *   Install dependencies.
        *   Run unit tests (`pytest tests/`).
    *   **`build_and_deploy` (depends on `lint`, `test`):**
        *   Checkout code.
        *   Authenticate to Google Cloud (using Workload Identity Federation or Service Account Key secret).
        *   Configure Docker for Artifact Registry (`gcloud auth configure-docker ...`).
        *   Build multi-platform image using `docker buildx build --platform linux/amd64 ...` and push to Artifact Registry with a unique tag (e.g., Git SHA).
        *   Deploy to Cloud Run using the newly pushed image tag (`gcloud run deploy ... --image <artifact-registry-path>:<tag> ...`).

3.  **Secrets:** Store GCP service account keys or Workload Identity Federation configuration securely in GitHub repository secrets.

```mermaid
flowchart TD
    A[Push to main branch] --> B{GitHub Actions Trigger};
    B --> C[Lint Job];
    B --> D[Test Job];
    C --> E{Build & Deploy Job};
    D --> E;
    E --> F[Auth to GCP];
    F --> G[Configure Docker];
    G --> H[Build & Push Image (linux/amd64)];
    H --> I[Deploy to Cloud Run];
```

This setup ensures that code is automatically tested and deployed only if checks pass, preventing broken deployments and enabling safer collaboration.

