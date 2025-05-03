import json
import logging
import os
import shutil
import subprocess
from unittest.mock import MagicMock

import vertexai
from google.cloud import aiplatform, storage
from vertexai.preview.generative_models import GenerativeModel, Part

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "automations-457120")
REGION = "us-east1"
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
    """Generates transcript from audio data."""
    if TESTING_MODE:
        # In testing mode, return a mock transcript
        logging.info("TESTING MODE: Returning mock transcript")
        return (
            "This is a mock transcript for testing purposes. "
            "It simulates what would be returned by the Gemini API in production."
        )
    else:
        # Use a model optimized for transcription if needed
        transcription_model = GenerativeModel("gemini-2.0-flash-001")
        prompt = (
            "Generate a transcription of the audio, only extract speech "
            "and ignore background audio."
        )
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
            "Generate subtitles in VTT format for the following audio. "
            "Ensure accurate timing.\\n"
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
            "Analyze the following audio and generate detailed shownotes. "
            "Include key takeaways, any mentioned links or resources, "
            "and relevant timestamps for important points."
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
            "Chapterize the video content by grouping the content into chapters "
            "and providing a summary for each chapter. "
            "Please only capture key events and highlights. "
            "If you are not sure about any info, please do not make it up. "
            "Return the result ONLY as a valid JSON array of objects, "
            "where each object "
            'has the keys "timecode" (string, e.g., "00:00") '
            'and "chapterSummary" (string). Aim for chapters roughly '
            "every 2 minutes.\\n"
            "Example JSON output format:\\n"
            "[\\n"
            '  {\\"timecode\\": \\"00:00\\", \\"chapterSummary\\": '
            '\\"Introduction to the topic...\\"},\\n'
            '  {\\"timecode\\": \\"02:01\\", \\"chapterSummary\\": '
            '\\"Discussing the first main point...\\"}\\n'
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
            "Keywords": (
                "testing,mock,video,automation,example,demo,sample,"
                "test,keywords,tags"
            ),
        }
    else:
        # Use a specific model if desired
        title_model = GenerativeModel("gemini-2.0-flash-001")
        prompt = (
            "Please write a 40-character long intriguing title for this video "
            "and 10 comma-separated hashtags suitable for YouTube Shorts "
            "based on the audio. Format the response strictly as a valid JSON object "
            "with two keys: 'Description' (containing the title, max 50 characters) "
            "and 'Keywords' (containing the comma-separated hashtags "
            "as a single string)."
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


def should_process_file(file_name):
    """
    Determine if a file should be processed based on file type and path.

    Args:
        file_name: Name of the file

    Returns:
        bool: True if file should be processed
    """
    # Check if the file is in the daily-raw or main-raw folders
    if not (file_name.startswith("daily-raw/") or file_name.startswith("main-raw/")):
        logging.info(
            f"File {file_name} is not in daily-raw/ or main-raw/ folder. Skipping."
        )
        return False

    # Check if the file is an MP4
    if not file_name.lower().endswith(".mp4"):
        logging.info(f"File {file_name} is not an MP4 file. Skipping.")
        return False

    return True


def setup_output_paths(bucket_name, file_name):
    """
    Set up all the necessary paths for processing.

    Args:
        bucket_name: The bucket name
        file_name: The file name

    Returns:
        tuple: Contains all the necessary paths for processing
    """
    # Determine if it's a daily or main channel video
    channel_type = "daily" if file_name.startswith("daily-raw/") else "main"

    # Extract the base filename without the path or extension
    base_filename = os.path.splitext(os.path.basename(file_name))[0]

    # Set up paths for the output files
    base_folder = "processed-daily" if channel_type == "daily" else "processed-main"
    output_folder = f"{base_folder}/{base_filename}"

    # Local paths for testing
    local_dir = f"local_output/{output_folder}"
    video_path = f"{local_dir}/{base_filename}.mp4"
    audio_path = f"{local_dir}/{base_filename}.wav"
    transcript_path = f"{local_dir}/{base_filename}.txt"
    vtt_path = f"{local_dir}/{base_filename}.vtt"
    shownotes_path = f"{local_dir}/{base_filename}.md"
    chapters_path = f"{local_dir}/{base_filename}.chapters.json"
    titles_path = f"{local_dir}/{base_filename}.titles.json"

    return (
        channel_type,
        base_filename,
        output_folder,
        local_dir,
        video_path,
        audio_path,
        transcript_path,
        vtt_path,
        shownotes_path,
        chapters_path,
        titles_path,
    )


def download_and_setup_local(bucket_name, file_name, video_path, local_dir):
    """
    Download the file from GCS and set up local directory.

    Args:
        bucket_name: The bucket name
        file_name: The file name
        video_path: Path to save the video
        local_dir: Local directory to create

    Returns:
        bool: True if successful
    """
    # Create local output directory if it doesn't exist
    os.makedirs(local_dir, exist_ok=True)

    # Download the video file from GCS
    if not TESTING_MODE or REAL_API_TEST:
        logging.info(f"Downloading gs://{bucket_name}/{file_name} to {video_path}")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        try:
            blob.download_to_filename(video_path)
            logging.info(f"Downloaded gs://{bucket_name}/{file_name} to {video_path}")
        except Exception as e:
            logging.error(f"Error downloading file: {e}")
            return False
    else:
        # In testing mode, create a dummy video file
        logging.info(f"TESTING MODE: Creating dummy file at {video_path}")
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        with open(video_path, "wb") as f:
            f.write(b"Dummy test video file for testing.")

    return True


def move_processed_file(
    file_name, bucket_name, destination_blob_name, source_path=None, dest_path=None
):
    """Move a processed file to the appropriate destination."""
    try:
        if LOCAL_OUTPUT and source_path and dest_path:
            # In local output mode, move the file locally
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                if not TESTING_MODE:
                    os.remove(source_path)
                logging.info(
                    f"Successfully moved local file from {source_path} to {dest_path}"
                )
            else:
                logging.warning(
                    f"Source file {source_path} does not exist. Skipping move."
                )
        else:
            if not TESTING_MODE or REAL_API_TEST:
                # In production mode, move the file in GCS
                # blob refers to the original blob object fetched earlier for download
                storage_client = storage.Client()
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(file_name)
                bucket.copy_blob(blob, bucket, destination_blob_name)
                blob.delete()  # Delete the original blob after successful copy
                logging.info(
                    f"Successfully moved gs://{bucket_name}/{file_name} to gs://{bucket_name}/{destination_blob_name}"
                )
    except Exception as move_error:
        # Log error but don't fail the entire process if move fails
        logging.error(
            f"Failed to move original file {file_name} to "
            f"{destination_blob_name}: {move_error}"
        )


def handle_processing_results(
    bucket_name,
    output_folder,
    base_filename,
    local_dir,
    video_path,
    audio_path,
    transcript_path,
    vtt_path,
    shownotes_path,
    chapters_path,
    titles_path,
):
    """Handle all processing results and output files."""
    try:
        # Define additional GCS paths
        bucket = None
        if not TESTING_MODE or REAL_API_TEST:
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)

        # Upload all files to GCS if not in local-only mode
        if not LOCAL_OUTPUT:
            try:
                # Upload video to the processed folder in GCS
                if os.path.exists(video_path) and (not TESTING_MODE or REAL_API_TEST):
                    video_blob = bucket.blob(f"{output_folder}/{base_filename}.mp4")
                    video_blob.upload_from_filename(video_path)

                # Upload metadata files to GCS
                for local_path, filename in [
                    (audio_path, f"{base_filename}.wav"),
                    (transcript_path, f"{base_filename}.txt"),
                    (vtt_path, f"{base_filename}.vtt"),
                    (shownotes_path, f"{base_filename}.md"),
                    (chapters_path, f"{base_filename}.chapters.json"),
                    (titles_path, f"{base_filename}.titles.json"),
                ]:
                    if os.path.exists(local_path) and (
                        not TESTING_MODE or REAL_API_TEST
                    ):
                        metadata_blob = bucket.blob(f"{output_folder}/{filename}")
                        metadata_blob.upload_from_filename(local_path)
                        logging.info(
                            f"Uploaded {local_path} to gs://{bucket_name}/{output_folder}/{filename}"
                        )

                # The YouTube uploader will be triggered automatically by the GCS event
                # when the files are uploaded to the processed-daily/ or
                # processed-main/ folders
                logging.info("YouTube uploader will be triggered by GCS event.")
            except Exception as upload_error:
                logging.error(f"Error uploading processed files: {upload_error}")
                return False

        return True
    except Exception as e:
        logging.error(f"Error handling processing results: {e}")
        return False


