-- Migration: Setup video processing tables (videos, video_jobs, video_metadata)
-- Original Timestamp: 20250514044259 (retained for filename consistency if modifying)
-- Purpose: Defines the core data structure for the video processing pipeline,
-- including tables for video uploads, processing jobs, and generated metadata,
-- along with appropriate RLS policies for user data isolation and an enum for job status.
BEGIN;
-- 0. Create ENUM type for processing_status if it doesn't exist
-- This ensures the type is available before being used in table definitions.
DO $$ BEGIN IF NOT EXISTS (
  SELECT 1
  FROM pg_type
  WHERE typname = 'processing_status_enum'
) THEN CREATE TYPE public.processing_status_enum AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');
END IF;
END $$;
-- 1. Create the 'videos' table
-- Stores core information about uploaded video files.
CREATE TABLE IF NOT EXISTS public.videos (
  id SERIAL PRIMARY KEY,
  uploader_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  original_filename TEXT NOT NULL,
  storage_path TEXT NOT NULL UNIQUE,
  content_type TEXT NOT NULL,
  size_bytes BIGINT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);
COMMENT ON TABLE public.videos IS 'Stores information about originally uploaded video files.';
COMMENT ON COLUMN public.videos.id IS 'Unique identifier for the video entry.';
COMMENT ON COLUMN public.videos.uploader_user_id IS 'Foreign key to auth.users, identifying the uploader.';
COMMENT ON COLUMN public.videos.original_filename IS 'The original name of the uploaded video file.';
COMMENT ON COLUMN public.videos.storage_path IS 'Unique path where the original video is stored (e.g., GCS path).';
COMMENT ON COLUMN public.videos.content_type IS 'MIME type of the video (e.g., video/mp4).';
COMMENT ON COLUMN public.videos.size_bytes IS 'Size of the original video file in bytes.';
COMMENT ON COLUMN public.videos.created_at IS 'Timestamp of when the video record was created.';
COMMENT ON COLUMN public.videos.updated_at IS 'Timestamp of when the video record was last updated.';
-- Generic Trigger function for updated_at columns
-- This function can be reused for multiple tables.
CREATE OR REPLACE FUNCTION public.update_updated_at_column() RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
SET search_path = '' AS $$ BEGIN NEW.updated_at = timezone('utc'::text, now());
RETURN NEW;
END;
$$;
-- Trigger for 'videos' table to automatically update 'updated_at'
DROP TRIGGER IF EXISTS trig_update_videos_updated_at ON public.videos;
CREATE TRIGGER trig_update_videos_updated_at BEFORE
UPDATE ON public.videos FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
-- RLS for 'videos' table
ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;
-- Policy: Users can select their own videos.
DROP POLICY IF EXISTS "Users can select their own videos" ON public.videos;
CREATE POLICY "Users can select their own videos" ON public.videos FOR
SELECT TO authenticated USING (
    (
      SELECT auth.uid()
    ) = uploader_user_id
  );
-- Policy: Users can insert videos for themselves.
DROP POLICY IF EXISTS "Users can insert their own videos" ON public.videos;
CREATE POLICY "Users can insert their own videos" ON public.videos FOR
INSERT TO authenticated WITH CHECK (
    (
      SELECT auth.uid()
    ) = uploader_user_id
  );
-- Policy: Users can update their own videos.
DROP POLICY IF EXISTS "Users can update their own videos" ON public.videos;
CREATE POLICY "Users can update their own videos" ON public.videos FOR
UPDATE TO authenticated USING (
    (
      SELECT auth.uid()
    ) = uploader_user_id
  ) WITH CHECK (
    (
      SELECT auth.uid()
    ) = uploader_user_id
  );
-- Policy: Users can delete their own videos.
DROP POLICY IF EXISTS "Users can delete their own videos" ON public.videos;
CREATE POLICY "Users can delete their own videos" ON public.videos FOR DELETE TO authenticated USING (
  (
    SELECT auth.uid()
  ) = uploader_user_id
);
-- Index for faster RLS checks and queries on uploader_user_id
CREATE INDEX IF NOT EXISTS idx_videos_uploader_user_id ON public.videos(uploader_user_id);
-- 2. Create the 'video_jobs' table
-- Tracks the status and progress of video processing tasks.
CREATE TABLE IF NOT EXISTS public.video_jobs (
  id SERIAL PRIMARY KEY,
  video_id INTEGER REFERENCES public.videos(id) ON DELETE CASCADE NOT NULL,
  status public.processing_status_enum NOT NULL DEFAULT 'PENDING',
  processing_stages JSONB NULL,
  error_message TEXT NULL,
  created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);
