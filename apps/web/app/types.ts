import type { Tables } from "@echo/db/types"

// Video processing types from the shared database schema
export type Video = Tables<"videos">
export type VideoJob = Tables<"video_jobs">
export type VideoMetadata = Tables<"video_metadata">