def extract_audio(video_path, output_path=None, sample_rate=16000, channels=1):
    """
    Extract audio from a video file using ffmpeg.

    Args:
        video_path: Path to the video file
        output_path: Path to save the audio file (if None, uses video path with .wav)
        sample_rate: Audio sample rate in Hz
        channels: Number of audio channels (1=mono, 2=stereo)

    Returns:
        Path to the output audio file
    """
    if output_path is None:
        # Generate output path based on video path
        output_path = os.path.splitext(video_path)[0] + ".wav"

    logging.info(f"Extracting audio from {video_path} to {output_path}")

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
                str(sample_rate),  # Audio sample rate
                "-ac",
                str(channels),  # Number of audio channels
                output_path,
            ],
            check=True,  # Raise exception on non-zero exit code
            capture_output=True,  # Capture stderr/stdout
            text=True,  # Decode stderr/stdout as text
        )
        logging.info("Audio extraction complete")
        return output_path
    except subprocess.CalledProcessError as e:
        logging.error(f"ffmpeg failed: {e}\nStderr: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error during audio extraction: {e}")
        raise


def process_audio_and_generate_content(
    video_path,
    audio_path,
    transcript_path,
    vtt_path,
    shownotes_path,
    chapters_path,
    titles_path,
):
    """
    Process audio and generate content using AI.

    Args:
        video_path: Path to the video file
        audio_path: Path to the audio file
        transcript_path: Path to save the transcript
        vtt_path: Path to save the VTT subtitles
        shownotes_path: Path to save the shownotes
        chapters_path: Path to save the chapters data
        titles_path: Path to save the titles data

    Returns:
        bool: True if successful
    """
    try:
        # Extract audio from video
        extract_audio(video_path, audio_path)
        logging.info(f"Extracted audio from {video_path} to {audio_path}")

        # Load the audio file for AI processing
        audio_part = None
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            try:
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
                    audio_part = Part.from_data(audio_data, mime_type="audio/wav")
            except Exception as e:
                logging.error(f"Error loading audio file: {e}")
                # Create dummy audio data for testing
                if TESTING_MODE:
                    audio_part = Part.from_data(
                        b"Dummy audio data for testing", mime_type="audio/wav"
                    )

        # Generate transcript
        transcript = generate_transcript(audio_part)
        if transcript:
            with open(transcript_path, "w") as f:
                f.write(transcript)
            logging.info(f"Saved transcript to {transcript_path}")

        # Generate VTT subtitles
        vtt = generate_vtt(audio_part)
        if vtt:
            with open(vtt_path, "w") as f:
                f.write(vtt)
            logging.info(f"Saved VTT subtitles to {vtt_path}")

        # Generate shownotes
        shownotes = generate_shownotes(audio_part)
        if shownotes:
            with open(shownotes_path, "w") as f:
                f.write(shownotes)
            logging.info(f"Saved shownotes to {shownotes_path}")

        # Generate chapters
        chapters = generate_chapters(audio_part)
        if chapters:
            with open(chapters_path, "w") as f:
                json.dump(chapters, f, indent=2)
            logging.info(f"Saved chapters to {chapters_path}")

        # Generate title and keywords
        titles_data = generate_titles(audio_part)
        if titles_data:
            with open(titles_path, "w") as f:
                json.dump(titles_data, f, indent=2)
            logging.info(f"Saved titles to {titles_path}")

        return True
    except Exception as e:
        logging.error(f"Error processing audio and generating content: {e}")
        logging.exception("Stack trace:")
        return False


