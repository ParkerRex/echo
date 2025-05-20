from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import lru_cache
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")

@lru_cache
def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
