// apps/web/src/types/api.ts

// Represents the summary of a video, typically for listings.
export type VideoSummary = {
  id: string;
  original_filename: string; // From VideoModel
  status?: string; // Potentially from VideoJobModel if joined
  created_at?: string; // From VideoModel
  thumbnail_url?: string | null; // From VideoMetadataModel
  title?: string | null; // From VideoMetadataModel
};

// Request payload for getting a signed upload URL.
export type SignedUploadUrlRequest = {
  filename: string;
  contentType: string;
};

// Response from the signed upload URL endpoint.
export type SignedUploadUrlResponse = {
  uploadUrl: string;
  videoId: string; // videoId or a temporary correlation ID
};

// Request payload for notifying backend of upload completion.
export type UploadCompleteRequest = {
  videoId: string; // videoId or correlation ID from SignedUploadUrlResponse
  originalFilename: string;
  storagePath?: string; // Path where the file was uploaded in cloud storage - Made optional
  contentType: string;
  sizeBytes: number;
};

// Represents the processing status of a video job.
// Mirrors apps/core/models/enums.py ProcessingStatus
export enum ProcessingStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
}

// Detailed information about a video processing job.
// Mirrors VideoJobSchema from apps/core/api/schemas/video_processing_schemas.py
export type VideoJob = {
  id: number;
  video_id: number;
  status: ProcessingStatus;
  processing_stages?: any; // JSON or Text
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  // Relationships if included by backend:
  // video?: Video;
  // metadata?: VideoMetadata;
};

// Detailed information about video metadata.
// Mirrors VideoMetadataSchema from apps/core/api/schemas/video_processing_schemas.py
export type VideoMetadata = {
  id: number;
  job_id: number;
  title?: string | null;
  description?: string | null;
  tags?: string[] | null; // Assuming JSON array of strings
  transcript_text?: string | null;
  transcript_file_url?: string | null;
  subtitle_files_urls?: { [key: string]: string } | null; // e.g., {"vtt": "url", "srt": "url"}
  thumbnail_file_url?: string | null;
  extracted_video_duration_seconds?: number | null;
  extracted_video_resolution?: string | null;
  extracted_video_format?: string | null;
  show_notes_text?: string | null;
  created_at: string;
  updated_at: string;
};

// Comprehensive details for a specific video.
// This combines VideoModel info with its related Job and Metadata.
export type VideoDetailsResponse = {
  id: string; // VideoModel id
  uploader_user_id: string;
  original_filename: string;
  storage_path: string;
  content_type: string;
  size_bytes: number;
  created_at: string; // VideoModel created_at
  updated_at: string; // VideoModel updated_at
  playbackUrl?: string | null; // Added for playback
  job?: VideoJob | null; // Related VideoJobModel
  metadata?: VideoMetadata | null; // Related VideoMetadataModel
};

// Request payload for updating video metadata.
export type VideoMetadataUpdateRequest = {
  title?: string;
  description?: string;
  tags?: string[];
  // Add other fields that are updatable by the user
};

// Standard error response from the API
export type ApiErrorResponse = {
  detail: string | any; // FastAPI often uses 'detail' for errors
}; 