COMMENT ON TABLE public.video_jobs IS 'Tracks each processing attempt or workflow for a video.';
COMMENT ON COLUMN public.video_jobs.id IS 'Unique identifier for the video processing job.';
COMMENT ON COLUMN public.video_jobs.video_id IS 'Foreign key referencing the associated video in public.videos.';
COMMENT ON COLUMN public.video_jobs.status IS 'Current status of the job using the processing_status_enum type.';
COMMENT ON COLUMN public.video_jobs.processing_stages IS 'JSONB field to store detailed progress of various processing stages.';
COMMENT ON COLUMN public.video_jobs.error_message IS 'Stores any error message if the job failed.';
COMMENT ON COLUMN public.video_jobs.created_at IS 'Timestamp of when the job record was created.';
COMMENT ON COLUMN public.video_jobs.updated_at IS 'Timestamp of when the job record was last updated.';
-- Trigger for 'video_jobs' table
DROP TRIGGER IF EXISTS trig_update_video_jobs_updated_at ON public.video_jobs;
CREATE TRIGGER trig_update_video_jobs_updated_at BEFORE
UPDATE ON public.video_jobs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
-- RLS for 'video_jobs' table
ALTER TABLE public.video_jobs ENABLE ROW LEVEL SECURITY;
-- Policy: Users can select jobs related to their own videos.
DROP POLICY IF EXISTS "Users can select jobs for their videos" ON public.video_jobs;
CREATE POLICY "Users can select jobs for their videos" ON public.video_jobs FOR
SELECT TO authenticated USING (
    EXISTS (
      SELECT 1
      FROM public.videos v
      WHERE v.id = video_jobs.video_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  );
-- Policy: Users can insert jobs for their own videos.
DROP POLICY IF EXISTS "Users can insert jobs for their videos" ON public.video_jobs;
CREATE POLICY "Users can insert jobs for their videos" ON public.video_jobs FOR
INSERT TO authenticated WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.videos v
      WHERE v.id = video_jobs.video_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  );
-- Policy: Users can update jobs related to their own videos.
DROP POLICY IF EXISTS "Users can update jobs for their videos" ON public.video_jobs;
CREATE POLICY "Users can update jobs for their videos" ON public.video_jobs FOR
UPDATE TO authenticated USING (
    EXISTS (
      SELECT 1
      FROM public.videos v
      WHERE v.id = video_jobs.video_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  ) WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.videos v
      WHERE v.id = video_jobs.video_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  );
