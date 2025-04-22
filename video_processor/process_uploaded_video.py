import os
import tempfile
import logging
import json

from google.cloud import storage, aiplatform
from vertexai.preview.generative_models import GenerativeModel
import subprocess
import vertexai
from unittest.mock import MagicMock

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "automations-457120")
REGION = "us-central1"
MODEL = "gemini-2.0-flash-001"

# Check if we're in testing mode
TESTING_MODE = os.environ.get("TESTING_MODE", "false").lower() == "true"

# Check if we're in real API test mode
REAL_API_TEST = os.environ.get("REAL_API_TEST", "false").lower() == "true"

# Check if we should write outputs to local filesystem
LOCAL_OUTPUT = os.environ.get("LOCAL_OUTPUT", "false").lower() == "true" or TESTING_MODE

# Initialize clients with appropriate configuration
if TESTING_MODE:
    # In testing mode, always use mock clients
    from unittest.mock import MagicMock

    # Create a mock storage client for testing
    storage_client = MagicMock()
    logging.info("Using mock storage client for testing")

    # Create mock bucket and blob methods
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    storage_client.bucket = MagicMock(return_value=mock_bucket)
    mock_bucket.blob = MagicMock(return_value=mock_blob)
    mock_bucket.copy_blob = MagicMock()
    mock_blob.upload_from_string = MagicMock()
    mock_blob.download_to_filename = MagicMock()
    mock_blob.delete = MagicMock()

    # Skip Vertex AI initialization in testing mode
    logging.info("Skipping Vertex AI initialization in testing mode")
    model = MagicMock()
    # Mock the generate_content method
    model.generate_content = MagicMock(
        return_value=MagicMock(
            text="This is a mock response from Gemini API in testing mode."
        )
    )
else:
    # Normal initialization for production
    storage_client = storage.Client()
    aiplatform.init(project=PROJECT_ID, location=REGION)
    vertexai.init(project=PROJECT_ID, location=REGION)
    # Load the Gemini model - Specify the correct model name
    model = GenerativeModel(MODEL)


def generate_transcript(audio_part):
    """Generates a full transcript from audio data using a specific model."""
    if TESTING_MODE:
        # In testing mode, return a mock transcript
        logging.info("TESTING MODE: Returning mock transcript")
        return "This is a mock transcript for testing purposes. It simulates what would be returned by the Gemini API in production."
    else:
        # Use a model optimized for transcription if needed
        transcription_model = GenerativeModel("gemini-2.0-flash-001")
        prompt = "Generate a transcription of the audio, only extract speech and ignore background audio."
        response = transcription_model.generate_content(  # Use the specific model
            [prompt, audio_part],
            generation_config={"temperature": 0.2},  # Lower temp for accuracy
        )
        # Add basic error handling or validation if needed
        return response.text.strip()


def generate_vtt(audio_part):
    """Generates VTT subtitles from audio data."""
    if TESTING_MODE:
        # In testing mode, return mock VTT subtitles
        logging.info("TESTING MODE: Returning mock VTT subtitles")
        return """WEBVTT

00:00:00.000 --> 00:00:05.000
This is a mock subtitle for testing purposes.

00:00:05.000 --> 00:00:10.000
It simulates what would be returned by the Gemini API in production."""
    else:
        vtt_model = GenerativeModel("gemini-2.0-flash-001")
        prompt = (
            "Generate subtitles in VTT format for the following audio. Ensure accurate timing.\\n"
            "Example format:\\n"
            "WEBVTT\\n\\n"
            "00:00:00.000 --> 00:00:05.000\\n"
            "Hello everyone and welcome back.\\n\\n"
            "00:00:05.500 --> 00:00:10.000\\n"
            "Today we are discussing..."
        )
        response = vtt_model.generate_content(
            [prompt, audio_part],
            # VTT can be long
            generation_config={"max_output_tokens": 4096, "temperature": 0.5},
        )
        # Add basic error handling or validation if needed
        # Ensure it starts with WEBVTT
        text = response.text.strip()
        if not text.startswith("WEBVTT"):
            text = "WEBVTT\\n\\n" + text  # Attempt basic correction
        return text


