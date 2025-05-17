"""
Unit tests for the VideoJobRepository.
"""

from datetime import datetime, timedelta
from typing import Generator, List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.core.lib.database.connection import Base
from apps.core.models.enums import ProcessingStatus
from apps.core.models.video_job_model import VideoJobModel
from apps.core.models.video_model import VideoModel
from apps.core.operations.video_job_repository import VideoJobRepository

# Setup in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Creates a new database session for a test."""
    Base.metadata.create_all(bind=engine)  # Create tables
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)  # Drop tables after test


class TestVideoJobRepository:
    def test_get_by_user_id_and_statuses_no_jobs(self, db_session: Session):
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
        db_session.add(video_for_user)
        db_session.commit()  # Commit the video so a job *could* be linked to it

        jobs = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=[ProcessingStatus.PENDING]
        )
        assert len(jobs) == 0

    def test_get_by_user_id_and_statuses_filters_by_user(self, db_session: Session):
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
        db_session.add(video1)
        db_session.commit()  # Commit video1 before creating job1
        job1 = VideoJobModel(video_id=video1.id, status=ProcessingStatus.PENDING)
        db_session.add(job1)
        # db_session.commit()  # Commit job1

        # Video for user 2
        video2 = VideoModel(
            uploader_user_id=user2_id,
            original_filename="video2.mp4",
            storage_path="path2",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session.add(video2)
        db_session.commit()  # Commit video2 before creating job2
        job2 = VideoJobModel(video_id=video2.id, status=ProcessingStatus.PENDING)
        db_session.add(job2)
        db_session.commit()  # Commit jobs

        jobs_user1 = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user1_id, statuses=[ProcessingStatus.PENDING]
        )
        assert len(jobs_user1) == 1
        assert jobs_user1[0].id == job1.id
        assert (
            jobs_user1[0].video.uploader_user_id == user1_id
        )  # Linter might still flag this

        jobs_user2 = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user2_id, statuses=[ProcessingStatus.PENDING]
        )
        assert len(jobs_user2) == 1
        assert jobs_user2[0].id == job2.id
        assert (
            jobs_user2[0].video.uploader_user_id == user2_id
        )  # Linter might still flag this

    def test_get_by_user_id_and_statuses_filters_by_multiple_statuses(
        self, db_session: Session
    ):
        user_id = "multi_status_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session.add(video)
        db_session.commit()

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
        db_session.add_all([job_pending, job_processing, job_completed])
        db_session.commit()

        # Test fetching PENDING and PROCESSING
        jobs_pending_processing = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session,
            user_id=user_id,
            statuses=[ProcessingStatus.PENDING, ProcessingStatus.PROCESSING],
        )
        assert len(jobs_pending_processing) == 2
        job_ids_pending_processing = {job.id for job in jobs_pending_processing}
        assert job_pending.id in job_ids_pending_processing
        assert job_processing.id in job_ids_pending_processing

        # Test fetching only COMPLETED
        jobs_completed = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=[ProcessingStatus.COMPLETED]
        )
        assert len(jobs_completed) == 1
        assert jobs_completed[0].id == job_completed.id

    def test_get_by_user_id_and_statuses_no_status_filter(self, db_session: Session):
        """Test behavior when statuses is None (should return all for user)."""
        user_id = "no_status_filter_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session.add(video)
        db_session.commit()

        job_pending = VideoJobModel(video_id=video.id, status=ProcessingStatus.PENDING)
        job_completed = VideoJobModel(
            video_id=video.id, status=ProcessingStatus.COMPLETED
        )
        db_session.add_all([job_pending, job_completed])
        db_session.commit()

        jobs = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=None
        )
        assert len(jobs) == 2  # Repository itself doesn't apply default filters

    def test_get_by_user_id_and_statuses_ordering(self, db_session: Session):
        user_id = "ordering_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session.add(video)
        db_session.commit()

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
        db_session.add_all([job1_older, job2_newer, job3_oldest])
        db_session.commit()

        jobs = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=None
        )
        assert len(jobs) == 3
        assert jobs[0].id == job2_newer.id  # Newest first
        assert jobs[1].id == job1_older.id
        assert jobs[2].id == job3_oldest.id  # Oldest last

    def test_get_by_user_id_and_statuses_pagination(self, db_session: Session):
        user_id = "pagination_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session.add(video)
        db_session.commit()

        for i in range(5):
            db_session.add(
                VideoJobModel(
                    video_id=video.id,
                    status=ProcessingStatus.PENDING,
                    created_at=datetime.utcnow() - timedelta(minutes=i),
                )
            )
        db_session.commit()

        # Get first page (limit 2)
        jobs_page1 = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=None, limit=2, offset=0
        )
        assert len(jobs_page1) == 2

        # Get second page (limit 2, offset 2)
        jobs_page2 = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=None, limit=2, offset=2
        )
        assert len(jobs_page2) == 2

        # Get third page (should have 1 remaining)
        jobs_page3 = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=None, limit=2, offset=4
        )
        assert len(jobs_page3) == 1

        # Ensure correct ordering is maintained with pagination by checking IDs if possible (requires knowing the order)
        all_jobs_ordered = sorted(
            db_session.query(VideoJobModel)
            .join(VideoModel)
            .filter(VideoModel.uploader_user_id == user_id)
            .all(),
            key=lambda j: j.created_at,
            reverse=True,
        )
        assert jobs_page1[0].id == all_jobs_ordered[0].id
        assert jobs_page1[1].id == all_jobs_ordered[1].id
        assert jobs_page2[0].id == all_jobs_ordered[2].id
        assert jobs_page2[1].id == all_jobs_ordered[3].id
        assert jobs_page3[0].id == all_jobs_ordered[4].id

    def test_get_by_user_id_and_statuses_no_matching_status(self, db_session: Session):
        user_id = "no_match_status_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session.add(video)
        db_session.commit()

        job_pending = VideoJobModel(video_id=video.id, status=ProcessingStatus.PENDING)
        db_session.add(job_pending)
        db_session.commit()

        jobs = VideoJobRepository.get_by_user_id_and_statuses(
            db=db_session, user_id=user_id, statuses=[ProcessingStatus.COMPLETED]
        )
        assert len(jobs) == 0

    def test_eager_loading(self, db_session: Session):
        """Check if video and video_metadata are eager loaded."""
        user_id = "eager_loading_user"
        video = VideoModel(
            uploader_user_id=user_id,
            original_filename="video.mp4",
            storage_path="path",
            content_type="video/mp4",
            size_bytes=100,
        )
        db_session.add(video)
        db_session.commit()
        from apps.core.models.video_metadata_model import (
            VideoMetadataModel,  # Import here to avoid circularity if any
        )

        job = VideoJobModel(video_id=video.id, status=ProcessingStatus.PENDING)
        db_session.add(job)
        db_session.commit()  # Commit job so it has an ID
        metadata = VideoMetadataModel(
            job_id=job.id, title="Test Title"
        )  # Create metadata linked to the job
        db_session.add(metadata)
        db_session.commit()

        with (
            db_session.no_autoflush
        ):  # Turn off autoflush for this specific check if needed, or use a new session
            # Fetch the job again using the repository method
            retrieved_jobs = VideoJobRepository.get_by_user_id_and_statuses(
                db=db_session, user_id=user_id, statuses=[ProcessingStatus.PENDING]
            )
            assert len(retrieved_jobs) == 1
            retrieved_job = retrieved_jobs[0]

            # Access related objects. If not eager loaded, this would trigger new queries.
            # We can't directly assert no new queries without a more complex setup (mocking query execution count).
            # So, we rely on the .options(joinedload(...)) in the repo and check attributes are accessible.
            assert retrieved_job.video is not None
            assert retrieved_job.video.uploader_user_id == user_id
            assert retrieved_job.video_metadata is not None
            assert retrieved_job.video_metadata.title == "Test Title"

    # TODO:
    # - (No outstanding major categories from previous TODO, covered above)