-- Policy: Users can delete jobs related to their own videos.
DROP POLICY IF EXISTS "Users can delete jobs for their videos" ON public.video_jobs;
CREATE POLICY "Users can delete jobs for their videos" ON public.video_jobs FOR DELETE TO authenticated USING (
  EXISTS (
    SELECT 1
    FROM public.videos v
    WHERE v.id = video_jobs.video_id
      AND v.uploader_user_id = (
        SELECT auth.uid()
      )
  )
);
-- Indexes for foreign keys and frequently queried columns
CREATE INDEX IF NOT EXISTS idx_video_jobs_video_id ON public.video_jobs(video_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON public.video_jobs(status);
-- 3. Create the 'video_metadata' table
-- Stores metadata extracted or generated during video processing.
CREATE TABLE IF NOT EXISTS public.video_metadata (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES public.video_jobs(id) ON DELETE CASCADE NOT NULL UNIQUE,
  title TEXT NULL,
  description TEXT NULL,
  tags TEXT [] NULL,
  transcript_text TEXT NULL,
  transcript_file_url TEXT NULL,
  subtitle_files_urls JSONB NULL,
  thumbnail_file_url TEXT NULL,
  extracted_video_duration_seconds FLOAT NULL,
  extracted_video_resolution TEXT NULL,
  extracted_video_format TEXT NULL,
  show_notes_text TEXT NULL,
  created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);
COMMENT ON TABLE public.video_metadata IS 'Stores metadata extracted or generated from a successfully completed video job.';
COMMENT ON COLUMN public.video_metadata.id IS 'Unique identifier for the video metadata entry.';
COMMENT ON COLUMN public.video_metadata.job_id IS 'Foreign key referencing the video_jobs table (one-to-one relationship).';
COMMENT ON COLUMN public.video_metadata.title IS 'Generated or user-provided title of the video.';
COMMENT ON COLUMN public.video_metadata.description IS 'Generated or user-provided description of the video.';
COMMENT ON COLUMN public.video_metadata.tags IS 'Array of tags associated with the video.';
COMMENT ON COLUMN public.video_metadata.transcript_text IS 'Full text transcript of the video.';
COMMENT ON COLUMN public.video_metadata.transcript_file_url IS 'URL to the stored transcript file (e.g., in GCS).';
COMMENT ON COLUMN public.video_metadata.subtitle_files_urls IS 'JSONB object storing URLs to various subtitle formats (e.g., {"vtt": "url", "srt": "url"}).';
COMMENT ON COLUMN public.video_metadata.thumbnail_file_url IS 'URL to the stored thumbnail image.';
COMMENT ON COLUMN public.video_metadata.extracted_video_duration_seconds IS 'Duration of the video in seconds, extracted by FFmpeg.';
COMMENT ON COLUMN public.video_metadata.extracted_video_resolution IS 'Resolution of the video (e.g., "1920x1080").';
COMMENT ON COLUMN public.video_metadata.extracted_video_format IS 'Format of the video (e.g., "mp4").';
COMMENT ON COLUMN public.video_metadata.show_notes_text IS 'Generated or user-provided show notes or detailed summary.';
COMMENT ON COLUMN public.video_metadata.created_at IS 'Timestamp of when the metadata record was created.';
COMMENT ON COLUMN public.video_metadata.updated_at IS 'Timestamp of when the metadata record was last updated.';
-- Trigger for 'video_metadata' table
DROP TRIGGER IF EXISTS trig_update_video_metadata_updated_at ON public.video_metadata;
CREATE TRIGGER trig_update_video_metadata_updated_at BEFORE
UPDATE ON public.video_metadata FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
-- RLS for 'video_metadata' table
ALTER TABLE public.video_metadata ENABLE ROW LEVEL SECURITY;
-- Policy: Users can select metadata for jobs related to their own videos.
DROP POLICY IF EXISTS "Users can select metadata for their video jobs" ON public.video_metadata;
CREATE POLICY "Users can select metadata for their video jobs" ON public.video_metadata FOR
SELECT TO authenticated USING (
    EXISTS (
      SELECT 1
      FROM public.video_jobs vj
        JOIN public.videos v ON vj.video_id = v.id
      WHERE vj.id = video_metadata.job_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  );
-- Policy: Users can insert metadata for jobs related to their own videos.
DROP POLICY IF EXISTS "Users can insert metadata for their video jobs" ON public.video_metadata;
CREATE POLICY "Users can insert metadata for their video jobs" ON public.video_metadata FOR
INSERT TO authenticated WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.video_jobs vj
        JOIN public.videos v ON vj.video_id = v.id
      WHERE vj.id = video_metadata.job_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  );
-- Policy: Users can update metadata for jobs related to their own videos.
DROP POLICY IF EXISTS "Users can update metadata for their video jobs" ON public.video_metadata;
CREATE POLICY "Users can update metadata for their video jobs" ON public.video_metadata FOR
UPDATE TO authenticated USING (
    EXISTS (
      SELECT 1
      FROM public.video_jobs vj
        JOIN public.videos v ON vj.video_id = v.id
      WHERE vj.id = video_metadata.job_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  ) WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.video_jobs vj
        JOIN public.videos v ON vj.video_id = v.id
      WHERE vj.id = video_metadata.job_id
        AND v.uploader_user_id = (
          SELECT auth.uid()
        )
    )
  );
-- Policy: Users can delete metadata for jobs related to their own videos.
DROP POLICY IF EXISTS "Users can delete metadata for their video jobs" ON public.video_metadata;
CREATE POLICY "Users can delete metadata for their video jobs" ON public.video_metadata FOR DELETE TO authenticated USING (
  EXISTS (
    SELECT 1
    FROM public.video_jobs vj
      JOIN public.videos v ON vj.video_id = v.id
    WHERE vj.id = video_metadata.job_id
      AND v.uploader_user_id = (
        SELECT auth.uid()
      )
  )
);
-- Index for the foreign key job_id
CREATE INDEX IF NOT EXISTS idx_video_metadata_job_id ON public.video_metadata(job_id);
COMMIT;