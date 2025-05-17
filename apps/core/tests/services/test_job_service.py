"""
Unit tests for the JobService.
"""

from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session  # For type hinting the db session mock

from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel  # For return type hint
from apps.core.services.job_service import get_user_jobs_by_statuses

# Assuming VideoJobRepository is imported by job_service, we patch it there.


@pytest.mark.asyncio  # Mark test as async as the service function is async
async def test_get_user_jobs_by_statuses_with_specific_statuses():
    """Test service passes specific statuses to the repository."""
    mock_db_session = MagicMock(spec=Session)
    user_id = "test_user"
    specific_statuses = [ProcessingStatus.COMPLETED]
    expected_jobs = [MagicMock(spec=VideoJobModel)]

    with patch(
        "apps.core.services.job_service.VideoJobRepository.get_by_user_id_and_statuses",
        return_value=expected_jobs,
    ) as mock_repo_call:
        result_jobs = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=specific_statuses
        )

        mock_repo_call.assert_called_once_with(
            db=mock_db_session, user_id=user_id, statuses=specific_statuses
        )
        assert result_jobs == expected_jobs


@pytest.mark.asyncio
async def test_get_user_jobs_by_statuses_with_no_statuses_defaults_correctly():
    """Test service defaults to PENDING and PROCESSING when no statuses are provided."""
    mock_db_session = MagicMock(spec=Session)
    user_id = "test_user_default"
    default_statuses = [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]
    expected_jobs = [MagicMock(spec=VideoJobModel), MagicMock(spec=VideoJobModel)]

    with patch(
        "apps.core.services.job_service.VideoJobRepository.get_by_user_id_and_statuses",
        return_value=expected_jobs,
    ) as mock_repo_call:
        # Test with statuses=None
        result_jobs_none = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=None
        )
        mock_repo_call.assert_called_with(
            db=mock_db_session,
            user_id=user_id,
            statuses=default_statuses,  # Check if default is passed
        )
        assert result_jobs_none == expected_jobs

        # Reset mock for next call
        mock_repo_call.reset_mock()

        # Test with statuses=[] (empty list)
        result_jobs_empty = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=[]
        )
        mock_repo_call.assert_called_with(
            db=mock_db_session,
            user_id=user_id,
            statuses=default_statuses,  # Check if default is passed for empty list too
        )
        assert result_jobs_empty == expected_jobs


@pytest.mark.asyncio
async def test_get_user_jobs_by_statuses_returns_repository_result():
    """Test that the service function returns whatever the repository provides."""
    mock_db_session = MagicMock(spec=Session)
    user_id = "test_user_return"
    mock_jobs_from_repo = [
        VideoJobModel(id=1, video_id=1, status=ProcessingStatus.PENDING),
        VideoJobModel(id=2, video_id=2, status=ProcessingStatus.PROCESSING),
    ]

    with patch(
        "apps.core.services.job_service.VideoJobRepository.get_by_user_id_and_statuses",
        return_value=mock_jobs_from_repo,
    ) as mock_repo_call:
        result_jobs = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=[ProcessingStatus.PENDING]
        )
        assert result_jobs == mock_jobs_from_repo