def generate_shownotes(audio_part):
    """Generates detailed shownotes from audio data."""
    if TESTING_MODE:
        # In testing mode, return mock shownotes
        logging.info("TESTING MODE: Returning mock shownotes")
        return """# Mock Shownotes for Testing

## Key Takeaways
- This is a mock shownote for testing purposes
- It simulates what would be returned by the Gemini API in production

## Resources Mentioned
- Example resource 1: https://example.com
- Example resource 2: https://test.com

## Timestamps
- 00:00 - Introduction
- 02:30 - Main topic discussion
- 05:45 - Conclusion"""
    else:
        prompt = (
            "Analyze the following audio and generate detailed shownotes. Include key takeaways, "
            "any mentioned links or resources, and relevant timestamps for important points."
        )
        shownotes_model = GenerativeModel("gemini-2.0-flash-001")
        response = shownotes_model.generate_content(
            [prompt, audio_part],
            generation_config={"max_output_tokens": 2048, "temperature": 0.7},
        )
        # Add basic error handling or validation if needed
        return response.text.strip()


def generate_chapters(audio_part):
    """Generates timestamped chapters with summaries from audio data."""
    if TESTING_MODE:
        # In testing mode, return mock chapters
        logging.info("TESTING MODE: Returning mock chapters")
        return [
            {"timecode": "00:00", "chapterSummary": "Introduction to the mock video"},
            {
                "timecode": "02:00",
                "chapterSummary": "First main point in the mock video",
            },
            {
                "timecode": "04:00",
                "chapterSummary": "Second main point in the mock video",
            },
            {"timecode": "06:00", "chapterSummary": "Conclusion of the mock video"},
        ]
    else:
        # Updated prompt asking for JSON output
        chapters_model = GenerativeModel("gemini-2.0-flash-001")
        prompt = (
            "Chapterize the video content by grouping the content into chapters and providing a summary for each chapter. "
            "Please only capture key events and highlights. If you are not sure about any info, please do not make it up. "
            'Return the result ONLY as a valid JSON array of objects, where each object has the keys "timecode" (string, e.g., "00:00") '
            'and "chapterSummary" (string). Aim for chapters roughly every 2 minutes.\\n'
            "Example JSON output format:\\n"
            "[\\n"
            '  {\\"timecode\\": \\"00:00\\", \\"chapterSummary\\": \\"Introduction to the topic...\\"},\\n'
            '  {\\"timecode\\": \\"02:01\\", \\"chapterSummary\\": \\"Discussing the first main point...\\"}\\n'
            "]"
        )
    response = chapters_model.generate_content(  # Use the specific model
        [prompt, audio_part],
        generation_config={
            "temperature": 0.6,
            "response_mime_type": "application/json",
        },  # Request JSON output
    )

    # Parse the JSON response
    try:
        # The response text should be a valid JSON string
        chapter_list = json.loads(response.text)
        # Basic validation: check if it's a list of dicts with required keys
        if not isinstance(chapter_list, list) or not all(
            isinstance(item, dict) and "timecode" in item and "chapterSummary" in item
            for item in chapter_list
        ):
            raise ValueError("Parsed JSON is not a list of chapter objects.")
        return chapter_list
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(
            f"Failed to parse chapters JSON: {e}. Raw response: {response.text}"
        )
        # Return an empty list or raise an error, depending on desired handling
        return []


def generate_titles(audio_part):
    """Generates title and keywords as a dictionary from audio data."""
    if TESTING_MODE:
        # In testing mode, return mock title and keywords
        logging.info("TESTING MODE: Returning mock title and keywords")
        return {
            "Description": "Mock Video Title for Testing Purposes",
            "Keywords": "testing,mock,video,automation,example,demo,sample,test,keywords,tags",
        }
    else:
        # Use a specific model if desired
        title_model = GenerativeModel("gemini-2.0-flash-001")
        prompt = (
            "Please write a 40-character long intriguing title for this video and 10 comma-separated hashtags "
            "suitable for YouTube Shorts based on the audio. Format the response strictly as a valid JSON object "
            "with two keys: 'Description' (containing the title, max 50 characters) and 'Keywords' "
            "(containing the comma-separated hashtags as a single string)."
        )
    response = title_model.generate_content(  # Use the specific model
        [prompt, audio_part],
        # Request JSON output
        generation_config={
            "temperature": 0.8,
            "response_mime_type": "application/json",
        },
    )

    # Parse the JSON response
    try:
        title_dict = json.loads(response.text)
        # Basic validation
        if (
            not isinstance(title_dict, dict)
            or "Description" not in title_dict
            or "Keywords" not in title_dict
        ):
            raise ValueError("Parsed JSON is not a dictionary with required keys.")
        return title_dict
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(
            f"Failed to parse title/keywords JSON: {e}. Raw response: {response.text}"
        )
        # Return a default dict or raise, depending on desired handling
        return {"Description": "Default Title", "Keywords": "default,keywords"}


