# Auphonic Video Processing & YouTube Automation

## Vision

This project automates the process of taking raw video uploads, enhancing their audio quality using Auphonic, organizing the processed files, and ultimately uploading them to designated YouTube channels. The goal is to create a seamless, hands-off pipeline from raw video to published content, potentially including future steps like blog post generation and social media snippets.

## Benefits ✨

*   **Time Savings:** Automates tedious manual steps of audio processing and uploading.
*   **Consistent Quality:** Ensures all videos benefit from Auphonic's audio enhancement presets.
*   **Organized Assets:** Automatically structures processed files (audio, video, transcripts) in GCS for easy access.
*   **Scalability:** Handles uploads for multiple channels (e.g., daily vs. main) based on input folder.
*   **Extensibility:** Designed with future automations (blogging, social media) in mind.

## Workflow Overview

```mermaid
graph LR
    A[Video Uploaded to GCS raw-* folder] --> B(Cloud Function: trigger_auphonic);
    B -- Fetches API Key --> C(Secret Manager);
    B -- Calls Auphonic API --> D(Auphonic);
    D -- Processes Audio --> E{GCS processed-* folder\
    (Structured Output)};
    E --> F(Future: YouTube Upload Function);
    F --> G(YouTube Channel);
    E --> H(Future: Content Gen Function);
    H --> I(Blog Posts, Social Media);
```

1.  **Upload:** A raw video file (`.mp4`, etc.) is uploaded to a specific folder in the GCS Bucket (`raw-daily/` or `raw-main/`).
2.  **Trigger:** The GCS upload triggers the `trigger_auphonic` Cloud Function.
3.  **Auth & API Call:** The function retrieves the Auphonic API key from Secret Manager and calls the Auphonic API, specifying the input file (using its relative GCS path), the appropriate preset/service UUID based on the input folder, and a structured output path (e.g., `processed-daily/video_title/`).
4.  **Auphonic Processing:** Auphonic accesses the file from GCS (via its configured External Service integration), processes the audio according to the preset, and saves the output files to the specified structured folder within the GCS bucket.
5.  **(Future) Downstream Processing:** Subsequent functions will be triggered by new files appearing in the `processed-*` folders to handle YouTube uploads, content generation, etc.

## Key Terms

*   **GCS (Google Cloud Storage):** The service used for storing all video files (raw input, processed output).
    *   `raw-daily/`, `raw-main/`: Input folders where initial videos are uploaded.
    *   `processed-daily/`, `processed-main/`: Output parent folders where Auphonic results are stored.
    *   `processed-*/video_title/`: Structured folders created by the automation to hold all assets for a single processed video.
*   **Auphonic:** An external web service used for automatic audio post-production (leveling, noise reduction, etc.).
*   **Cloud Functions:** Serverless functions hosted on Google Cloud used to run the automation code.
*   **Secret Manager:** Google Cloud service for securely storing API keys and other secrets.
*   **Eventarc:** Google Cloud service used to connect events (like GCS uploads) to triggers for services like Cloud Functions.
*   **Service Account:** Google Cloud identity used by services (like Cloud Functions, GCS, Eventarc) to interact with other services and APIs.

## Core Components

*   **`main.py`:** Contains the primary Cloud Function `trigger_auphonic`.
    *   Triggered by GCS `object.finalize` events.
    *   Parses event data to get bucket/file name.
    *   Determines Auphonic preset/service based on input folder.
    *   Constructs structured output path.
    *   Retrieves API key from Secret Manager.
    *   Calls the Auphonic API (`/api/productions.json`) to start processing.
*   **`requirements.txt`:** Lists Python dependencies (`functions-framework`, `requests`, `google-cloud-secret-manager`, `google-cloud-storage`).
*   **`tasks/` directory:** Contains tasks managed by Task Master AI for project development.
*   **(Planned) YouTube Upload Functions:** Future components to handle uploading processed videos from `processed-*` folders to YouTube.
*   **(Planned) Content Generation Functions:** Future components to generate blog posts/social media content.

## Getting Started

### Prerequisites

1.  **Google Cloud Project:** An active GCP project.
2.  **Google Cloud SDK (`gcloud`):** Installed and authenticated (`gcloud auth login`, `gcloud config set project YOUR_PROJECT_ID`).
3.  **Python & Pip:** Python 3.10+ recommended.
4.  **Virtual Environment:** Recommended (e.g., `python -m venv venv`, `source venv/bin/activate`).
5.  **Auphonic Account:** Account with API access enabled.
6.  **GCS Bucket:** Created in a specific region (e.g., `us-east1`).
7.  **Auphonic API Key:** Stored in Google Secret Manager (e.g., secret ID `auphonic-api-key`).
8.  **Auphonic Presets & External Services:**
    *   Auphonic presets created for different processing needs (e.g., daily vs. main channel).
    *   Google Cloud Storage configured as an External Service in Auphonic, linked to your GCS bucket (this allows Auphonic to read input and write output). Note the Service UUIDs.

### Setup & Configuration

1.  **Clone Repository:** (Assuming it's created based on Task 12)
    ```bash
    git clone git@github.com:parkerrex/Automations.git
    cd Automations
    ```
2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure `main.py`:**
    *   Update `PROJECT_ID` if different from `automations-457120`.
    *   Update `SECRET_ID` if different from `auphonic-api-key`.
    *   Update `PRESETS` dictionary with your actual Auphonic Preset UUIDs.
    *   Update `SERVICES` dictionary with your actual Auphonic GCS External Service UUIDs.
5.  **GCP Service Account Permissions:** Ensure the service account used for the Cloud Function (`gcsfuse-automation@...` in the example) has roles:
    *   `Secret Manager Secret Accessor` (to get API key)
    *   `Cloud Functions Developer` (or Invoker/Admin as needed)
    *   Any roles needed to interact with GCS if not already covered.
6.  **GCP API Enablement:** Ensure these APIs are enabled in your project:
    *   Cloud Functions API
    *   Cloud Build API
    *   Eventarc API
    *   Secret Manager API
    *   Cloud Storage API
    *   (Potentially others depending on future functions)
7.  **Eventarc & GCS Service Agent Permissions:** As encountered during deployment, ensure:
    *   The Eventarc Service Agent (`service-<PROJECT_NUMBER>@gcp-sa-eventarc.iam.gserviceaccount.com`) has `roles/eventarc.eventReceiver`.
    *   The GCS Service Account (`service-<PROJECT_NUMBER>@gs-project-accounts.iam.gserviceaccount.com`) has `roles/pubsub.publisher`.

### Deployment

Deploy the main Cloud Function using `gcloud`. **Ensure the `--region` matches your GCS bucket's region.**

```bash
gcloud functions deploy trigger-auphonic \
  --gen2 \
  --runtime=python310 \
  --region=YOUR_GCS_BUCKET_REGION \
  --source=. \
  --entry-point=trigger_auphonic \
  --trigger-event=google.storage.object.finalize \
  --trigger-resource=YOUR_GCS_BUCKET_NAME \
  --service-account=YOUR_FUNCTION_SERVICE_ACCOUNT_EMAIL \
  --set-env-vars=GCS_BUCKET=YOUR_GCS_BUCKET_NAME
```

Replace `YOUR_GCS_BUCKET_REGION`, `YOUR_GCS_BUCKET_NAME`, and `YOUR_FUNCTION_SERVICE_ACCOUNT_EMAIL` with your specific values.

## Contributing

(Placeholder - Add guidelines later if applicable)

## License

(Placeholder - Specify license, e.g., MIT, Apache 2.0)
