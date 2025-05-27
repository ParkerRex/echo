"""
Service layer for job-related operations.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.operations.video_job_repository import VideoJobRepository

# Placeholder for CRUD operations if we create a crud_jobs.py
# from apps.core.crud.crud_jobs import get_jobs_by_user_and_statuses


async def get_user_jobs_by_statuses(
    db: AsyncSession,  # Changed to AsyncSession
    user_id: str,  # Supabase User ID (string/UUID)
    statuses: Optional[List[ProcessingStatus]] = None,
) -> List[VideoJobModel]:
    """
    Retrieves video processing jobs for a specific user, filtered by specified statuses.

    Args:
        db: SQLAlchemy async session.
        user_id: The ID of the user (Supabase string UUID).
        statuses: An optional list of ProcessingStatus enums to filter by.
                  If None or empty, this service will default to PENDING and PROCESSING.

    Returns:
        A list of VideoJobModel objects matching the criteria.
    """
    # If no specific statuses are requested by the client,
    # default to fetching PENDING and PROCESSING jobs.
    if not statuses:
        statuses_to_fetch = [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]
    else:
        statuses_to_fetch = statuses

    # Repository method is now async, so await the call.
    jobs = await VideoJobRepository.get_by_user_id_and_statuses(
        db=db,
        user_id=user_id,
        statuses=statuses_to_fetch,
        # We can add limit/offset parameters here if needed by the API endpoint later
    )
    # Explicitly cast to ensure type safety
    return list(jobs)
