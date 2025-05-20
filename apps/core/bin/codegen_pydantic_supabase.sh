#!/usr/bin/env bash
set -euo pipefail

# Navigate to project root to find .env and ensure correct relative paths
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJECT_ROOT_DIR"

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
  set -a # automatically export all variables
  source "$ENV_FILE"
  set +a
else
  echo "Warning: .env file not found at project root. DATABASE_URL or Supabase connection details might not be set for supabase-pydantic."
fi

# supabase-pydantic uses environment variables for connection:
# SUPABASE_URL and SUPABASE_KEY (anon or service_role)
# Or, it can use DATABASE_URL.
# Ensure your .env file has these. For schema introspection, SERVICE_ROLE_KEY is best.

OUTPUT_DIR_PYDANTIC="${PROJECT_ROOT_DIR}/apps/core/app/db_pydantic_models"
OUTPUT_FILE_PYDANTIC="${OUTPUT_DIR_PYDANTIC}/supabase_models.py"

mkdir -p "$OUTPUT_DIR_PYDANTIC"

echo "Generating Pydantic models from Supabase schema using supabase-pydantic..."
echo "Outputting to: ${OUTPUT_FILE_PYDANTIC}"

# Ensure SUPABASE_URL and a SUPABASE_KEY (preferably SUPABASE_SERVICE_ROLE_KEY) are set in .env
if [ -z "${SUPABASE_URL}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY}" ]; then
    echo "Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the root .env file for supabase-pydantic."
    # Fallback to DATABASE_URL if the others aren't set, though supabase-pydantic prefers URL/KEY
    if [ -z "${DATABASE_URL}" ]; then
        echo "Error: Neither Supabase URL/Key nor DATABASE_URL are set. Cannot generate Pydantic models."
        exit 1
    else
        echo "Warning: Using DATABASE_URL for supabase-pydantic. URL/KEY method is preferred by the tool."
        # The tool might still pick up DATABASE_URL if others are missing.
    fi
fi

# Command for supabase-pydantic.
# It will pick up SUPABASE_URL and SUPABASE_KEY from the environment.
# Use --service-role-key flag if you want to explicitly tell it to use that key.
CMD_PYDANTIC="uv run supabase-pydantic --output \"${OUTPUT_FILE_PYDANTIC}\" --schema public --pydantic-v2"

# If you want to ensure it uses the service role key for introspection:
# CMD_PYDANTIC="uv run supabase-pydantic --output \"${OUTPUT_FILE_PYDANTIC}\" --schema public --pydantic-v2 --service-role-key"

eval "$CMD_PYDANTIC"

echo "Pydantic models from Supabase schema generated in ${OUTPUT_FILE_PYDANTIC}"
echo "Review the generated models and import them into your FastAPI schemas or services as needed."