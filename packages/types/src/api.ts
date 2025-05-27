// API types - just the stuff your Python API actually returns
import type { Video, VideoJob, VideoMetadata } from './database';
import type { ProcessingStatus } from './shared';

// Just use the database types but with better names for API responses
export interface VideoResponse extends Video {}

export interface VideoJobResponse extends Omit<VideoJob, 'status'> {
  status: ProcessingStatus;
}

export interface VideoMetadataResponse extends VideoMetadata {}

// Simple request/response types
export interface VideoUploadRequest {
  filename: string;
  content_type: string;
  size_bytes: number;
}

export interface VideoMetadataUpdateRequest {
  title?: string;
  description?: string;
  tags?: string[];
}

export interface VideoSummary {
  id: number;
  original_filename: string;
  title?: string | null;
  thumbnail_file_url?: string | null;
  created_at: string;
  status?: ProcessingStatus | null;
}

export interface VideoUploadResponse {
  video_id: number;
  job_id: number;
  status: ProcessingStatus;
  upload_url?: string;
}

export interface VideoWithJobsResponse extends VideoResponse {
  jobs: VideoJobResponse[];
}

export interface VideoJobWithDetailsResponse extends VideoJobResponse {
  video: VideoResponse;
  video_metadata?: VideoMetadataResponse | null;
}

export interface VideoDetailsResponse {
  id: number;
  video_id: number;
  uploader_user_id?: string | null;
  original_filename?: string | null;
  status: ProcessingStatus;
  processing_stages?: string[] | Record<string, any> | null;
  error_message?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  video?: VideoResponse | null;
  metadata?: VideoMetadataResponse | null;
}

export interface SignedUploadUrlResponse {
  upload_url: string;
  video_id: number;
  expires_at: string;
}

// Missing types that the frontend needs
export interface SignedUploadUrlRequest {
  filename: string;
  content_type: string;
  size_bytes: number;
}

export interface UploadCompleteRequest {
  video_id: number;
  upload_key: string;
  original_filename?: string;
}

export interface ApiErrorResponse {
  error: string;
  message: string;
  details?: any;
  detail?: string; // Legacy alias
}

export interface WebSocketJobUpdate {
  type: 'job_update';
  job_id: number;
  video_id?: number;
  status: ProcessingStatus;
  processing_stages?: Record<string, any>;
  error_message?: string | null;
  title?: string;
  metadata?: {
    title?: string;
    thumbnail_file_url?: string;
  };
}

// Legacy aliases - keep these so nothing breaks
export interface VideoSchema extends VideoResponse {}
export interface VideoJobSchema extends VideoJobResponse {
  video?: VideoResponse | null;
  metadata?: VideoMetadataResponse | null;
}
export interface VideoMetadataSchema extends VideoMetadataResponse {}

// More legacy aliases that are used in the frontend
export interface VideoResponseSchema extends VideoResponse {}
export interface VideoJobResponseSchema extends VideoJobResponse {}
export interface VideoMetadataResponseSchema extends VideoMetadataResponse {}
