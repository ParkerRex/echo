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
import { supabase } from '@echo/db/clients/client'; // Import Supabase client

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";

// Helper to get Supabase token
async function getAuthHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  return headers;
}

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

// Define PaginationParams interface
export interface PaginationParams {
  limit?: number;
  offset?: number;
  // page?: number; // Alternative, if backend uses page numbers
}

// Fetches the current user's videos from the backend API.
export async function fetchMyVideos(params?: PaginationParams): Promise<VideoSummary[]> {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', String(params.limit));
  if (params?.offset) queryParams.append('offset', String(params.offset));
  // if (params?.page) queryParams.append('page', String(params.page));

  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/users/me/videos${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const headers = await getAuthHeaders();

  const res = await fetch(endpoint, {
    method: "GET",
    headers: headers,
  });

  return handleApiResponse<VideoSummary[]>(res);
}

// Requests a pre-signed URL to upload a video directly to cloud storage.
export async function getSignedUploadUrl(
  data: SignedUploadUrlRequest
): Promise<SignedUploadUrlResponse> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/signed-upload-url`;
  const headers = await getAuthHeaders(); // Assuming this might need auth too
  const res = await fetch(endpoint, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data),
  });
  return handleApiResponse<SignedUploadUrlResponse>(res);
}

// Notifies the backend that a direct video upload is complete.
export async function notifyUploadComplete(
  data: UploadCompleteRequest
): Promise<void> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/upload-complete`;
  const headers = await getAuthHeaders();
  const res = await fetch(endpoint, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data),
  });
  return handleApiResponse<void>(res);
}

// Fetches comprehensive details for a specific video.
export async function getVideoDetails(
  videoId: string
): Promise<VideoDetailsResponse> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/${videoId}/details`;
  const headers = await getAuthHeaders();
  const res = await fetch(endpoint, {
    method: "GET",
    headers: headers,
  });
  return handleApiResponse<VideoDetailsResponse>(res);
}

// Updates metadata for a specific video.
export async function updateVideoMetadata(
  videoId: string,
  metadata: VideoMetadataUpdateRequest
): Promise<void> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/${videoId}/metadata`;
  const headers = await getAuthHeaders();
  const res = await fetch(endpoint, {
    method: "PUT",
    headers: headers,
    body: JSON.stringify(metadata),
  });
  return handleApiResponse<void>(res);
}

// Fetches the status and results of a specific processing job.
// Note: WebSocket is preferred for real-time updates, but this can be a fallback.
// Assuming VideoJob type would be defined in types/api.ts similar to VideoDetailsResponse
// For now, let's assume it returns a similar structure to VideoJob from types/api.ts
import type { VideoJobSchema as VideoJob } from '../types/api';
export async function getJobDetails(jobId: string): Promise<VideoJob> {
  const endpoint = `${API_BASE_URL}${API_V1_PREFIX}/videos/jobs/${jobId}`;
  const headers = await getAuthHeaders();
  const res = await fetch(endpoint, {
    method: "GET",
    headers: headers,
  });
  return handleApiResponse<VideoJob>(res);
}
