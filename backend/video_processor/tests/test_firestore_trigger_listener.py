import os
import time
import pytest
from unittest.mock import patch, MagicMock, call
from google.cloud import firestore

import firestore_trigger_listener as listener

# Mark all tests in this module as "integration" so they can be
# selectively run via `pytest -m integration`
pytestmark = pytest.mark.integration

TEST_COLLECTION = "videos_test"

@pytest.fixture(scope="module")
def firestore_client():
    # Use the same credentials as the main app, but a test collection
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = listener.SERVICE_ACCOUNT_PATH
    client = firestore.Client()
    yield client
    # Cleanup: delete all docs in the test collection after tests
    docs = client.collection(TEST_COLLECTION).stream()
    for doc in docs:
        doc.reference.delete()

def create_test_doc(client, doc_id, data):
    doc_ref = client.collection(TEST_COLLECTION).document(doc_id)
    doc_ref.set(data)
    return doc_ref

def update_test_doc(client, doc_id, updates):
    doc_ref = client.collection(TEST_COLLECTION).document(doc_id)
    doc_ref.update(updates)

def get_doc_data(client, doc_id):
    doc_ref = client.collection(TEST_COLLECTION).document(doc_id)
    return doc_ref.get().to_dict()

def run_listener_once(client, last_snapshots):
    # Simulate one iteration of the listener's polling logic
    docs = client.collection(TEST_COLLECTION).stream()
    for doc in docs:
        doc_id = doc.id
        data = doc.to_dict()
        prev = last_snapshots.get(doc_id)

        if prev is not None:
            for key, value in data.items():
                if key == "thumbnails" and "thumbnails" in prev:
                    for idx, thumb in enumerate(value):
                        prev_thumb = prev["thumbnails"][idx] if idx < len(prev["thumbnails"]) else {}
                        if thumb.get("prompt") != prev_thumb.get("prompt"):
                            listener.regenerate_thumbnail(doc_id, idx, thumb.get("prompt"))
                elif key in ["title", "tags", "description", "scheduledTime"]:
                    if value != prev.get(key):
                        listener.update_metadata(doc_id, {key: value})
        last_snapshots[doc_id] = data

def test_firestore_trigger_listener_metadata_update(firestore_client):
    doc_id = "test_video_1"
    initial_data = {
        "title": "Original Title",
        "tags": ["tag1"],
        "description": "Original description",
        "scheduledTime": "2025-05-01T10:00:00Z",
        "thumbnails": [{"prompt": "original prompt"}]
    }
    create_test_doc(firestore_client, doc_id, initial_data)
    last_snapshots = {doc_id: initial_data.copy()}

    # Simulate a metadata update
    updates = {"title": "New Title"}
    update_test_doc(firestore_client, doc_id, updates)

    with patch.object(listener, "update_metadata") as mock_update_metadata, \
         patch.object(listener, "regenerate_thumbnail") as mock_regen_thumb:
        run_listener_once(firestore_client, last_snapshots)
        mock_update_metadata.assert_called_once_with(doc_id, {"title": "New Title"})
        mock_regen_thumb.assert_not_called()

def test_firestore_trigger_listener_thumbnail_prompt_change(firestore_client):
    doc_id = "test_video_2"
    initial_data = {
        "title": "Title",
        "tags": ["tag1"],
        "description": "desc",
        "scheduledTime": "2025-05-01T10:00:00Z",
        "thumbnails": [{"prompt": "original prompt"}]
    }
    create_test_doc(firestore_client, doc_id, initial_data)
    last_snapshots = {doc_id: initial_data.copy()}

    # Simulate a thumbnail prompt change
    updates = {"thumbnails": [{"prompt": "new prompt"}]}
    update_test_doc(firestore_client, doc_id, updates)

    with patch.object(listener, "update_metadata") as mock_update_metadata, \
         patch.object(listener, "regenerate_thumbnail") as mock_regen_thumb:
        run_listener_once(firestore_client, last_snapshots)
        mock_regen_thumb.assert_called_once_with(doc_id, 0, "new prompt")
        mock_update_metadata.assert_not_called()
