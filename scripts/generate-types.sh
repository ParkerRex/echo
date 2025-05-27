#!/bin/bash

# Generate types from Supabase database
# This script generates TypeScript types from the database schema

set -e

echo "🔄 Generating types from Supabase database..."

# Navigate to supabase directory
cd packages/supabase

# Generate TypeScript types from local database
echo "📝 Generating TypeScript types..."
supabase gen types typescript --local > types/database.ts

echo "✅ TypeScript types generated successfully!"

# Navigate back to root
cd ../..

echo ""
echo "🎉 Type generation complete!"
echo ""
echo "📁 Generated files:"
echo "  • packages/supabase/types/database.ts"
echo ""
echo "💡 Usage in TypeScript:"
echo "  import { Database } from '@echo/db/types'"
echo ""
echo "💡 Usage in Python:"
echo "  from apps.core.app.db.supabase_client import supabase_client"
echo "  result = supabase_client.get_video(video_id)"
