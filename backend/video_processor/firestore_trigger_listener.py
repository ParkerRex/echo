import os
import time
from google.cloud import firestore

# Path to service account key
SERVICE_ACCOUNT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "../../@credentials/service_account.json"
))

def regenerate_thumbnail(video_id, thumbnail_idx, prompt):
    # Placeholder: implement actual thumbnail regeneration logic
    print(f"[THUMBNAIL] Regenerating thumbnail {thumbnail_idx} for video {video_id} with prompt: {prompt}")

def update_metadata(video_id, updated_fields):
    # Placeholder: implement actual metadata update logic
    print(f"[METADATA] Updating metadata for video {video_id}: {updated_fields}")

def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
    db = firestore.Client()

    videos_ref = db.collection("videos")

    # Store last seen document snapshots to detect changes
    last_snapshots = {}

    print("Listening for Firestore document changes in 'videos' collection...")

    while True:
        docs = videos_ref.stream()
        for doc in docs:
            doc_id = doc.id
            data = doc.to_dict()
            prev = last_snapshots.get(doc_id)

            if prev is not None:
                # Compare previous and current data to detect changes
                for key, value in data.items():
                    if key == "thumbnails" and "thumbnails" in prev:
                        # Check for prompt changes in thumbnails array
                        for idx, thumb in enumerate(value):
                            prev_thumb = prev["thumbnails"][idx] if idx < len(prev["thumbnails"]) else {}
                            if thumb.get("prompt") != prev_thumb.get("prompt"):
                                regenerate_thumbnail(doc_id, idx, thumb.get("prompt"))
                    elif key in ["title", "tags", "description", "scheduledTime"]:
                        if value != prev.get(key):
                            update_metadata(doc_id, {key: value})
                    # Add more field checks as needed

            # Update last snapshot
            last_snapshots[doc_id] = data

        time.sleep(2)  # Poll every 2 seconds

if __name__ == "__main__":
    main()
