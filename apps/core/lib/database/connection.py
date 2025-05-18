from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from core.config import settings

# Create SQLAlchemy engine
# Add connect_args for SQLite compatibility
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


# Async SQLAlchemy engine
async_db_url = settings.DATABASE_URL
if settings.DATABASE_URL.startswith("postgresql://"):
    async_db_url = settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
elif settings.DATABASE_URL.startswith(
    "sqlite:///"
):  # Assuming 'sqlite:////path/to/db.sqlite'
    async_db_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
elif settings.DATABASE_URL.startswith(
    "sqlite://"
):  # Assuming relative path 'sqlite://./db.sqlite'
    async_db_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")


async_engine = create_async_engine(async_db_url)

# SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async SessionLocal class
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,  # Explicitly set for clarity, though default for AsyncSession
    autoflush=False,  # Explicitly set for clarity, though default for AsyncSession
)

# Base class for models
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function to get DB session
    Usage: db: Session = Depends(get_db_session)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get an async DB session.
    Usage: db: AsyncSession = Depends(get_async_db_session)
    """
    # The type checker might complain here, but this is the standard way
    # to create an async session with SQLAlchemy.
    async_session_local_instance = AsyncSessionLocal()

    async with async_session_local_instance as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            # Closing the session is handled by the async context manager
            pass


def create_session() -> Session:
    """Create and return a new session"""
    return SessionLocal()


# It's good practice to also have an async version if needed outside FastAPI Depends
async def create_async_session() -> AsyncSession:
    """Create and return a new async session"""
    # The type checker might complain here as well.
    return AsyncSessionLocal()
