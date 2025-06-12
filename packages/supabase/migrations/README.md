# Database Migrations

This directory contains Supabase database migrations for the Echo project.

## Quick Reference

For comprehensive database documentation including schema, RLS policies, and migration best practices, see the main [README.md](../../../README.md#database--migrations) file.

## Common Commands

```bash
# From project root:
# Start local Supabase
bun db:start

# Create new migration
cd packages/supabase
supabase migration new <descriptive_name>

# Apply migrations to local database
bun db:push

# Reset local database (careful!)
bun db:reset

# Generate types from database schema
bun gen:types:db

# Generate migration from schema diff
cd packages/supabase
supabase db diff --schema public
```

## Migration Files

Migration files are named with timestamps and should follow this pattern:
- `YYYYMMDDHHMMSS_descriptive_name.sql`
- Always wrap changes in `BEGIN;` and `COMMIT;`
- Include rollback instructions in comments

## Current Schema

The database includes these main tables:
- `public.videos` - Video file information
- `public.video_jobs` - Processing job status
- `public.video_metadata` - AI-generated metadata

For detailed schema documentation and development guidelines, see the main [README.md](../../../README.md).
