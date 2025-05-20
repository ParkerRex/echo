-- Migration: Create videos table with RLS for Echo platform
-- Created: 2025-05-14T04:42:59Z UTC
-- Purpose: Introduces the core 'videos' table for user-uploaded video records, with row-level security policies for user isolation.
-- 1. Create the videos table
create table if not exists public.videos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  title text,
  description text,
  tags text [],
  subtitles text,
  thumbnail_gcs_path text,
  original_video_gcs_path text not null,
  processing_status text default 'pending',
  created_at timestamptz default timezone('utc'::text, now()),
  updated_at timestamptz default timezone('utc'::text, now())
);
-- 2. Trigger to auto-update updated_at
create or replace function public.update_updated_at_column() returns trigger language plpgsql security invoker
set search_path = '' as $$ begin new.updated_at = timezone('utc'::text, now());
return new;
end;
$$;
drop trigger if exists update_videos_updated_at on public.videos;
create trigger update_videos_updated_at before
update on public.videos for each row execute function public.update_updated_at_column();
-- 3. Enable Row Level Security (RLS)
alter table public.videos enable row level security;
-- 4. RLS Policies
-- SELECT: Users can select their own videos
create policy "Users can select their own videos" on public.videos for
select to authenticated using (
    (
      select auth.uid()
    ) = user_id
  );
-- INSERT: Users can insert their own videos
create policy "Users can insert their own videos" on public.videos for
insert to authenticated with check (
    (
      select auth.uid()
    ) = user_id
  );
-- UPDATE: Users can update their own videos
create policy "Users can update their own videos" on public.videos for
update to authenticated using (
    (
      select auth.uid()
    ) = user_id
  ) with check (
    (
      select auth.uid()
    ) = user_id
  );
-- DELETE: Users can delete their own videos
create policy "Users can delete their own videos" on public.videos for delete to authenticated using (
  (
    select auth.uid()
  ) = user_id
);
-- Index for user_id to optimize policy checks
create index if not exists idx_videos_user_id on public.videos(user_id);
-- End of migration