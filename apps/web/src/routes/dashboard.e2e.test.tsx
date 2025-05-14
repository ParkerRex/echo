// E2E smoke test for login → upload → dashboard video listing
// This test assumes the backend and Supabase are running locally and accessible.

import { describe, it, expect, beforeAll } from "vitest";
import { fetchMyVideos } from "@/lib/api";

// NOTE: This is a placeholder for a true E2E test. In a real E2E setup, use Playwright or Cypress for browser automation.
// Here, we test the API integration and dashboard listing logic.

describe("E2E: Dashboard video listing", () => {
  let initialVideos: Awaited<ReturnType<typeof fetchMyVideos>>;

  beforeAll(async () => {
    // Simulate user login here if possible (e.g., set cookie/JWT)
    // For now, assume the test runner is authenticated or running with a test user session.
    initialVideos = await fetchMyVideos();
  });

  it("should list videos for the current user", async () => {
    const videos = await fetchMyVideos();
    expect(Array.isArray(videos)).toBe(true);
    // If there are no videos, the test still passes (empty state)
    // If there are videos, check structure
    if (videos.length > 0) {
      const video = videos[0];
      expect(video).toHaveProperty("id");
      expect(video).toHaveProperty("title");
      expect(video).toHaveProperty("status");
      expect(video).toHaveProperty("created_at");
    }
  });

  // Additional steps for upload and dashboard refresh would require browser automation.
  // This test can be expanded with Playwright/Cypress for full E2E coverage.
});
