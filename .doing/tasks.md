## Full Task List: Database, Backend, and Frontend Synchronization for End-to-End Type Safety

**Objective:** To establish a robust and type-safe data flow from the Supabase database through the Python backend (SQLAlchemy ORM models, Pydantic API Schemas) to the TypeScript frontend types. This involves restructuring the database, regenerating/refining models, and updating the respective layers of the application.

**Core Problem Addressed:** The current database schema (based on the single `videos` table in the old migration) is insufficient and needs to be expanded to properly represent `videos`, `video_jobs`, and `video_metadata` as distinct but related entities.

**Key Tools & Libraries:**
*   Supabase CLI (for migrations)
*   `sqlacodegen` (for generating SQLAlchemy ORM models from the database)
*   `supabase-pydantic` (for generating Pydantic models directly from the Supabase schema)
*   `pydantic-to-typescript` (for generating TypeScript types from Pydantic API schemas)

---

**Phase 1: Database Schema Definition & Migration**

*   **Task 1.1: Finalize Table Structures (Conceptual)**
    *   **Objective:** Confirm the columns, types, relationships, and constraints for `videos`, `video_jobs`, and `video_metadata` tables.
    *   **Details:**
        *   **`public.videos` Table:**
            *   `id`: `SERIAL PRIMARY KEY` (Auto-incrementing integer, maps to `VideoModel.id`)
            *   `uploader_user_id`: `UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL` (Links to Supabase auth user)
            *   `original_filename`: `TEXT NOT NULL`
            *   `storage_path`: `TEXT NOT NULL UNIQUE` (Path to the original video, e.g., in GCS)
            *   `content_type`: `TEXT NOT NULL` (e.g., "video/mp4")
            *   `size_bytes`: `BIGINT NOT NULL`
            *   `created_at`: `TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL`
            *   `updated_at`: `TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL`
        *   **`public.video_jobs` Table:**
            *   `id`: `SERIAL PRIMARY KEY` (Maps to `VideoJobModel.id`)
            *   `video_id`: `INTEGER REFERENCES public.videos(id) ON DELETE CASCADE NOT NULL` (Foreign key to `videos` table)
            *   `status`: `public.processing_status_enum NOT NULL DEFAULT 'PENDING'` (PostgreSQL ENUM type: `('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')`)
            *   `processing_stages`: `JSONB NULL` (Stores progress, e.g., `{"transcription": "done", "metadata_extraction": "pending"}`)
            *   `error_message`: `TEXT NULL`
            *   `created_at`: `TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL`
            *   `updated_at`: `TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL`
        *   **`public.video_metadata` Table:**
            *   `id`: `SERIAL PRIMARY KEY` (Maps to `VideoMetadataModel.id`)
            *   `job_id`: `INTEGER REFERENCES public.video_jobs(id) ON DELETE CASCADE NOT NULL UNIQUE` (One-to-one with `video_jobs`)
            *   `title`: `TEXT NULL`
            *   `description`: `TEXT NULL`
            *   `tags`: `TEXT[] NULL` (Array of text for tags)
            *   `transcript_text`: `TEXT NULL`
            *   `transcript_file_url`: `TEXT NULL` (URL to stored transcript file)
            *   `subtitle_files_urls`: `JSONB NULL` (e.g., `{"vtt": "url_to_vtt", "srt": "url_to_srt"}`)
            *   `thumbnail_file_url`: `TEXT NULL` (URL to stored thumbnail)
            *   `extracted_video_duration_seconds`: `FLOAT NULL`
            *   `extracted_video_resolution`: `TEXT NULL` (e.g., "1920x1080")
            *   `extracted_video_format`: `TEXT NULL` (e.g., "mp4")
            *   `show_notes_text`: `TEXT NULL`
            *   `created_at`: `TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL`
            *   `updated_at`: `TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL`

