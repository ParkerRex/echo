# Product Context

**Why this project exists:**  
To reduce manual work in video publishing and ensure high-quality, consistent metadata for YouTube uploads.

**Problems it solves:**  
- Manual metadata creation is time-consuming and error-prone
- Inconsistent uploads and metadata quality
- Lack of automation in video publishing pipelines

**How it should work:**  
- User uploads a `.mp4` file to a designated **Google Cloud Storage (GCS) bucket** (canonical storage for all video files)
- The system automatically processes the video, generates AI-powered metadata (transcripts, titles, chapters, descriptions), and uploads the video to YouTube with all metadata attached
- **Firestore is used for real-time status and metadata for each video.**
- **Firebase Storage is NOT used for video files in production.** (Current frontend implementation uses Firebase Storage for local/dev convenience, but all production uploads must go to GCS.)
- Minimal manual intervention required; reliable, repeatable, and scalable workflow

**User experience goals:**  
- Simple, automated workflow from video upload to YouTube publishing
- Minimal manual steps for the user
- Consistent, high-quality metadata and video uploads
- Scalable to handle both daily and main channel content

**Source:**  
- [README.md](../README.md) (Overview, Usage & Expected Outcomes)  
- [ROADMAP.md](../ROADMAP.md) (Vision)
