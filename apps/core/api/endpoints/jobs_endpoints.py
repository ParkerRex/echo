from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from apps.core.api.schemas.video_processing_schemas import (
    VideoJobWithDetailsResponseSchema,
)
from apps.core.lib.auth.supabase_auth import AuthenticatedUser, get_current_user
from apps.core.lib.database.connection import get_async_db_session, get_db_session
from apps.core.models.enums import ProcessingStatus
from apps.core.services.job_service import get_user_jobs_by_statuses

# Placeholder for the service function we will create in Task 3.X.2
# from apps.core.services.job_service import get_user_jobs_by_statuses

router = APIRouter()


@router.get(
    "/",
    response_model=List[VideoJobWithDetailsResponseSchema],
    summary="Get User's Processing Jobs",
    description="Retrieve a list of video processing jobs for the authenticated user, filtered by status.",
)
async def get_my_processing_jobs(
    *,  # Enforces keyword-only arguments for clarity
    db: AsyncSession = Depends(get_async_db_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    status: Optional[List[ProcessingStatus]] = Query(
        default=None,  # Default to None, meaning all non-terminal if not specified by service
        description="Filter jobs by status (e.g., PENDING, PROCESSING). If not provided, by default PENDING and PROCESSING jobs are returned.",
        example=[ProcessingStatus.PENDING, ProcessingStatus.PROCESSING],
    ),
):
    """
    Retrieves video processing jobs for the current authenticated user.

    Allows filtering by one or more job statuses.
    If no statuses are provided, the service layer will return PENDING and PROCESSING jobs.
    The user_id passed to the service layer will be current_user.id (string UUID from Supabase).
    """
    # Call the service layer function.
    # Note: get_user_jobs_by_statuses is async, so we await it.
    # The underlying repository call is synchronous for now.
    jobs = await get_user_jobs_by_statuses(
        db=db,
        user_id=current_user.id,  # Pass the string ID from AuthenticatedUser
        statuses=status,
    )
    return jobs


# Future job-related endpoints will be added here
