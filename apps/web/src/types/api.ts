/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

/**
 * Current status of the processing job.
 */
export type ProcessingStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
/**
 * Enumeration of possible video processing job statuses.
 *
 * This enum inherits from str to allow for easy serialization to/from databases
 * and JSON, while still providing type safety and enumeration benefits.
 *
 * Attributes:
 *     PENDING: Job has been created but processing has not started.
 *     PROCESSING: Job is currently being processed.
 *     COMPLETED: Job has completed successfully.
 *     FAILED: Job processing failed with an error.
 */
export type ProcessingStatus1 = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
/**
 * Enumeration of possible video processing job statuses.
 *
 * This enum inherits from str to allow for easy serialization to/from databases
 * and JSON, while still providing type safety and enumeration benefits.
 *
 * Attributes:
 *     PENDING: Job has been created but processing has not started.
 *     PROCESSING: Job is currently being processed.
 *     COMPLETED: Job has completed successfully.
 *     FAILED: Job processing failed with an error.
 */
export type ProcessingStatus2 = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

/**
 * Individual error detail, often part of a list in ApiErrorResponse.
 */
export interface ApiErrorDetail {
  /**
   * Location of the error (e.g., field path)
   */
  loc?: (string | number)[] | null;
  /**
   * Error message
   */
  msg: string;
  /**
   * Type of error (e.g., 'value_error')
   */
  type: string;
  /**
   * Additional context for the error
   */
  ctx?: {
    [k: string]: unknown;
  } | null;
}
/**
 * Standard error response structure for API errors.
 */
export interface ApiErrorResponse {
  /**
   * Error message or list of error details
   */
  detail: string | ApiErrorDetail[];
}
/**
 * Request schema for obtaining a signed URL for video upload.
 */
export interface SignedUploadUrlRequest {
  /**
   * Original filename of the video.
   */
  filename: string;
  /**
   * MIME type of the video file.
   */
  content_type: string;
}
/**
 * Response schema after requesting a signed URL.
 */
export interface SignedUploadUrlResponse {
  /**
   * The GCS signed URL for direct PUT upload.
   */
  upload_url: string;
  /**
   * The unique ID assigned to this video upload attempt/record.
   */
  video_id: string;
}
/**
 * Request schema to notify the backend that a direct upload is complete.
 */
export interface UploadCompleteRequest {
  /**
   * The unique ID of the video upload.
   */
  video_id: string;
  /**
   * Original filename of the uploaded video.
   */
  original_filename: string;
  /**
   * MIME type of the video file.
   */
  content_type: string;
  /**
   * Size of the video file in bytes.
   */
  size_bytes: number;
  /**
   * Canonical path in GCS if known by uploader; backend may infer.
   */
  storage_path?: string | null;
}
/**
 * Comprehensive details for a specific video, including its job and metadata.
 * This often mirrors VideoJobSchema if that schema is the primary source of truth.
 * Alternatively, it can be a composition of VideoSchema, VideoMetadataSchema, and job details.
 * Let's make it closely related to VideoJobSchema for now.
 */
export interface VideoDetailsResponse {
  /**
   * Video Job ID. If this is for Video Details, this might be Video ID with Job details nested or vice-versa
   */
  id: number;
  /**
   * Associated Video ID
   */
  video_id: number;
  /**
   * ID of the user who uploaded the video. (Derived from video)
   */
  uploader_user_id?: string | null;
  /**
   * Original filename from the upload. (Derived from video)
   */
  original_filename?: string | null;
  status: ProcessingStatus;
  /**
   * Progress information.
   */
  processing_stages?:
    | string[]
    | {
        [k: string]: unknown;
      }
    | null;
  /**
   * Error details if the job failed.
   */
  error_message?: string | null;
  /**
   * When the job (or video) was created.
   */
  created_at?: string | null;
  /**
   * When the job (or video) was last updated.
   */
  updated_at?: string | null;
  /**
   * Associated video details.
   */
  video?: VideoSchema | null;
  /**
   * Associated metadata details.
   */
  metadata?: VideoMetadataSchema | null;
}
/**
 * Schema representing a video file in the system. (Existing)
 */
export interface VideoSchema {
  id: number;
  uploader_user_id: string;
  original_filename: string;
  storage_path: string;
  content_type: string;
  size_bytes: number;
  created_at?: string | null;
  updated_at?: string | null;
}
/**
 * Schema representing metadata extracted from a processed video. (Existing)
 */
export interface VideoMetadataSchema {
  id?: number | null;
  job_id?: number | null;
  title?: string | null;
  description?: string | null;
  tags?: string[] | null;
  transcript_text?: string | null;
  transcript_file_url?: string | null;
  subtitle_files_urls?: {
    [k: string]: unknown;
  } | null;
  thumbnail_file_url?: string | null;
  extracted_video_duration_seconds?: number | null;
  extracted_video_resolution?: string | null;
  extracted_video_format?: string | null;
  show_notes_text?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}
/**
 * Schema representing a video processing job. (Existing)
 */
export interface VideoJobSchema {
  id: number;
  video_id: number;
  status: ProcessingStatus1;
  processing_stages?:
    | string[]
    | {
        [k: string]: unknown;
      }
    | null;
  error_message?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  video?: VideoSchema | null;
  metadata?: VideoMetadataSchema | null;
}
/**
 * Request schema for updating video metadata.
 */
export interface VideoMetadataUpdateRequest {
  /**
   * New title for the video.
   */
  title?: string | null;
  /**
   * New description for the video.
   */
  description?: string | null;
  /**
   * New list of tags for the video.
   */
  tags?: string[] | null;
}
/**
 * Summarized video information, typically for lists.
 */
export interface VideoSummary {
  /**
   * Unique identifier for the video.
   */
  id: number;
  /**
   * Original filename of the video.
   */
  original_filename: string;
  /**
   * Title of the video.
   */
  title?: string | null;
  /**
   * Timestamp of video creation.
   */
  created_at?: string | null;
  /**
   * Current processing status of the video.
   */
  status?: ProcessingStatus1 | null;
  /**
   * URL to the video's thumbnail.
   */
  thumbnail_file_url?: string | null;
}
/**
 * Response schema for the video upload endpoint. (Existing)
 * NOTE: This might be for when upload starts processing, not the signed URL itself.
 * If getSignedUploadUrl returns SignedUploadUrlResponse, this might be for a different step.
 * For now, keeping as is, assuming it's used by an endpoint.
 */
export interface VideoUploadResponseSchema {
  /**
   * The ID of the created video processing job.
   */
  job_id: number;
  status: ProcessingStatus2;
}
