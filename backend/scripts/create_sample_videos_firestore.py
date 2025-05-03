import os

from google.cloud import firestore

# Path to service account key
SERVICE_ACCOUNT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../credentials/service_account.json")
)


def main():
    # Set the environment variable for authentication
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH

    # Initialize Firestore client
    db = firestore.Client()

    # Sample video documents
    videos = [
        {
            "title": "My First Video",
            "status": "Thumbnail Generation",
            "channel": "Main",
            "scheduledTime": "2025-05-01T10:00:00Z",
            "metadata": {"scheduled_time": "2025-05-01T10:00:00Z"},
        },
        {
            "title": "AI News Daily",
            "status": "Transcription",
            "channel": "Daily",
            "scheduledTime": "2025-05-02T09:00:00Z",
            "metadata": {"scheduled_time": "2025-05-02T09:00:00Z"},
        },
    ]

    # Add each video as a document in the "videos" collection
    for video in videos:
        doc_ref = db.collection("videos").document()
        doc_ref.set(video)
        print(f"Added video: {video['title']} (ID: {doc_ref.id})")


if __name__ == "__main__":
    main()
