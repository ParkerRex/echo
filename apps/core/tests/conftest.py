import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from core.lib.database.connection import Base, get_async_db_session

# Assuming your FastAPI app instance is in 'main.py' at the root of 'apps/core'
# Adjust the import path if your main app instance is located elsewhere.
from main import app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

# Use a separate in-memory SQLite database for tests
# Using a file-based SQLite for easier inspection if needed: ./test.db
# For true in-memory, use "sqlite+aiosqlite:///:memory:"
# However, :memory: dbs are distinct per connection, which can be tricky with SQLAlchemy engines/sessions.
# A file-based one ensures all connections in a test session hit the same DB.
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_db_file.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine_fixture():  # Renamed to avoid conflict if a var is named async_engine
    """Create an async engine for the test database for the entire session."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        # Drop all tables first to ensure a clean state for each test session
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
    # Consider removing the test_db_file.db if created
    # import os
    # if os.path.exists("./test_db_file.db"):
    #     os.remove("./test_db_file.db")


@pytest_asyncio.fixture(scope="function")
async def db_session_fixture(
    async_engine_fixture,
) -> AsyncGenerator[AsyncSession, None]:  # Renamed
    """Yield an AsyncSession for each test function, ensuring transaction rollback."""
    # sessionmaker for test sessions
    AsyncTestSessionLocal = sessionmaker(
        bind=async_engine_fixture,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with AsyncTestSessionLocal() as session:
        # Begin a transaction
        await session.begin()
        try:
            yield session
        finally:
            # Rollback the transaction to ensure test isolation
            await session.rollback()
            await session.close()


@pytest.fixture(scope="function")  # Changed to function scope
def test_client_fixture(
    db_session_fixture: AsyncSession,
) -> Generator[TestClient, None, None]:  # Renamed
    """
    Create a TestClient for API tests for each function.
    Overrides the get_async_db_session dependency with the test session.
    """

    async def override_get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session_fixture

    app.dependency_overrides[get_async_db_session] = override_get_async_db_session
    with TestClient(app) as client:
        yield client
    # Clean up the override after the test
    del app.dependency_overrides[get_async_db_session]
