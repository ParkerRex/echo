import os
import random
import string

from google.cloud import firestore

# Path to service account key
SERVICE_ACCOUNT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../credentials/service_account.json")
)


def random_string(length=6):
    return "".join(random.choices(string.ascii_letters, k=length))


def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
    db = firestore.Client()

    # Get the first video document
    videos_ref = db.collection("videos")
    docs = list(videos_ref.stream())
    if not docs:
        print("No video documents found.")
        return

    doc = docs[0]
    doc_id = doc.id
    data = doc.to_dict()

    # Simulate updating the title
    new_title = f"Simulated Title {random_string()}"
    print(f"Updating title of video {doc_id} to '{new_title}'")
    videos_ref.document(doc_id).update({"title": new_title})

    # Simulate updating a thumbnail prompt if thumbnails exist
    if (
        "thumbnails" in data
        and isinstance(data["thumbnails"], list)
        and data["thumbnails"]
    ):
        new_prompt = f"Simulated prompt {random_string()}"
        print(f"Updating thumbnails.0.prompt of video {doc_id} to '{new_prompt}'")
        videos_ref.document(doc_id).update({"thumbnails.0.prompt": new_prompt})


if __name__ == "__main__":
    main()
