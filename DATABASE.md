# Database Schema Reference

> **Note**: This document provides detailed database schema reference. For development workflows and type generation, see the main [README.md](./README.md).

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core Tables](#core-tables)
3. [Custom Types](#custom-types)
4. [Indexes](#indexes)
5. [Row Level Security](#row-level-security)
6. [Database Functions](#database-functions)

## Schema Overview

Echo uses PostgreSQL via Supabase with a database-first architecture. The database schema is the single source of truth for all types across the application.

### Key Features

- **User Isolation**: RLS policies ensure users can only access their own data
- **Audit Trail**: Automatic `created_at` and `updated_at` timestamps
- **Referential Integrity**: Foreign key constraints maintain data consistency
- **Type Safety**: Custom ENUM types for status fields
- **Type Generation**: Schema drives TypeScript and Python type generation

## Core Tables

#### `public.videos`

Stores information about uploaded video files.

```sql
CREATE TABLE public.videos (
    id SERIAL PRIMARY KEY,
    uploader_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    original_filename TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    content_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

**Columns:**

- `id`: Unique identifier for the video entry
- `uploader_user_id`: Foreign key to auth.users, identifying the uploader
- `original_filename`: The original name of the uploaded video file
- `storage_path`: Unique path where the original video is stored (e.g., GCS path)
- `content_type`: MIME type of the video (e.g., video/mp4)
- `size_bytes`: Size of the original video file in bytes
- `created_at`: Timestamp of when the video record was created
- `updated_at`: Timestamp of when the video record was last updated

#### `public.video_jobs`

Tracks the status and progress of video processing tasks.

```sql
CREATE TABLE public.video_jobs (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES public.videos(id) ON DELETE CASCADE NOT NULL,
    status public.processing_status_enum NOT NULL DEFAULT 'PENDING',
    processing_stages JSONB NULL,
    error_message TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

**Columns:**

- `id`: Unique identifier for the video processing job
- `video_id`: Foreign key referencing the associated video in public.videos
- `status`: Current status of the job using the processing_status_enum type
- `processing_stages`: JSONB field to store detailed progress of various processing stages
- `error_message`: Stores any error message if the job failed
- `created_at`: Timestamp of when the job record was created
- `updated_at`: Timestamp of when the job record was last updated

#### `public.video_metadata`

Stores AI-generated metadata for processed videos.

```sql
CREATE TABLE public.video_metadata (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES public.video_jobs(id) ON DELETE CASCADE NOT NULL UNIQUE,
    title TEXT NULL,
    description TEXT NULL,
    tags TEXT[] NULL,
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
```

**Columns:**

- `id`: Unique identifier for the metadata record
- `job_id`: One-to-one foreign key to video_jobs
- `title`: AI-generated video title
- `description`: AI-generated video description
- `tags`: Array of AI-generated tags
- `transcript_text`: Full transcript of the video
- `transcript_file_url`: URL to stored transcript file
- `subtitle_files_urls`: JSONB object with subtitle file URLs (e.g., {"vtt": "url", "srt": "url"})
- `thumbnail_file_url`: URL to generated thumbnail
- `extracted_video_duration_seconds`: Video duration in seconds
- `extracted_video_resolution`: Video resolution (e.g., "1920x1080")
- `extracted_video_format`: Video format (e.g., "mp4")
- `show_notes_text`: AI-generated show notes
- `created_at`: Timestamp of when the metadata was created
- `updated_at`: Timestamp of when the metadata was last updated

### Custom Types

#### `processing_status_enum`

Defines the possible states of a video processing job.

```sql
CREATE TYPE public.processing_status_enum AS ENUM (
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'FAILED'
);
```

### Indexes

```sql
-- Performance indexes for common queries
CREATE INDEX idx_videos_uploader_user_id ON public.videos(uploader_user_id);
CREATE INDEX idx_video_jobs_video_id ON public.video_jobs(video_id);
CREATE INDEX idx_video_jobs_status ON public.video_jobs(status);
CREATE INDEX idx_video_metadata_job_id ON public.video_metadata(job_id);
```

## Row Level Security (RLS)

RLS ensures users can only access their own data. All tables have RLS enabled with appropriate policies.

### Videos Table Policies

```sql
-- Users can select their own videos
CREATE POLICY "Users can select their own videos" ON public.videos
FOR SELECT TO authenticated
USING ((SELECT auth.uid()) = uploader_user_id);

-- Users can insert videos for themselves
CREATE POLICY "Users can insert their own videos" ON public.videos
FOR INSERT TO authenticated
WITH CHECK ((SELECT auth.uid()) = uploader_user_id);

-- Users can update their own videos
CREATE POLICY "Users can update their own videos" ON public.videos
FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = uploader_user_id)
WITH CHECK ((SELECT auth.uid()) = uploader_user_id);

-- Users can delete their own videos
CREATE POLICY "Users can delete their own videos" ON public.videos
FOR DELETE TO authenticated
USING ((SELECT auth.uid()) = uploader_user_id);
```

### Video Jobs Table Policies

```sql
-- Users can access jobs for their videos
CREATE POLICY "Users can select jobs for their videos" ON public.video_jobs
FOR SELECT TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.videos v
        WHERE v.id = video_jobs.video_id
        AND v.uploader_user_id = (SELECT auth.uid())
    )
);

-- Similar policies for INSERT, UPDATE, DELETE...
```

## Database Functions

### Automatic Timestamp Updates

```sql
-- Function to update updated_at column
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER SET search_path = '' AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$;

-- Trigger for videos table
CREATE TRIGGER trig_update_videos_updated_at
BEFORE UPDATE ON public.videos
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
```

### Custom Functions

You can create custom functions for complex operations:

```sql
-- Function to get video processing summary
CREATE OR REPLACE FUNCTION get_user_video_summary(user_id UUID)
RETURNS TABLE (
    total_videos BIGINT,
    pending_jobs BIGINT,
    completed_jobs BIGINT,
    failed_jobs BIGINT
) LANGUAGE sql SECURITY DEFINER AS $$
    SELECT
        COUNT(DISTINCT v.id) as total_videos,
        COUNT(CASE WHEN vj.status = 'PENDING' THEN 1 END) as pending_jobs,
        COUNT(CASE WHEN vj.status = 'COMPLETED' THEN 1 END) as completed_jobs,
        COUNT(CASE WHEN vj.status = 'FAILED' THEN 1 END) as failed_jobs
    FROM public.videos v
    LEFT JOIN public.video_jobs vj ON v.id = vj.video_id
    WHERE v.uploader_user_id = user_id;
$$;
```

---

> **For migration workflows, local development setup, and production deployment**, see the main [README.md](./README.md) which covers the complete database-first development workflow.
