"""
Unit tests for the JobService.
"""

from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.services.job_service import get_user_jobs_by_statuses


@pytest.mark.asyncio
async def test_get_user_jobs_by_statuses_with_specific_statuses():
    """Test service passes specific statuses to the repository."""
    mock_db_session = AsyncMock(spec=AsyncSession)
    user_id = "test_user"
    specific_statuses = [ProcessingStatus.COMPLETED]
    expected_jobs_data = [
        VideoJobModel(id=1, video_id=101, status=ProcessingStatus.COMPLETED)
    ]

    with patch(
        "apps.core.services.job_service.VideoJobRepository.get_by_user_id_and_statuses",
        new_callable=AsyncMock,
    ) as mock_repo_call:
        mock_repo_call.return_value = expected_jobs_data

        result_jobs = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=specific_statuses
        )

        mock_repo_call.assert_awaited_once_with(
            db=mock_db_session, user_id=user_id, statuses=specific_statuses
        )
        assert result_jobs == expected_jobs_data


@pytest.mark.asyncio
async def test_get_user_jobs_by_statuses_with_no_statuses_defaults_correctly():
    """Test service defaults to PENDING and PROCESSING when no statuses are provided."""
    mock_db_session = AsyncMock(spec=AsyncSession)
    user_id = "test_user_default"
    default_statuses = [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]
    expected_jobs_data = [
        VideoJobModel(id=2, video_id=102, status=ProcessingStatus.PENDING),
        VideoJobModel(id=3, video_id=103, status=ProcessingStatus.PROCESSING),
    ]

    with patch(
        "apps.core.services.job_service.VideoJobRepository.get_by_user_id_and_statuses",
        new_callable=AsyncMock,
    ) as mock_repo_call:
        mock_repo_call.return_value = expected_jobs_data

        # Test with statuses=None
        result_jobs_none = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=None
        )
        mock_repo_call.assert_awaited_with(
            db=mock_db_session,
            user_id=user_id,
            statuses=default_statuses,
        )
        assert result_jobs_none == expected_jobs_data

        # Test with statuses=[] (empty list)
        result_jobs_empty = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=[]
        )
        mock_repo_call.assert_awaited_with(
            db=mock_db_session,
            user_id=user_id,
            statuses=default_statuses,
        )
        assert result_jobs_empty == expected_jobs_data

        # To be very precise about both calls:
        assert mock_repo_call.await_count == 2
        call_args_list = mock_repo_call.await_args_list
        assert call_args_list[0].kwargs["statuses"] == default_statuses
        assert call_args_list[1].kwargs["statuses"] == default_statuses


@pytest.mark.asyncio
async def test_get_user_jobs_by_statuses_returns_repository_result():
    """Test that the service function returns whatever the repository provides."""
    mock_db_session = AsyncMock(spec=AsyncSession)
    user_id = "test_user_return"
    mock_jobs_from_repo = [
        VideoJobModel(id=1, video_id=1, status=ProcessingStatus.PENDING),
        VideoJobModel(id=2, video_id=2, status=ProcessingStatus.PROCESSING),
    ]

    with patch(
        "apps.core.services.job_service.VideoJobRepository.get_by_user_id_and_statuses",
        new_callable=AsyncMock,
    ) as mock_repo_call:
        mock_repo_call.return_value = mock_jobs_from_repo

        result_jobs = await get_user_jobs_by_statuses(
            db=mock_db_session, user_id=user_id, statuses=[ProcessingStatus.PENDING]
        )
        mock_repo_call.assert_awaited_once_with(
            db=mock_db_session, user_id=user_id, statuses=[ProcessingStatus.PENDING]
        )
        assert result_jobs == mock_jobs_from_repo
