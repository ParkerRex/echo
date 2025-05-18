import os

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile

import apps.core.models
from apps.core.api.endpoints import router as video_api_router
from apps.core.api.endpoints.jobs_endpoints import router as jobs_api_router

app = FastAPI()

# Register routers
app.include_router(video_api_router, prefix="/api/v1/videos", tags=["Video Processing"])
app.include_router(jobs_api_router, prefix="/api/v1/jobs", tags=["Jobs"])


# Add a simple startup message
@app.get("/")
async def root():
    return {"message": "Video Processing API is running"}


# Simple test endpoint for video upload without authentication
@app.post("/test/upload")
async def test_upload(file: UploadFile = File(...)):
    """Test endpoint for uploading videos without authentication"""
    print(f"Received file: {file.filename}, content_type: {file.content_type}")

    # For testing, we'll accept any file type
    # if not file.content_type or not file.content_type.startswith("video/"):
    #     return {"error": "File must be a video"}

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    # Save the file to a temporary location using an absolute path
    content = await file.read()

    # Get the absolute path to the core directory - we're in apps/core/main.py
    core_dir = os.path.dirname(os.path.abspath(__file__))
    test_upload_dir = os.path.join(core_dir, "output_files", "uploads", "test")

    # Create directory if it doesn't exist
    os.makedirs(test_upload_dir, exist_ok=True)

    # Build full file path
    save_path = os.path.join(test_upload_dir, file.filename)

    # Save the file
    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "message": "Video uploaded successfully for testing",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "saved_path": save_path,
    }


# Run the application if this script is executed directly
if __name__ == "__main__":
    import uvicorn

    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