# Rename function and change signature to accept bucket and file name directly
def process_video_event(bucket_name, file_name):
    logging.info(f"Processing video event for gs://{bucket_name}/{file_name}")

    # Skip files that don't need processing
    if not should_process_file(file_name):
        return

    # Set up all the paths
    (
        channel_type,
        base_filename,
        output_folder,
        local_dir,
        video_path,
        audio_path,
        transcript_path,
        vtt_path,
        shownotes_path,
        chapters_path,
        titles_path,
    ) = setup_output_paths(bucket_name, file_name)

    # Download the file from GCS and set up local directory
    if not download_and_setup_local(bucket_name, file_name, video_path, local_dir):
        logging.error("Failed to download and set up files. Aborting.")
        return

    # --- Process the video file and generate content ---
    if not process_audio_and_generate_content(
        video_path,
        audio_path,
        transcript_path,
        vtt_path,
        shownotes_path,
        chapters_path,
        titles_path,
    ):
        logging.error("Failed to process video and generate content. Aborting.")
        return

    # --- Move the original video file to a processed folder ---
    original_video_destination = f"raw-processed/{file_name}"
    move_processed_file(file_name, bucket_name, original_video_destination)

    # --- Handle the processing results ---
    if not handle_processing_results(
        bucket_name,
        output_folder,
        base_filename,
        local_dir,
        video_path,
        audio_path,
        transcript_path,
        vtt_path,
        shownotes_path,
        chapters_path,
        titles_path,
    ):
        logging.error("Failed to handle processing results.")
        return False

    logging.info(f"Completed processing for {file_name}")
    return True
