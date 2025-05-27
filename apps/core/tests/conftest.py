"""
Test configuration for Echo backend.

NOTE: This test configuration is currently disabled as we've migrated from SQLAlchemy
to Supabase as our single source of truth. The test suite needs to be updated to work
with the new Supabase-first architecture.

TODO: Rewrite test configuration to use Supabase test database instead of SQLAlchemy.
"""

import asyncio
from typing import Generator

import pytest
from starlette.testclient import TestClient

# Assuming your FastAPI app instance is in 'main.py' at the root of 'apps/core'
from main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_client_fixture() -> Generator[TestClient, None, None]:
    """
    Create a TestClient for API tests.

    NOTE: This is a simplified version that doesn't set up database fixtures.
    Tests that require database access will need to be updated to work with Supabase.
    """
    with TestClient(app) as client:
        yield client
