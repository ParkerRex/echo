"""
Official Supabase Python Client for Echo Backend

This module provides a clean, trustworthy interface to Supabase using the official
supabase-py client library. It replaces the unreliable third-party supabase-pydantic
package with the official Supabase Python client.

Installation:
    cd apps/core && uv add supabase

Usage:
    from packages.supabase.clients.python import get_supabase_client

    supabase = get_supabase_client()
    result = supabase.table('videos').select('*').execute()

Environment Variables Required:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_ANON_KEY - Public anon key for regular operations
    SUPABASE_SERVICE_ROLE_KEY - Service role key for admin operations
"""

import os
from typing import Any, Dict, Optional

# Import with runtime check - linter may complain but this works at runtime
try:
    from supabase import create_client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    create_client = None


def get_supabase_client(service_role: bool = False):
    """
    Create a Supabase client using the official supabase-py library.

    Args:
        service_role (bool): If True, use service role key for admin operations.
                           If False, use anon key for regular operations.

    Returns:
        Supabase Client instance

    Raises:
        ImportError: If supabase package is not installed
        ValueError: If required environment variables are missing
    """
    if not SUPABASE_AVAILABLE or create_client is None:
        raise ImportError(
            "Official Supabase Python client not installed. "
            "Run: cd apps/core && uv add supabase"
        )

    # Get URL from environment
    supabase_url = os.environ.get("SUPABASE_URL")
    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable is required")

    # Get appropriate key based on service_role flag
    if service_role:
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not supabase_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY environment variable is required "
                "for service role operations"
            )
    else:
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        if not supabase_key:
            raise ValueError("SUPABASE_ANON_KEY environment variable is required")

    # Create client with official library
    return create_client(supabase_url, supabase_key)


def get_admin_client():
    """
    Convenience function to get a service role client for admin operations.

    Returns:
        Supabase client with service role privileges
    """
    return get_supabase_client(service_role=True)


def get_anon_client():
    """
    Convenience function to get an anonymous client for regular operations.

    Returns:
        Supabase client with anonymous privileges
    """
    return get_supabase_client(service_role=False)


def test_connection() -> Dict[str, Any]:
    """
    Test the Supabase connection and return status information.

    Returns:
        Dict with connection status and available operations
    """
    try:
        # Test anonymous client
        anon_client = get_anon_client()

        # Test a simple query (this will fail if connection is bad)
        # Note: This assumes you have a 'videos' table, adjust as needed
        result = anon_client.table("videos").select("id").limit(1).execute()

        return {
            "status": "success",
            "message": "Supabase connection working",
            "anon_client": True,
            "query_test": True,
            "data_count": len(result.data) if hasattr(result, "data") else 0,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "anon_client": False,
            "query_test": False,
        }


# Example usage patterns
def example_usage():
    """
    Example usage patterns for the Supabase client.

    This function demonstrates how to use the client for common operations.
    Remove this function in production.
    """
    # Get a client
    supabase = get_supabase_client()

    # Query data
    result = supabase.table("videos").select("*").execute()

    # Insert data
    new_video = {
        "title": "My Video",
        "uploader_user_id": "user-123",
        "original_filename": "video.mp4",
    }
    insert_result = supabase.table("videos").insert(new_video).execute()

    # Update data
    update_result = (
        supabase.table("videos")
        .update({"title": "Updated Title"})
        .eq("id", "video-id")
        .execute()
    )

    # Delete data
    delete_result = supabase.table("videos").delete().eq("id", "video-id").execute()

    # Admin operations (requires service role)
    try:
        admin_client = get_admin_client()
        user_result = admin_client.auth.admin.get_user_by_id("user-id")
    except Exception as e:
        user_result = f"Admin operation failed: {e}"

    return {
        "query": result,
        "insert": insert_result,
        "update": update_result,
        "delete": delete_result,
        "user": user_result,
    }


if __name__ == "__main__":
    # Quick test when run directly
    print("Testing Supabase connection...")
    status = test_connection()
    print(f"Status: {status}")
