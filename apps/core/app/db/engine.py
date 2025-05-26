import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Construct the path to the root .env file
# __file__ is engine.py, so ../../.. goes from app/db/engine.py to apps/core/ to apps/ to project root
root_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
env_files = [
    os.path.join(root_dir, ".env"),
    os.path.join(root_dir, ".env.development"),
    os.path.join(root_dir, ".env.production"),
]

# Load environment files in order of preference
for env_file in env_files:
    if os.path.exists(env_file):
        load_dotenv(
            dotenv_path=env_file, override=False
        )  # Don't override already set variables

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
