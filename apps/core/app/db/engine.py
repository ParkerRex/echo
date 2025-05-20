import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Construct the path to the root .env file
# __file__ is engine.py, so ../../.. goes from app/db/engine.py to apps/core/ to apps/ to project root
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres"
)


@lru_cache
def get_engine():
    # Add connect_args for SQLite compatibility if you ever use SQLite for testing with this engine
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)


SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
