// API fetchers for the web app

import type {
  VideoSummary,
  SignedUploadUrlRequest,
  SignedUploadUrlResponse,
  UploadCompleteRequest,
  VideoDetailsResponse,
  VideoMetadataUpdateRequest,
  ApiErrorResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";

async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorPayload: ApiErrorResponse | string;
    try {
      errorPayload = await response.json();
    } catch (e) {
      errorPayload = await response.text();
    }
    const errorMessage = typeof errorPayload === 'string' ? errorPayload : (errorPayload as ApiErrorResponse).detail || `HTTP error ${response.status}`;
    throw new Error(`API Error: ${response.status} - ${errorMessage}`);
  }
  if (response.status === 204) { // No Content
    return undefined as T; // Or handle as appropriate for your use case
  }
  return response.json() as Promise<T>;
}

// Fetches the current user's videos from the backend API.
export async function fetchMyVideos(): Promise<VideoSummary[]> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/users/me/videos`;

  const res = await fetch(endpoint, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  return handleApiResponse<VideoSummary[]>(res);
}

// Requests a pre-signed URL to upload a video directly to cloud storage.
export async function getSignedUploadUrl(
  data: SignedUploadUrlRequest
): Promise<SignedUploadUrlResponse> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/signed-upload-url`;
  const res = await fetch(endpoint, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleApiResponse<SignedUploadUrlResponse>(res);
}

// Notifies the backend that a direct video upload is complete.
export async function notifyUploadComplete(
  data: UploadCompleteRequest
): Promise<void> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/upload-complete`;
  const res = await fetch(endpoint, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleApiResponse<void>(res);
}

// Fetches comprehensive details for a specific video.
export async function getVideoDetails(
  videoId: string
): Promise<VideoDetailsResponse> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/${videoId}/details`;
  const res = await fetch(endpoint, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleApiResponse<VideoDetailsResponse>(res);
}

// Updates metadata for a specific video.
export async function updateVideoMetadata(
  videoId: string,
  metadata: VideoMetadataUpdateRequest
): Promise<void> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/${videoId}/metadata`;
  const res = await fetch(endpoint, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(metadata),
  });
  return handleApiResponse<void>(res);
}

// Fetches the status and results of a specific processing job.
// Note: WebSocket is preferred for real-time updates, but this can be a fallback.
// Assuming VideoJob type would be defined in types/api.ts similar to VideoDetailsResponse
// For now, let's assume it returns a similar structure to VideoJob from types/api.ts
import type { VideoJob } from '../types/api';
export async function getJobDetails(jobId: string): Promise<VideoJob> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/jobs/${jobId}`;
  const res = await fetch(endpoint, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleApiResponse<VideoJob>(res);
}
