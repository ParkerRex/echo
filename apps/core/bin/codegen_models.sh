#!/usr/bin/env bash
set -euo pipefail

# Navigate to project root to find .env
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJECT_ROOT_DIR"

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
  set -a # automatically export all variables
  source "$ENV_FILE"
  set +a
else
  echo "Warning: .env file not found at project root. DATABASE_URL might not be set."
fi

# Check if DATABASE_URL is set, fallback to default local Supabase URL if not.
DB_URL_TO_USE="${DATABASE_URL:-postgresql://postgres:postgres@localhost:54322/postgres}"

if [ "${DATABASE_URL}" != "${DB_URL_TO_USE}" ] && [ -z "${DATABASE_URL}" ]; then
    echo "Warning: DATABASE_URL not set in .env, using default: ${DB_URL_TO_USE}"
fi

echo "Generating SQLAlchemy models from ${DB_URL_TO_USE}..."
# Ensure the output directory exists
mkdir -p "${PROJECT_ROOT_DIR}/apps/core/app/db"

# Run sqlacodegen using uv to ensure it uses the project's Python environment and dependencies
# Using the default generator which is declarative for SQLAlchemy
uv run sqlacodegen "${DB_URL_TO_USE}" --outfile "${PROJECT_ROOT_DIR}/apps/core/app/db/models.py"

echo "SQLAlchemy models generated in apps/core/app/db/models.py"
echo "Reminder: Update Pydantic schemas in apps/core/app/db/schemas.py using pydantic-sqlalchemy-2 if needed."