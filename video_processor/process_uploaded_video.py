import os
import tempfile
import logging
import json

from google.cloud import storage, aiplatform
from vertexai.preview.generative_models import GenerativeModel
import subprocess
import vertexai

PROJECT_ID = "automations-457120"
REGION = "us-central1"
MODEL = "gemini-1.5-pro-preview-0409"

# Initialize clients potentially once per instance (trade-offs apply)
# For Cloud Run with low traffic/cold starts, initializing per-call might be simpler.
storage_client = storage.Client()
aiplatform.init(project=PROJECT_ID, location=REGION)

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=REGION)

# Load the Gemini model - Specify the correct model name
model = GenerativeModel("gemini-1.5-pro-preview-0409")


def generate_transcript(audio_part):
    """Generates a full transcript from audio data using a specific model."""
    # Use a model optimized for transcription if needed
    transcription_model = GenerativeModel("gemini-2.0-flash-001")
    prompt = "Generate a transcription of the audio, only extract speech and ignore background audio."
    response = transcription_model.generate_content(  # Use the specific model
        [prompt, audio_part],
        generation_config={"temperature": 0.2},  # Lower temp for accuracy
    )
    # Add basic error handling or validation if needed
    return response.text.strip()


# TODO: Define the model
def generate_vtt(audio_part):
    """Generates VTT subtitles from audio data."""
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


# TODO: Make this better
def generate_shownotes(audio_part):
    """Generates detailed shownotes from audio data."""
    prompt = (
        "Analyze the following audio and generate detailed shownotes. Include key takeaways, "
        "any mentioned links or resources, and relevant timestamps for important points."
    )
    response = model.generate_content(
        [prompt, audio_part],
        generation_config={"max_output_tokens": 2048, "temperature": 0.7},
    )
    # Add basic error handling or validation if needed
    return response.text.strip()


def generate_chapters(audio_part):
    """Generates timestamped chapters with summaries from audio data."""
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
    channel = "daily" if file_name.startswith("daily-raw/") else "main"
    processed_path = f"processed-{channel}/{base_name}/"

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, base_name + ".mp4")
        audio_path = os.path.join(tmpdir, base_name + ".wav")

        # Download video
        logging.info(f"Downloading {file_name} to {video_path}...")
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
        video_keywords = title_dict.get("Keywords", "default,keywords")

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
