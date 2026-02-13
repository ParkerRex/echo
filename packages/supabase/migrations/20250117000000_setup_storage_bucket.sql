-- Migration: Setup storage bucket for video uploads
-- Description: Creates storage bucket and policies for video file uploads

-- Enable the storage extension if not already enabled
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'uploads',
  'uploads',
  false, -- Private bucket, files need signed URLs
  524288000, -- 500MB limit
  ARRAY['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']::text[]
)
ON CONFLICT (id) DO UPDATE
SET 
  file_size_limit = 524288000,
  allowed_mime_types = ARRAY['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']::text[];

-- Policy: Users can upload files to their own folder
CREATE POLICY "Users can upload their own files" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (
  bucket_id = 'uploads' 
  AND (auth.uid())::text = (storage.foldername(name))[1]
);

-- Policy: Users can view their own files  
CREATE POLICY "Users can view their own files" ON storage.objects
FOR SELECT TO authenticated
USING (
  bucket_id = 'uploads' 
  AND (auth.uid())::text = (storage.foldername(name))[1]
);

-- Policy: Users can update their own files
CREATE POLICY "Users can update their own files" ON storage.objects
FOR UPDATE TO authenticated
USING (
  bucket_id = 'uploads' 
  AND (auth.uid())::text = (storage.foldername(name))[1]
)
WITH CHECK (
  bucket_id = 'uploads' 
  AND (auth.uid())::text = (storage.foldername(name))[1]
);

-- Policy: Users can delete their own files
CREATE POLICY "Users can delete their own files" ON storage.objects
FOR DELETE TO authenticated
USING (
  bucket_id = 'uploads' 
  AND (auth.uid())::text = (storage.foldername(name))[1]
);