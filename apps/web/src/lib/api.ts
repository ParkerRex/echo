// API fetchers for the web app

export type VideoSummary = {
  id: string;
  title: string;
  status?: string;
  created_at?: string;
  thumbnail_url?: string | null;
};

// Fetches the current user's videos from the backend API.
export async function fetchMyVideos(): Promise<VideoSummary[]> {
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const endpoint = `${API_BASE_URL}/videos/my`;

  // The browser will send cookies (including access token) automatically if using httpOnly cookies.
  // If you need to send a token manually, add it here.

  const res = await fetch(endpoint, {
    method: "GET",
    credentials: "include", // send cookies if needed
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch videos: ${res.status} ${errorText}`);
  }

  return res.json();
}
