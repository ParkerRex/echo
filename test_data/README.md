# Test Data Directory

Place test video files in this directory for local testing.

## Example Usage

1. Add a test video file to this directory (e.g., `test-video.mp4`)
2. Run the local test script:
   ```
   ./scripts/local_test.sh
   ```
3. Trigger a test event:
   ```
   curl -X POST http://localhost:8081/trigger \
     -H "Content-Type: application/json" \
     -d '{"bucket":"automations-videos","name":"test-video.mp4"}'
   ```

## Supported File Types

The Video Processor supports the following file types:
- MP4 (.mp4)
- MOV (.mov)
- AVI (.avi)
- Other formats supported by ffmpeg
