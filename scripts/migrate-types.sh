#!/bin/bash

# Just install the damn types package and make it work

set -e

echo "🔄 Setting up unified types..."

# Install types package
echo "📦 Installing @echo/types..."
cd packages/types
pnpm install
cd ../..

# Install it in the web app too
echo "📦 Adding types to web app..."
cd apps/web
pnpm add @echo/types@workspace:*
cd ../..

echo "✅ Types package ready!"
echo ""
echo "Now you can import like this:"
echo "  import { Video, VideoResponse, ProcessingStatus } from '@echo/types'"
echo ""
echo "🚀 Run 'pnpm typecheck' to make sure everything works"

exit 0

# Old migration guide below (ignore this)
cat > /dev/null << 'EOF'
# Type System Migration Guide

## Overview
This guide helps you migrate from the dual-track type system to the unified @echo/types package.

## Import Changes

### Before (Dual Track)
```typescript
// Database operations
import type { Tables } from "@echo/db/types";
type Video = Tables<"videos">;

// API operations
import type { VideoResponse } from "~/types/api";
```

### After (Unified)
```typescript
// For database operations
import type { DatabaseVideo } from "@echo/types";

// For API operations
import type { VideoResponse } from "@echo/types";

// Or use namespaced imports for clarity
import type { Database, API } from "@echo/types";
type Video = Database.Video;
type ApiVideo = API.VideoResponse;
```

## Migration Steps

1. **Update imports in components**:
   - Replace `import type { Tables } from "@echo/db/types"`
   - With `import type { DatabaseVideo } from "@echo/types"`

2. **Update API type imports**:
   - Replace `import type { VideoResponse } from "~/types/api"`
   - With `import type { VideoResponse } from "@echo/types"`

3. **Update enum usage**:
   - Replace multiple ProcessingStatus imports
   - With single `import { ProcessingStatus } from "@echo/types"`

## Benefits After Migration

- ✅ Single import path for all types
- ✅ Consistent naming across the codebase
- ✅ Better IntelliSense and autocomplete
- ✅ Easier maintenance and updates
- ✅ Type safety maintained throughout

## Rollback Plan

If issues arise, you can rollback by:
1. Reverting import changes
2. Using the original type generation commands
3. The old type files remain unchanged during migration
EOF

echo "✅ Migration preparation complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Review the generated types in packages/types/src/"
echo "  2. Read MIGRATION_GUIDE.md for detailed migration steps"
echo "  3. Update frontend imports gradually"
echo "  4. Test thoroughly before removing old type files"
echo ""
echo "🚀 Run 'pnpm gen:types:unified' to regenerate types after database changes"