*   **Task 1.2: Create/Update SQL Migration File**
    *   **Objective:** Write the SQL to create these tables, define the `processing_status_enum` type, set up RLS policies, and create `updated_at` triggers.
    *   **File to Modify:** `packages/db/migrations/20250514044259_create_videos_table.sql`
        *   *(Note: In a production workflow with existing data, you would create a new additive migration. For a development reset, modifying the existing one is acceptable if you intend to reset the DB.)*
    *   **Action:** Replace the entire content of this file with the following SQL. This SQL includes the enum, tables, triggers, RLS, and comments as per best practices.

        ```sql
        -- Migration: Setup video processing tables (videos, video_jobs, video_metadata)
        -- Original Timestamp: 20250514044259 (retained for filename consistency if modifying)
        -- Purpose: Defines the core data structure for the video processing pipeline,
        -- including tables for video uploads, processing jobs, and generated metadata,
        -- along with appropriate RLS policies for user data isolation and an enum for job status.

        BEGIN;

        -- 0. Create ENUM type for processing_status if it doesn't exist
        -- This ensures the type is available before being used in table definitions.
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'processing_status_enum') THEN
                CREATE TYPE public.processing_status_enum AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');
            END IF;
        END$$;

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
        CREATE OR REPLACE FUNCTION public.update_updated_at_column()
        RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER SET search_path = '' AS $$
        BEGIN
            NEW.updated_at = timezone('utc'::text, now());
            RETURN NEW;
        END;
        $$;

        -- Trigger for 'videos' table to automatically update 'updated_at'
        DROP TRIGGER IF EXISTS trig_update_videos_updated_at ON public.videos;
        CREATE TRIGGER trig_update_videos_updated_at
        BEFORE UPDATE ON public.videos
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

        -- RLS for 'videos' table
        ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;

        -- Policy: Users can select their own videos.
        DROP POLICY IF EXISTS "Users can select their own videos" ON public.videos;
        CREATE POLICY "Users can select their own videos" ON public.videos
        FOR SELECT TO authenticated USING ((SELECT auth.uid()) = uploader_user_id);

        -- Policy: Users can insert videos for themselves.
        DROP POLICY IF EXISTS "Users can insert their own videos" ON public.videos;
        CREATE POLICY "Users can insert their own videos" ON public.videos
        FOR INSERT TO authenticated WITH CHECK ((SELECT auth.uid()) = uploader_user_id);

        -- Policy: Users can update their own videos.
        DROP POLICY IF EXISTS "Users can update their own videos" ON public.videos;
        CREATE POLICY "Users can update their own videos" ON public.videos
        FOR UPDATE TO authenticated USING ((SELECT auth.uid()) = uploader_user_id) WITH CHECK ((SELECT auth.uid()) = uploader_user_id);

        -- Policy: Users can delete their own videos.
        DROP POLICY IF EXISTS "Users can delete their own videos" ON public.videos;
        CREATE POLICY "Users can delete their own videos" ON public.videos
        FOR DELETE TO authenticated USING ((SELECT auth.uid()) = uploader_user_id);

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
        CREATE TRIGGER trig_update_video_jobs_updated_at
        BEFORE UPDATE ON public.video_jobs
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

        -- RLS for 'video_jobs' table
        ALTER TABLE public.video_jobs ENABLE ROW LEVEL SECURITY;

        -- Policy: Users can select jobs related to their own videos.
        DROP POLICY IF EXISTS "Users can select jobs for their videos" ON public.video_jobs;
        CREATE POLICY "Users can select jobs for their videos" ON public.video_jobs
        FOR SELECT TO authenticated USING (
            EXISTS (SELECT 1 FROM public.videos v WHERE v.id = video_jobs.video_id AND v.uploader_user_id = (SELECT auth.uid()))
        );

        -- Policy: Users can insert jobs for their own videos.
        DROP POLICY IF EXISTS "Users can insert jobs for their videos" ON public.video_jobs;
        CREATE POLICY "Users can insert jobs for their videos" ON public.video_jobs
        FOR INSERT TO authenticated WITH CHECK (
            EXISTS (SELECT 1 FROM public.videos v WHERE v.id = video_jobs.video_id AND v.uploader_user_id = (SELECT auth.uid()))
        );

        -- Policy: Users can update jobs related to their own videos.
        DROP POLICY IF EXISTS "Users can update jobs for their videos" ON public.video_jobs;
        CREATE POLICY "Users can update jobs for their videos" ON public.video_jobs
        FOR UPDATE TO authenticated USING (
             EXISTS (SELECT 1 FROM public.videos v WHERE v.id = video_jobs.video_id AND v.uploader_user_id = (SELECT auth.uid()))
        ) WITH CHECK (
            EXISTS (SELECT 1 FROM public.videos v WHERE v.id = video_jobs.video_id AND v.uploader_user_id = (SELECT auth.uid()))
        );

        -- Policy: Users can delete jobs related to their own videos.
        DROP POLICY IF EXISTS "Users can delete jobs for their videos" ON public.video_jobs;
        CREATE POLICY "Users can delete jobs for their videos" ON public.video_jobs
        FOR DELETE TO authenticated USING (
            EXISTS (SELECT 1 FROM public.videos v WHERE v.id = video_jobs.video_id AND v.uploader_user_id = (SELECT auth.uid()))
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
        CREATE TRIGGER trig_update_video_metadata_updated_at
        BEFORE UPDATE ON public.video_metadata
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

        -- RLS for 'video_metadata' table
        ALTER TABLE public.video_metadata ENABLE ROW LEVEL SECURITY;

        -- Policy: Users can select metadata for jobs related to their own videos.
        DROP POLICY IF EXISTS "Users can select metadata for their video jobs" ON public.video_metadata;
        CREATE POLICY "Users can select metadata for their video jobs" ON public.video_metadata
        FOR SELECT TO authenticated USING (
            EXISTS (
                SELECT 1
                FROM public.video_jobs vj
                JOIN public.videos v ON vj.video_id = v.id
                WHERE vj.id = video_metadata.job_id AND v.uploader_user_id = (SELECT auth.uid())
            )
        );

        -- Policy: Users can insert metadata for jobs related to their own videos.
        DROP POLICY IF EXISTS "Users can insert metadata for their video jobs" ON public.video_metadata;
        CREATE POLICY "Users can insert metadata for their video jobs" ON public.video_metadata
        FOR INSERT TO authenticated WITH CHECK (
            EXISTS (
                SELECT 1
                FROM public.video_jobs vj
                JOIN public.videos v ON vj.video_id = v.id
                WHERE vj.id = video_metadata.job_id AND v.uploader_user_id = (SELECT auth.uid())
            )
        );

        -- Policy: Users can update metadata for jobs related to their own videos.
        DROP POLICY IF EXISTS "Users can update metadata for their video jobs" ON public.video_metadata;
        CREATE POLICY "Users can update metadata for their video jobs" ON public.video_metadata
        FOR UPDATE TO authenticated USING (
            EXISTS (
                SELECT 1
                FROM public.video_jobs vj
                JOIN public.videos v ON vj.video_id = v.id
                WHERE vj.id = video_metadata.job_id AND v.uploader_user_id = (SELECT auth.uid())
            )
        ) WITH CHECK (
            EXISTS (
                SELECT 1
                FROM public.video_jobs vj
                JOIN public.videos v ON vj.video_id = v.id
                WHERE vj.id = video_metadata.job_id AND v.uploader_user_id = (SELECT auth.uid())
            )
        );

        -- Policy: Users can delete metadata for jobs related to their own videos.
        DROP POLICY IF EXISTS "Users can delete metadata for their video jobs" ON public.video_metadata;
        CREATE POLICY "Users can delete metadata for their video jobs" ON public.video_metadata
        FOR DELETE TO authenticated USING (
            EXISTS (
                SELECT 1
                FROM public.video_jobs vj
                JOIN public.videos v ON vj.video_id = v.id
                WHERE vj.id = video_metadata.job_id AND v.uploader_user_id = (SELECT auth.uid())
            )
        );

        -- Index for the foreign key job_id
        CREATE INDEX IF NOT EXISTS idx_video_metadata_job_id ON public.video_metadata(job_id);

        COMMIT;
        ```

