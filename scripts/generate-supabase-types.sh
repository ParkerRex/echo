#!/bin/bash

# Generate Supabase TypeScript types from local database
# This script should be run whenever the database schema changes

set -e

echo "🔄 Generating Supabase TypeScript types..."

# Navigate to the supabase directory
cd "$(dirname "$0")/../packages/supabase"

# Check if Supabase CLI is available
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI is not installed. Please install it first:"
    echo "   npm install -g supabase"
    exit 1
fi

# Generate types from local database
echo "📝 Generating types from local Supabase database..."
supabase gen types typescript --local > types/generated.ts

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo "✅ Supabase types generated successfully!"
    echo "📁 Types saved to: packages/supabase/types/generated.ts"
    
    # Show a summary of what was generated
    echo ""
    echo "📊 Generated types summary:"
    grep -E "(Tables|Enums|Functions)" types/generated.ts | head -10
    
    echo ""
    echo "🔧 To use these types in your application:"
    echo "   import type { Database, Tables } from '@echo/db'"
    echo ""
    echo "💡 Remember to commit the generated types to version control!"
else
    echo "❌ Failed to generate Supabase types"
    exit 1
fi 