def write_blob(bucket_name, blob_path, content):
    if LOCAL_OUTPUT:
        # In local output mode, write to the local filesystem
        # Determine the local path based on environment
        if os.path.exists("/app/test_data"):
            # Docker environment
            base_path = "/app/test_data"
        else:
            # Local environment
            base_path = "test_data"

        local_path = os.path.join(base_path, blob_path)
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # Write the content to the file
        with open(local_path, "w") as f:
            f.write(content)
        logging.info(f"Wrote {blob_path} to local file {local_path}")

    # If not in testing mode or in real API test mode, also write to GCS
    if not TESTING_MODE or REAL_API_TEST:
        # In production mode, write to GCS
        # Assuming storage_client is initialized globally or passed as an arg
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_string(content)
        logging.info(f"Uploaded {blob_path} to bucket {bucket_name}")


# Rename function and change signature to accept bucket and file name directly
def process_video_event(bucket_name, file_name):
    logging.info(f"Processing video event for gs://{bucket_name}/{file_name}")

    # Assuming storage_client is initialized globally
    if not file_name.endswith(".mp4") or not file_name.startswith(
        ("daily-raw/", "main-raw/")
    ):
        logging.info(f"Skipping non-target file: {file_name}")
        return

    base_name = os.path.splitext(os.path.basename(file_name))[0]
    # Replace spaces with hyphens in the base name for better compatibility
    base_name_normalized = base_name.replace(" ", "-")
    channel = "daily" if file_name.startswith("daily-raw/") else "main"
    processed_path = f"processed-{channel}/{base_name_normalized}/"

    logging.info(f"Original base name: {base_name}")
    logging.info(f"Normalized base name: {base_name_normalized}")
    logging.info(f"Processed path: {processed_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, base_name + ".mp4")
        audio_path = os.path.join(tmpdir, base_name + ".wav")

        # Download video
        logging.info(f"Downloading {file_name} to {video_path}...")

        if TESTING_MODE:
            # In testing mode, create a dummy file instead of downloading
            logging.info(
                "TESTING MODE: Creating dummy video file instead of downloading"
            )
            try:
                # Create a small dummy MP4 file
                with open(video_path, "wb") as f:
                    f.write(b"DUMMY MP4 FILE")
                logging.info("Created dummy video file for testing.")
                # Create a mock blob for later operations
                bucket = MagicMock()
                blob = MagicMock()
            except Exception as e:
                logging.error(f"Failed to create dummy file: {e}")
                raise
        else:
            # Normal download in production mode
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file_name)
            try:
                blob.download_to_filename(video_path)
                logging.info("Download complete.")
            except Exception as e:
                logging.error(f"Failed to download {file_name}: {e}")
                raise

        # Extract audio using ffmpeg
        logging.info(f"Extracting audio from {video_path} to {audio_path}...")

        if TESTING_MODE:
            # In testing mode, create a dummy WAV file instead of running ffmpeg
            logging.info(
                "TESTING MODE: Creating dummy WAV file instead of running ffmpeg"
            )
            try:
                # Create a small dummy WAV file
                with open(audio_path, "wb") as f:
                    # Write a minimal WAV header + some data
                    f.write(
                        b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
                    )
                logging.info("Created dummy WAV file for testing.")
            except Exception as e:
                logging.error(f"Failed to create dummy WAV file: {e}")
                raise
        else:
            # Normal ffmpeg processing in production mode
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",  # Overwrite output files without asking
                        "-i",
                        video_path,
                        "-vn",  # No video output
                        "-acodec",
                        "pcm_s16le",  # Standard WAV format
                        "-ar",
                        "16000",  # Audio sample rate
                        "-ac",
                        "1",  # Mono audio
                        audio_path,
                    ],
                    check=True,  # Raise exception on non-zero exit code
                    capture_output=True,  # Capture stderr/stdout
                    text=True,  # Decode stderr/stdout as text
                )
                logging.info("Audio extraction complete.")
            except subprocess.CalledProcessError as e:
                logging.error(f"ffmpeg failed: {e}\nStderr: {e.stderr}")
                raise
            except Exception as e:
                logging.error(f"Error during ffmpeg execution: {e}")
                raise

        # Call Gemini
        logging.info(f"Calling Gemini for {audio_path}...")
        try:
            from vertexai.preview.generative_models import Part

            # Read the audio file and create a proper Part object
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # Create a Part object with the correct MIME type
            audio_part = Part.from_data(mime_type="audio/wav", data=audio_bytes)

            # Pass the properly formatted audio part to the Gemini functions
            transcript = generate_transcript(audio_part)
            subtitles_vtt = generate_vtt(audio_part)
            shownotes = generate_shownotes(audio_part)
            chapters_json = generate_chapters(audio_part)
            title_dict = generate_titles(audio_part)
            logging.info("Gemini processing complete.")
        except Exception as e:
            logging.error(f"Gemini API call failed: {e}")
            raise

        # Format chapters JSON into a string for the text file
        chapters_text = "\\n".join(
            [f"{ch['timecode']} - {ch['chapterSummary']}" for ch in chapters_json]
        )

        # Extract title and keywords
        video_title = title_dict.get("Description", "Default Title")
        # Store keywords for potential future use
        # video_keywords = title_dict.get("Keywords", "default,keywords")

        # Write blobs
        logging.info(f"Uploading results to gs://{bucket_name}/{processed_path}...")
        try:
            write_blob(bucket_name, processed_path + "transcript.txt", transcript)
            # Save subtitles as .vtt
            write_blob(bucket_name, processed_path + "subtitles.vtt", subtitles_vtt)
            write_blob(bucket_name, processed_path + "shownotes.txt", shownotes)
            write_blob(
                bucket_name, processed_path + "chapters.txt", chapters_text
            )  # Use formatted text
            write_blob(
                bucket_name, processed_path + "title.txt", video_title
            )  # Save only the title
            # TODO: Decide how to save/use video_keywords
            logging.info("Result uploads complete.")

            # --- Move original video file to processed folder ---
            try:
                destination_blob_name = processed_path + os.path.basename(file_name)
                logging.info(
                    f"Moving original file {file_name} to {destination_blob_name}..."
                )

                if LOCAL_OUTPUT:
                    # In local output mode, move the file in the local filesystem
                    # Determine the local path based on environment
                    if os.path.exists("/app/test_data"):
                        # Docker environment
                        base_path = "/app/test_data"
                    else:
                        # Local environment
                        base_path = "test_data"

                    source_path = os.path.join(base_path, file_name)
                    dest_path = os.path.join(base_path, destination_blob_name)
                    # Create the directory if it doesn't exist
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    # Copy the file
                    if os.path.exists(source_path):
                        import shutil

                        shutil.copy2(source_path, dest_path)
                        # Delete the original file if not in real API test mode
                        if not REAL_API_TEST:
                            os.remove(source_path)
                        logging.info(
                            f"Successfully moved local file from {source_path} to {dest_path}"
                        )
                    else:
                        logging.warning(
                            f"Source file {source_path} does not exist for local move"
                        )

                # If not in testing mode or in real API test mode, also move in GCS
                if not TESTING_MODE or REAL_API_TEST:
                    # In production mode, move the file in GCS
                    # blob refers to the original blob object fetched earlier for download
                    bucket.copy_blob(blob, bucket, destination_blob_name)
                    blob.delete()  # Delete the original blob after successful copy

                logging.info(
                    f"Successfully moved original file to {destination_blob_name}"
                )
            except Exception as move_error:
                # Log error but don't fail the entire process if move fails
                logging.error(
                    f"Failed to move original file {file_name} to {destination_blob_name}: {move_error}"
                )
            # --- End move original video file ---

        except Exception as e:
            logging.error(f"Failed to upload results: {e}")
            raise

    logging.info(f"Successfully processed gs://{bucket_name}/{file_name}")