*   **Task 1.3: Apply Database Changes**
    *   **Objective:** Update your local Supabase instance with the new schema.
    *   **Commands (from project root):**
        1.  Ensure Supabase local development environment is running: `pnpm db:start` (if not already running).
        2.  Reset the database to apply the modified migration cleanly: `pnpm db:reset`
            *   *(This command will wipe any existing local data and re-apply all migrations from scratch. This is suitable for this major schema change in a development environment. For production, you'd use `supabase db push` or a more controlled migration strategy.)*
    *   **Verification:**
        *   Open Supabase Studio (usually at `http://localhost:54323`).
        *   Navigate to the `Table Editor` section.
        *   Verify that `videos`, `video_jobs`, and `video_metadata` tables exist in the `public` schema with the correct columns, types, primary keys, and foreign key relationships.
        *   Verify that RLS is enabled for each table (look for the shield icon).
        *   Check the "Policies" tab for each table to ensure the defined RLS policies are present.
        *   In the `SQL Editor`, run `SELECT enum_range(NULL::public.processing_status_enum);` to verify the `processing_status_enum` type exists and has the correct values: `(PENDING,PROCESSING,COMPLETED,FAILED)`.

---

**Phase 2: Python Backend Code Generation & Model Alignment**

*   **Task 2.1: Update Python Dependencies (If Necessary)**
    *   **Objective:** Ensure `pyproject.toml` includes `supabase-pydantic` and other necessary tools, then install/update dependencies.
    *   **File:** `apps/core/pyproject.toml`
    *   **Action:** Verify that `supabase-pydantic~=0.19.1` (or the version you intend to use) is listed under `[project.dependencies]` or `[project.optional-dependencies.dev]`. Also ensure `sqlacodegen` is present for ORM model generation.
    *   **Command (from project root, then `cd apps/core`):**
        ```bash
        cd apps/core
        # Ensure your Python virtual environment is active
        # (e.g., source .venv/bin/activate or however you manage it)
        uv pip install -e ".[dev]" # Installs package in editable mode with dev dependencies
        ```
    *   **Verification:** The command completes successfully. If `uv.lock` is modified, commit it.

*   **Task 2.2: Generate SQLAlchemy ORM Models**
    *   **Objective:** Create initial SQLAlchemy ORM model definitions based on the new database schema.
    *   **Command (from project root):** `pnpm codegen:db-orm-models`
        *   This script (`apps/core/bin/codegen_models.sh`) runs `sqlacodegen` and outputs to `apps/core/app/db/models.py`.
    *   **Verification & Manual Adjustments:**
        1.  Open the generated file: `apps/core/app/db/models.py`.
        2.  It should contain classes like `Videos`, `VideoJobs`, `VideoMetadata` (names might vary slightly based on `sqlacodegen`'s inflection).
        3.  **Crucially, review and adjust relationships:** `sqlacodegen` might not perfectly infer `back_populates` or `uselist=False` for one-to-one relationships. You will likely need to manually edit this file.
            *   Example for `Videos` model:
                ```python
                # In class Videos(Base):
                #   __tablename__ = 'videos'
                #   # ... other columns
                #   jobs = relationship("VideoJobs", back_populates="video") # Ensure correct class name "VideoJobs"
                ```
            *   Example for `VideoJobs` model:
                ```python
                # In class VideoJobs(Base):
                #   __tablename__ = 'video_jobs'
                #   # ... other columns
                #   video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
                #   video = relationship("Videos", back_populates="jobs")
                #   video_metadata = relationship("VideoMetadata", back_populates="job", uselist=False, cascade="all, delete-orphan") # uselist=False for one-to-one
                ```
            *   Example for `VideoMetadata` model:
                ```python
                # In class VideoMetadata(Base):
                #   __tablename__ = 'video_metadata'
                #   # ... other columns
                #   job_id = Column(Integer, ForeignKey('video_jobs.id'), nullable=False, unique=True)
                #   job = relationship("VideoJobs", back_populates="video_metadata")
                ```
        4.  **Adjust Enum Type for `status` column:** The `status` column in the `VideoJobs` model generated by `sqlacodegen` will likely be `Column(Text,...)`. Manually change this to use your Python Enum.
            *   First, ensure your Python enum exists (Task 2.3).
            *   Then, in `apps/core/app/db/models.py` (or later in `apps/core/models/video_job_model.py` after moving), modify the `VideoJobs` class:
                ```python
                from sqlalchemy import Enum # Add Enum to sqlalchemy imports
                from apps.core.models.enums import ProcessingStatus # Path to your Python enum

                # ... inside the VideoJobs class definition ...
                # status = Column(Text, nullable=False, server_default=text("'PENDING'::processing_status_enum")) # Original from sqlacodegen (example)
                status = Column(Enum(ProcessingStatus, name="processing_status_enum", create_type=False), nullable=False, server_default='PENDING')
                # create_type=False because we defined the ENUM type in SQL already.
                # server_default='PENDING' ensures the DB default is also aligned if SQLAlchemy manages table creation (not the case here as migration does it).
                ```

*   **Task 2.3: Create/Verify Python Enum for `ProcessingStatus`**
    *   **Objective:** Ensure a Python enum exists that mirrors the `processing_status_enum` in the database.
    *   **File:** `apps/core/models/enums.py`
    *   **Action:** Create or verify the file with the following content:
        ```python
        from enum import Enum

        class ProcessingStatus(str, Enum):
            PENDING = "PENDING"
            PROCESSING = "PROCESSING"
            COMPLETED = "COMPLETED"
            FAILED = "FAILED"
        ```
    *   **Verification:** Enum values exactly match those defined in the SQL `CREATE TYPE public.processing_status_enum AS ENUM (...)`.

*   **Task 2.4: Consolidate and Refine SQLAlchemy Models into `apps/core/models/`**
    *   **Objective:** Move the generated and manually adjusted ORM model definitions from `apps/core/app/db/models.py` into your structured model files within `apps/core/models/`. This makes them the canonical ORM models for your application.
    *   **Source File:** `apps/core/app/db/models.py`
    *   **Target Files:**
        *   `apps/core/models/video_model.py` (for the `Videos` table's model)
        *   `apps/core/models/video_job_model.py` (for the `VideoJobs` table's model)
        *   `apps/core/models/video_metadata_model.py` (for the `VideoMetadata` table's model)
        *   `apps/core/models/__init__.py` (to export the models)
    *   **Action:**
        1.  For each generated model class (e.g., `Videos`, `VideoJobs`, `VideoMetadata`) in `apps/core/app/db/models.py`:
            *   Copy the class definition.
            *   Paste it into the corresponding target file (e.g., `Videos` class into `video_model.py`).
            *   Rename the class to your desired application-consistent name (e.g., `Videos` to `VideoModel`, `VideoJobs` to `VideoJobModel`, `VideoMetadata` to `VideoMetadataModel`).
            *   Adjust imports within these files. Common imports will be:
                ```python
                from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Enum, Float, BigInteger # etc.
                from sqlalchemy.orm import relationship
                from sqlalchemy.sql import func # For server_default=func.now()
                from apps.core.lib.database.connection import Base # Assuming Base is defined here
                from ..enums import ProcessingStatus # For VideoJobModel, if enums.py is in the same directory
                # For relationships, use string references to avoid circular imports if models are in separate files:
                # e.g., video = relationship("VideoModel", back_populates="jobs")
                ```
            *   Ensure all relationships (`relationship(...)`) use the new class names and correctly define `back_populates`.
        2.  Update `apps/core/models/__init__.py` to export your refined models:
            ```python
            from .enums import ProcessingStatus
            from .video_model import VideoModel
            from .video_job_model import VideoJobModel
            from .video_metadata_model import VideoMetadataModel
            # Add other models like User, Chat, Message if they are part of this structure

            __all__ = [
                "ProcessingStatus",
                "VideoModel",
                "VideoJobModel",
                "VideoMetadataModel",
                # "User", "Chat", "Message"
            ]
            ```
        3.  Once confident, you can delete `apps/core/app/db/models.py` or add it to `.gitignore` as its contents are now managed within `apps/core/models/`. For this guide, assume it's moved and maintained in `apps/core/models/`.
    *   **Verification:** The models in `apps/core/models/` are correctly defined, importable, and reflect the database schema including relationships and the `ProcessingStatus` enum.

*   **Task 2.5: Generate Pydantic Models using `supabase-pydantic`**
    *   **Objective:** Create Pydantic V2 models directly from the live Supabase schema. These models can be useful for direct DB interactions or as a reference for your API schemas.
    *   **Command (from project root):** `pnpm codegen:db-pydantic-models`
        *   This script (`apps/core/bin/codegen_pydantic_supabase.sh`) runs `supabase-pydantic`.
        *   Ensure your `.env` file at the project root has `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` correctly set for `supabase-pydantic` to connect and introspect the schema.
    *   **Output File:** `apps/core/app/db_pydantic_models/supabase_models.py`
    *   **Verification:**
        *   Inspect the generated `supabase_models.py`.
        *   It should contain Pydantic classes corresponding to your tables (e.g., `Videos`, `VideoJobs`, `VideoMetadata`).
        *   Check that types are mapped correctly (e.g., `timestamptz` to `datetime.datetime`, `text[]` to `List[str]`, `jsonb` to `Dict` or `Any`, `processing_status_enum` to a Pydantic `Enum` or `Literal`).
        *   Note: `supabase-pydantic` might generate its own version of the `ProcessingStatus` enum or use `Literal`. You'll need to decide if you use this generated enum or your manually defined Python enum (`apps.core.models.enums.ProcessingStatus`) in your API schemas. Consistency is key.

---

**Phase 3: Python Backend Logic Refactoring**

*   **Task 3.1: Refactor Pydantic API Schemas**
    *   **Objective:** Update your FastAPI request/response schemas to align with the new database structure (three tables) and the refined SQLAlchemy ORM models. These API schemas will be the source for TypeScript type generation.
    *   **File:** `apps/core/api/schemas/video_processing_schemas.py`
    *   **Action:**
        1.  Review each existing schema (e.g., `VideoSchema`, `VideoJobSchema`, `VideoMetadataSchema`, `VideoSummary`, `VideoDetailsResponse`, `VideoUploadResponseSchema`, `VideoMetadataUpdateRequest`).
        2.  **Design Decision:** Your API schemas should reflect the data structures you want to expose to the client. They will be built based on your SQLAlchemy ORM models (from `apps.core.models`).
            *   Create distinct Pydantic schemas for API representation of `Video`, `VideoJob`, and `VideoMetadata`.
            *   Example: `VideoResponseSchema`, `VideoJobResponseSchema`, `VideoMetadataResponseSchema`.
            *   These schemas should include `model_config = ConfigDict(from_attributes=True)` to allow direct creation from SQLAlchemy ORM model instances.
        3.  Update schemas that combine data. For example, `VideoJobResponseSchema` might nest `VideoResponseSchema` and `VideoMetadataResponseSchema` if you want to return job details along with its related video and metadata.
            ```python
            # Example structure in apps/core/api/schemas/video_processing_schemas.py

            from datetime import datetime
            from typing import List, Optional, Any, Dict, Union # Union for processing_stages
            from pydantic import BaseModel, Field, ConfigDict
            from apps.core.models.enums import ProcessingStatus # Your canonical Python enum

            class VideoResponseSchema(BaseModel):
                id: int
                uploader_user_id: str # Assuming UUID is converted to str for API
                original_filename: str
                # storage_path: str # Potentially not exposed directly in all responses
                content_type: str
                size_bytes: int
                created_at: datetime
                updated_at: datetime
                model_config = ConfigDict(from_attributes=True)

            class VideoMetadataResponseSchema(BaseModel):
                id: int
                # job_id: int # Usually linked via VideoJobResponseSchema
                title: Optional[str] = None
                description: Optional[str] = None
                tags: Optional[List[str]] = Field(default_factory=list)
                transcript_text: Optional[str] = None # Or just URL if text is too large
                transcript_file_url: Optional[str] = None
                subtitle_files_urls: Optional[Dict[str, Any]] = Field(default_factory=dict) # e.g. {"vtt": "url", "srt": "url"}
                thumbnail_file_url: Optional[str] = None
                extracted_video_duration_seconds: Optional[float] = None
                extracted_video_resolution: Optional[str] = None
                extracted_video_format: Optional[str] = None
                show_notes_text: Optional[str] = None # Or URL
                created_at: datetime
                updated_at: datetime
                model_config = ConfigDict(from_attributes=True)

            class VideoJobResponseSchema(BaseModel):
                id: int
                video_id: int
                status: ProcessingStatus # Use your Python enum
                processing_stages: Optional[Union[List[str], Dict[str, Any]]] = None # Flexible for stages
                error_message: Optional[str] = None
                created_at: datetime
                updated_at: datetime
                video: Optional[VideoResponseSchema] = None # For nested video details
                metadata: Optional[VideoMetadataResponseSchema] = None # For nested metadata
                model_config = ConfigDict(from_attributes=True, extra="ignore") # extra='ignore' can be useful

            class VideoUploadResponseSchema(BaseModel): # For the /upload endpoint response
                job_id: int
                status: ProcessingStatus

            class VideoSummarySchema(BaseModel): # For list views
                id: int # This is VideoModel.id
                original_filename: str
                title: Optional[str] = None # From VideoMetadataModel.title via the latest job
                created_at: datetime # VideoModel.created_at
                status: Optional[ProcessingStatus] = None # VideoJobModel.status for the latest job
                thumbnail_file_url: Optional[str] = None # VideoMetadataModel.thumbnail_file_url
                model_config = ConfigDict(from_attributes=True) # If built from ORM objects with joins

            class VideoMetadataUpdateRequestSchema(BaseModel): # For updating metadata
                title: Optional[str] = None
                description: Optional[str] = None
                tags: Optional[List[str]] = None
                # Add other editable fields as needed
            ```
        4.  Ensure all schemas use `datetime.datetime` for date/time fields (Pydantic V2 standard).
        5.  The `status` field in `VideoJobResponseSchema` must use your Python enum `apps.core.models.enums.ProcessingStatus`.
    *   **Verification:** API schemas in `apps/core/api/schemas/video_processing_schemas.py` are well-defined, use correct types (especially `ProcessingStatus` and `datetime`), have `from_attributes=True` where ORM instances are returned by services, and are ready for `pydantic-to-typescript`.

*   **Task 3.2: Update Repository Layer (`apps/core/operations/`)**
    *   **Objective:** Ensure repositories use the correct SQLAlchemy ORM models (from `apps.core.models`) and query the new table structures. All repository methods should now be `async`.
    *   **Files to Update:**
        *   `apps/core/operations/video_repository.py`
        *   `apps/core/operations/video_job_repository.py`
        *   `apps/core/operations/video_metadata_repository.py`
    *   **Action:**
        1.  **Imports:** Change imports from `apps.core.app.db.models` or old model paths to `from apps.core.models import VideoModel, VideoJobModel, VideoMetadataModel, ProcessingStatus`.
        2.  **Async Methods:** Convert all synchronous methods (`def`) to asynchronous (`async def`). All database operations (`db.execute`, `db.add`, `db.commit`, `db.refresh`, `db.flush`) must be `await`ed. The `db` parameter type hint should be `AsyncSession`.
        3.  **`VideoRepository`**:
            *   `create`: Should now create a `VideoModel` instance.
            *   `get_by_id`: Should fetch `VideoModel`.
        4.  **`VideoJobRepository`**:
            *   `create`: Creates a `VideoJobModel` linking to `video_id`.
            *   `get_by_id`: Fetches `VideoJobModel`. Consider eager loading related `video` and `video_metadata` here if frequently needed together:
                ```python
                # Example in VideoJobRepository.get_by_id
                from sqlalchemy.orm import joinedload
                # ...
                stmt = (
                    select(VideoJobModel)
                    .filter(VideoJobModel.id == job_id)
                    .options(
                        joinedload(VideoJobModel.video),
                        joinedload(VideoJobModel.video_metadata)
                    )
                )
                result = await db.execute(stmt)
                return result.scalars().first()
                ```
            *   `update_status`: Updates `VideoJobModel.status` and `error_message`.
            *   `add_processing_stage`: Updates `VideoJobModel.processing_stages`.
            *   `get_by_user_id_and_statuses`: This method is crucial. It needs to join `VideoJobModel` with `VideoModel` to filter by `uploader_user_id`. Ensure it also uses eager loading for `video` and `video_metadata` if these are part of the response schema.
                ```python
                # In apps/core/operations/video_job_repository.py
                from sqlalchemy.orm import joinedload
                # ...
                @staticmethod
                async def get_by_user_id_and_statuses(
                    db: AsyncSession,
                    user_id: str, # This is VideoModel.uploader_user_id (UUID as str from Supabase)
                    statuses: Optional[List[ProcessingStatus]] = None,
                    limit: int = 100,
                    offset: int = 0,
                ) -> List[VideoJobModel]:
                    stmt = (
                        select(VideoJobModel)
                        .join(VideoModel, VideoJobModel.video_id == VideoModel.id)
                        .filter(VideoModel.uploader_user_id == user_id)
                    )
                    if statuses:
                        stmt = stmt.filter(VideoJobModel.status.in_(statuses))

                    stmt = stmt.options(
                        joinedload(VideoJobModel.video),
                        joinedload(VideoJobModel.video_metadata) # Eager load metadata
                    ).order_by(VideoJobModel.created_at.desc()).offset(offset).limit(limit)
                    
                    result = await db.execute(stmt)
                    return list(result.scalars().all())
                ```
        5.  **`VideoMetadataRepository`**:
            *   `create_or_update`: Uses `job_id` to find/create `VideoMetadataModel`.
            *   `get_by_job_id`: Fetches `VideoMetadataModel`.
        6.  **Dependency Injection for Repositories:** Ensure repository getter functions (e.g., `get_video_repository`) are updated if necessary, though if they are simple type hints or class instantiations, they might not need changes beyond what FastAPI handles for `Depends`.
    *   **Verification:** Repository methods are `async`, use `AsyncSession`, align with the new ORM models, and database queries are correct for the new schema. Eager loading is implemented where appropriate.

*   **Task 3.3: Update Service Layer (`apps/core/services/`)**
    *   **Objective:** Adapt service logic to the new three-model structure and asynchronous repository methods.
    *   **Files to Update:**
        *   `apps/core/services/video_processing_service.py`
        *   `apps/core/services/job_service.py`
        *   Potentially `apps/core/services/metadata_service.py` if it interacts directly with these models/repos.
    *   **Action:**
        1.  **Async Calls:** All calls to repository methods must now be `await`ed. Service methods interacting with repos will likely become `async def`.
        2.  **`VideoProcessingService.initiate_video_processing`**:
            *   Save video file to storage (already async).
            *   `await self.video_repo.create(...)` to create `VideoModel`.
            *   `await self.job_repo.create(...)` to create `VideoJobModel`, linking it to the `VideoModel.id`.
            *   `await db.commit()` (session passed to the service method).
            *   Schedule `_execute_processing_pipeline` (which is async) in background tasks.
        3.  **`VideoProcessingService._execute_processing_pipeline`**:
            *   This method runs in a background task and should manage its own `AsyncSession`.
                ```python
                # At the beginning of _execute_processing_pipeline
                async with AsyncSessionLocal() as db_bg: # Create a new session for the background task
                    # ... rest of the logic using db_bg ...
                    await self.job_repo.get_by_id(db_bg, job_id)
                    # ...
                    await db_bg.commit()
                ```
            *   Fetch `VideoJobModel` using `await self.job_repo.get_by_id(db_bg, job_id)`.
            *   Access related `VideoModel` via `job.video` (ensure it's loaded, possibly via eager loading in `job_repo.get_by_id`).
            *   When saving metadata (title, description, transcript URL, etc.), create/update a `VideoMetadataModel` instance using `await self.metadata_repo.create_or_update(db_bg, job_id=job.id, title=...)`.
            *   Update `VideoJobModel` status and stages using `await self.job_repo.update_status(...)` and `await self.job_repo.add_processing_stage(...)`.
            *   Commit changes within the background task's session: `await db_bg.commit()`.
        4.  **`VideoProcessingService.get_job_details`**:
            *   Fetch `VideoJobModel` using `await self.job_repo.get_by_id(db, job_id)`.
            *   The eager loading in `job_repo.get_by_id` should make `job.video` and `job.video_metadata` available.
            *   Perform authorization check: `job.video.uploader_user_id == user_id`.
        5.  **`JobService.get_user_jobs_by_statuses`**:
            *   This service should now correctly call `await VideoJobRepository.get_by_user_id_and_statuses(...)`. The returned `VideoJobModel` instances should have their `video` and `video_metadata` relationships populated due to eager loading in the repository.
    *   **Verification:** Service logic correctly orchestrates `async` operations across the new models and repositories. Background tasks manage their own sessions. Data flow between services and repositories is correct.

*   **Task 3.4: Update API Endpoints (`apps/core/api/endpoints/`)**
    *   **Objective:** Ensure API endpoints use the correct Pydantic API schemas (from `apps.core.api.schemas.video_processing_schemas`) and make `async` calls to services.
    *   **Files to Update:**
        *   `apps/core/api/endpoints/video_processing_endpoints.py`
        *   `apps/core/api/endpoints/jobs_endpoints.py`
    *   **Action:**
        1.  **Async Endpoints:** All endpoint functions that call `async` service methods must be `async def`.
        2.  **Dependencies:** Ensure `db: AsyncSession = Depends(get_async_db_session)` is used for injecting asynchronous sessions.
        3.  **Response Models:** Update `response_model` in endpoint definitions to use the refactored Pydantic API schemas (e.g., `VideoJobResponseSchema`, `VideoUploadResponseSchema`, `List[VideoSummarySchema]`).
        4.  Ensure data passed to and returned from service calls matches the updated service method signatures and Pydantic API schema expectations.
        5.  For `get_my_processing_jobs` (in `jobs_endpoints.py`), it should return `List[VideoJobResponseSchema]` (or `List[VideoSummarySchema]` if a summary is preferred for lists). The service `get_user_jobs_by_statuses` returns `List[VideoJobModel]`. FastAPI will convert these ORM models to the Pydantic response model using `from_attributes=True`.
        6.  For `upload_video` (in `video_processing_endpoints.py`), the response `VideoUploadResponseSchema` should contain `job_id` and initial `status` from the created `VideoJobModel`.
        7.  For `get_job_details` (in `video_processing_endpoints.py`), the response `VideoJobResponseSchema` should be populated from the `VideoJobModel` returned by the service, including its nested `video` and `metadata` if applicable due to eager loading.
    *   **Verification:** API endpoints are correctly typed with `async def`, use `AsyncSession`, use the correct Pydantic API response schemas, and function correctly with the refactored services. Test with a tool like Postman or by running frontend against it.

---

**Phase 4: TypeScript Type Generation & Frontend Alignment**

*   **Task 4.1: Generate TypeScript Types**
    *   **Objective:** Create up-to-date TypeScript interfaces for the frontend based on the Pydantic API schemas.
    *   **Command (from project root):** `pnpm codegen:api-types`
    *   **Script to Verify/Update (in root `package.json`):**
        ```jsonc
        // In root package.json under "scripts"
        "codegen:api-types": "cd apps/core && uv run pydantic-to-typescript --module apps.core.api.schemas.video_processing_schemas --output ../../apps/web/app/types/api.ts --json2ts-cmd ../../apps/web/node_modules/.bin/json2ts && cd ../..",
        ```
        *   Ensure `--module` points to `apps.core.api.schemas.video_processing_schemas` (where your final API Pydantic schemas are defined).
        *   Ensure `--output` points to `apps/web/app/types/api.ts`.
    *   **Verification:** Open `apps/web/app/types/api.ts`. It should contain TypeScript interfaces like `VideoJobResponseSchema`, `VideoResponseSchema`, `VideoMetadataResponseSchema`, `ProcessingStatus` (as a TypeScript enum or literal union type), etc., matching your Pydantic API schema definitions.

*   **Task 4.2: Update Frontend Code**
    *   **Objective:** Ensure frontend components, hooks, and API calls use the new TypeScript types and expect data in the new structure.
    *   **Key Files/Areas to Update:**
        *   **API Client Functions:** `apps/web/app/lib/api.ts` - Update fetch functions to use new request/response types.
        *   **WebSocket Handling:** `apps/web/app/hooks/useAppWebSocket.ts` and `apps/web/app/hooks/useJobStatusManager.ts` - If WebSocket message structures for job updates change, update the types and handling logic. The `WebSocketJobUpdate` type in `useJobStatusManager.ts` will be critical.
        *   **Video Components:**
            *   `apps/web/app/components/video/ProcessingDashboard.tsx`
            *   `apps/web/app/components/video/VideoList.tsx` & `VideoListItem.tsx` (will likely use `VideoSummarySchema`)
            *   `apps/web/app/components/video/VideoDetail.tsx` (route `/video/$videoId`, will use `VideoJobResponseSchema` or a similar detailed type)
            *   `apps/web/app/components/video/VideoUploadDropzone.tsx` (ensure it aligns with any changes to upload API responses)
        *   **Route Components:** Any routes in `apps/web/app/routes/` that display or interact with video/job data.
        *   **TanStack Query Hooks:** Review `useQuery` and `useMutation` calls to ensure query keys and expected data types match the new API responses.
    *   **Action:**
        1.  Update type imports in frontend files to use the types from `~/types/api` (or the correct relative path to `api.ts`).
        2.  Adjust data access patterns. For example, if `VideoSummarySchema` is now used for lists, ensure components expect this structure. If `VideoJobResponseSchema` now nests `video` and `metadata` objects, update components to access data like `job.video.original_filename` or `job.metadata.title`.
        3.  Pay close attention to how `processing_stages` and `status` are handled and displayed.
    *   **Verification:** Frontend compiles without TypeScript errors. Data fetched from the backend is correctly displayed. UI interactions related to video/job data work as expected.

---

**Phase 5: Testing**

*   **Task 5.1: Update Backend Unit & Integration Tests**
    *   **Objective:** Ensure all backend tests pass with the new schema, asynchronous logic, and model structures.
    *   **Files to Update:** All test files in `apps/core/tests/`.
        *   `apps/core/tests/unit/operations/`: Update repository tests for async methods and new model interactions.
        *   `apps/core/tests/unit/services/`: Update service tests for async calls and new data structures.
        *   `apps/core/tests/api/`: Update API integration tests to expect new request/response structures and test async endpoints.
        *   `apps/core/tests/integration/conftest.py` (or `apps/core/tests/conftest.py`): Update fixtures to create and populate the new `videos`, `video_jobs`, `video_metadata` tables correctly for integration tests. Ensure async session fixtures are used.
    *   **Command (from project root):** `pnpm api:test` (or `cd apps/core && pytest`)
    *   **Verification:** All backend tests pass. Coverage is maintained or improved.

*   **Task 5.2: Frontend Testing (if applicable)**
    *   **Objective:** Ensure frontend tests (unit, integration, E2E) pass with the new types and UI changes.
    *   **Action:** Update any frontend tests in `apps/web/` that interact with video/job data or components displaying this data.
    *   **Verification:** Frontend tests pass.

---

This detailed roadmap should guide you through the process of achieving end-to-end type safety and aligning your database, backend, and frontend. Remember to tackle one phase and task at a time, verifying each step before moving to the next. Good luck!