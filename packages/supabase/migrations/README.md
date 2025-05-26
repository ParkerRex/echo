# Database Migrations

This directory contains Supabase database migrations for the Echo project.

## Quick Reference

For comprehensive database documentation including schema, RLS policies, and migration best practices, see the main [DATABASE.md](../../../DATABASE.md) file.

## Common Commands

```bash
# Create new migration
supabase migration new <descriptive_name>

# Apply migrations to local database
supabase db push

# Reset local database (careful!)
supabase db reset

# Generate migration from schema diff
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

For detailed schema documentation, see [DATABASE.md](../../../DATABASE.md).
