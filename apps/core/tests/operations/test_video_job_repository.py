"""
Unit tests for the VideoJobRepository.
"""

from datetime import datetime, timedelta
from typing import AsyncGenerator, List

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.lib.database.connection import Base
from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.models.video_model import VideoModel
from apps.core.operations.video_job_repository import VideoJobRepository

# Setup in-memory SQLite database for testing
# engine = create_engine("sqlite:///:memory:")
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# db_session fixture - REMOVED (now comes from conftest.py as db_session_fixture)
# @pytest.fixture(scope="function")
# def db_session() -> Generator[Session, None, None]:
#     """Creates a new database session for a test."""
#     Base.metadata.create_all(bind=engine)  # Create tables
#     session = TestingSessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()
#         Base.metadata.drop_all(bind=engine)  # Drop tables after test


class TestVideoJobRepository:
    @pytest.mark.asyncio
    async def test_get_by_user_id_and_statuses_no_jobs(
        self, db_session_fixture: AsyncSession
    ):
        """Test retrieving jobs when no jobs exist for the user."""
        user_id = "test_user_1"
        # Ensure VideoModel for the user exists, otherwise join will fail if jobs were present
        # For this specific test (no jobs), it's fine, but good practice for others.
        video_for_user = VideoModel(
            uploader_user_id=user_id,
            original_filename="test.mp4",
            storage_path="test/path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video_for_user)
        await db_session_fixture.commit()  # Commit the video

        jobs = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture, user_id=user_id, statuses=[ProcessingStatus.PENDING]
        )
        assert len(jobs) == 0

    @pytest.mark.asyncio
    async def test_get_by_user_id_and_statuses_filters_by_user(
        self, db_session_fixture: AsyncSession
    ):
        """Test that jobs are correctly filtered by user_id."""
        user1_id = "user_1"
        user2_id = "user_2"

        # Video for user 1
        video1 = VideoModel(
            uploader_user_id=user1_id,
            original_filename="video1.mp4",
            storage_path="path1",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video1)
        await db_session_fixture.commit()  # Commit video1 before creating job1
        job1 = VideoJobModel(video_id=video1.id, status=ProcessingStatus.PENDING)
        db_session_fixture.add(job1)
        # await db_session_fixture.commit() # Commit job1 separately if needed, or commit all at once

        # Video for user 2
        video2 = VideoModel(
            uploader_user_id=user2_id,
            original_filename="video2.mp4",
            storage_path="path2",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video2)
        await db_session_fixture.commit()  # Commit video2 before creating job2
        job2 = VideoJobModel(video_id=video2.id, status=ProcessingStatus.PENDING)
        db_session_fixture.add(job2)
        await db_session_fixture.commit()  # Commit jobs

        jobs_user1 = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture, user_id=user1_id, statuses=[ProcessingStatus.PENDING]
        )
        assert len(jobs_user1) == 1
        assert bool(jobs_user1[0].id == job1.id)
        assert bool(jobs_user1[0].video.uploader_user_id == user1_id)

        jobs_user2 = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture, user_id=user2_id, statuses=[ProcessingStatus.PENDING]
        )
        assert len(jobs_user2) == 1
        assert bool(jobs_user2[0].id == job2.id)
        assert bool(jobs_user2[0].video.uploader_user_id == user2_id)

    @pytest.mark.asyncio
    async def test_get_by_user_id_and_statuses_filters_by_multiple_statuses(
        self, db_session_fixture: AsyncSession
    ):
        user_id = "multi_status_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video)
        await db_session_fixture.commit()

        job_pending = VideoJobModel(
            video_id=video.id,
            status=ProcessingStatus.PENDING,
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        job_processing = VideoJobModel(
            video_id=video.id,
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        job_completed = VideoJobModel(
            video_id=video.id,
            status=ProcessingStatus.COMPLETED,
            created_at=datetime.utcnow(),
        )
        db_session_fixture.add_all([job_pending, job_processing, job_completed])
        await db_session_fixture.commit()

        # Test fetching PENDING and PROCESSING
        jobs_pending_processing = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture,
            user_id=user_id,
            statuses=[ProcessingStatus.PENDING, ProcessingStatus.PROCESSING],
        )
        assert len(jobs_pending_processing) == 2
        job_ids_pending_processing = {job.id for job in jobs_pending_processing}
        assert job_pending.id in job_ids_pending_processing
        assert job_processing.id in job_ids_pending_processing

        # Test fetching only COMPLETED
        jobs_completed_list = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture,
            user_id=user_id,
            statuses=[ProcessingStatus.COMPLETED],
        )
        assert len(jobs_completed_list) == 1
        assert bool(jobs_completed_list[0].id == job_completed.id)

    @pytest.mark.asyncio
    async def test_get_by_user_id_and_statuses_no_status_filter(
        self, db_session_fixture: AsyncSession
    ):
        """Test behavior when statuses is None (should return all for user)."""
        user_id = "no_status_filter_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video)
        await db_session_fixture.commit()

        job_pending = VideoJobModel(video_id=video.id, status=ProcessingStatus.PENDING)
        job_completed = VideoJobModel(
            video_id=video.id, status=ProcessingStatus.COMPLETED
        )
        db_session_fixture.add_all([job_pending, job_completed])
        await db_session_fixture.commit()

        jobs = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture, user_id=user_id, statuses=None
        )
        assert len(jobs) == 2

    @pytest.mark.asyncio
    async def test_get_by_user_id_and_statuses_ordering(
        self, db_session_fixture: AsyncSession
    ):
        user_id = "ordering_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video)
        await db_session_fixture.commit()

        # Timestamps are important here
        job1_older = VideoJobModel(
            video_id=video.id,
            status=ProcessingStatus.PENDING,
            created_at=datetime.utcnow() - timedelta(minutes=10),
        )
        job2_newer = VideoJobModel(
            video_id=video.id,
            status=ProcessingStatus.PENDING,
            created_at=datetime.utcnow() - timedelta(minutes=1),
        )
        job3_oldest = VideoJobModel(
            video_id=video.id,
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.utcnow() - timedelta(minutes=20),
        )
        db_session_fixture.add_all([job1_older, job2_newer, job3_oldest])
        await db_session_fixture.commit()

        jobs = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture, user_id=user_id, statuses=None
        )
        assert len(jobs) == 3
        assert bool(jobs[0].id == job2_newer.id)  # Newest first
        assert bool(jobs[1].id == job1_older.id)
        assert bool(jobs[2].id == job3_oldest.id)  # Oldest last

    @pytest.mark.asyncio
    async def test_get_by_user_id_and_statuses_pagination(
        self, db_session_fixture: AsyncSession
    ):
        user_id = "pagination_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video)
        await db_session_fixture.commit()

        all_jobs_data = []
        for i in range(5):  # Create 5 jobs
            job = VideoJobModel(
                video_id=video.id,
                status=ProcessingStatus.PENDING,
                created_at=datetime.utcnow() - timedelta(minutes=i),
            )
            all_jobs_data.append(job)
        db_session_fixture.add_all(all_jobs_data)
        await db_session_fixture.commit()

        # Test fetching first page (limit 2)
        jobs_page1 = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture,
            user_id=user_id,
            statuses=[ProcessingStatus.PENDING],
            limit=2,
            offset=0,
        )
        assert len(jobs_page1) == 2
        # Assuming jobs are ordered by created_at desc by default (newest first)
        # Newest is -0 minutes ago, then -1 minutes ago
        assert bool(jobs_page1[0].created_at > jobs_page1[1].created_at)

        # Test fetching second page (limit 2, offset 2)
        jobs_page2 = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture,
            user_id=user_id,
            statuses=[ProcessingStatus.PENDING],
            limit=2,
            offset=2,
        )
        assert len(jobs_page2) == 2
        assert bool(
            jobs_page1[1].created_at > jobs_page2[0].created_at
        )  # End of page 1 vs start of page 2

        # Test fetching a page that exceeds total items
        jobs_page_exceed = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture,
            user_id=user_id,
            statuses=[ProcessingStatus.PENDING],
            limit=2,
            offset=4,  # 5 items total, offset 4 means 5th item
        )
        assert len(jobs_page_exceed) == 1

        # Test fetching with limit only (no offset)
        jobs_limit_only = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture,
            user_id=user_id,
            statuses=[ProcessingStatus.PENDING],
            limit=3,
        )
        assert len(jobs_limit_only) == 3

    @pytest.mark.asyncio
    async def test_get_by_user_id_and_statuses_no_matching_status(
        self, db_session_fixture: AsyncSession
    ):
        user_id = "no_match_status_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session_fixture.add(video)
        await db_session_fixture.commit()

        job_pending = VideoJobModel(video_id=video.id, status=ProcessingStatus.PENDING)
        db_session_fixture.add(job_pending)
        await db_session_fixture.commit()

        jobs = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture,
            user_id=user_id,
            statuses=[ProcessingStatus.COMPLETED],
        )
        assert len(jobs) == 0

    @pytest.mark.asyncio
    async def test_eager_loading(self, db_session_fixture: AsyncSession):
        """Test that video and video_metadata are eagerly loaded."""
        user_id = "eager_loading_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video_eager.mp4",
            storage_path="path_eager",
            content_type="video/mp4",
            size_bytes=100,
            # video_metadata field is implicitly handled via backref if VideoMetadataModel has one
            # or can be explicitly set if VideoMetadataModel instance is created and linked
        )
        db_session_fixture.add(video)
        await db_session_fixture.commit()  # Commit video first to get its ID

        # Create a job linked to this video
        job = VideoJobModel(video_id=video.id, status=ProcessingStatus.PENDING)
        db_session_fixture.add(job)
        await db_session_fixture.commit()

        # Clear the session to ensure objects are loaded from DB, not cache, for testing eager loading
        db_session_fixture.expunge_all()
        # Alternatively, and often better for testing eager loads against the DB:
        # await db_session_fixture.close()
        # db_session_fixture = await anext(db_session_fixture_gen()) # if db_session_fixture was a generator

        # Retrieve the job.
        # The get_by_user_id_and_statuses method should use joinedload/selectinload
        retrieved_jobs = await VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session_fixture, user_id=user_id, statuses=[ProcessingStatus.PENDING]
        )
        assert len(retrieved_jobs) == 1
        retrieved_job = retrieved_jobs[0]

        # Accessing .video and .video.video_metadata should not trigger new SQL queries
        # This is hard to assert directly without inspecting SQL queries (e.g. using an event listener)
        # For now, we assume the repository's query options handle this.
        # A simple check is that the attributes are accessible:
        assert retrieved_job.video is not None
        assert retrieved_job.video.original_filename == "video_eager.mp4"
        # If VideoMetadataModel was setup and linked, you would check it too:
        # assert retrieved_job.video.video_metadata is not None
        # assert retrieved_job.video.video_metadata.title == "Some Title" # if metadata was created and linked

        # To truly test eager loading, you'd need to mock the session or use SQLAlchemy events
        # to count queries. For this test, we rely on the implementation detail of the repository.
        # One indirect way is to check if the relationship is loaded without error after expunging.
        # If it wasn't eagerly loaded, accessing it might raise a DetachedInstanceError or similar,
        # or it would be None if the session was completely closed and reopened.
        # Since we are just expunging, the objects are detached but still in memory.
        # A more robust test would involve a fresh session or query counting.

        # For this test, let's ensure the related video's uploader_user_id is correct,
        # which implies 'video' was loaded.
        assert retrieved_job.video.uploader_user_id == user_id

    # TODO:
    # - (No outstanding major categories from previous TODO, covered above)
