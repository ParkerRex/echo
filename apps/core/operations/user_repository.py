from typing import List, Optional

from fastapi import Depends
from sqlalchemy import delete, select, update  # Added select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession  # Added AsyncSession

# from lib.database import create_session # Will be replaced by async version
from sqlalchemy.orm import Session

from apps.core.lib.database.connection import (
    get_async_db_session,  # Import async session getter
)
from apps.core.models.user_model import User


class UserRepository:
    def __init__(self, db: AsyncSession):  # Changed to AsyncSession
        self.db = db

    async def get_user(self, user_id: int) -> Optional[User]:  # async def
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:  # async def
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:  # async def
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[User]:  # async def
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create_user(self, user_data: dict) -> User:  # async def
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()  # await commit
        await self.db.refresh(user)  # await refresh
        return user

    async def update_user(
        self, user_id: int, user_data: dict
    ) -> Optional[User]:  # async def
        # We need to be careful here. self.get_user is now async.
        # SQLAlchemy 2.0 style update is preferred for partial updates.
        # However, to maintain similar logic of fetch then update for now:
        user = await self.get_user(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            await self.db.commit()  # await commit
            await self.db.refresh(user)  # await refresh
        return user
        # Alternative using SQLAlchemy update:
        # stmt = update(User).where(User.id == user_id).values(**user_data)
        # result = await self.db.execute(stmt)
        # if result.rowcount == 0:
        #     return None
        # await self.db.commit()
        # return await self.get_user(user_id) # Re-fetch to get updated model

    async def delete_user(self, user_id: int) -> bool:  # async def
        # SQLAlchemy 2.0 style delete is preferred.
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()  # await commit
        return result.rowcount > 0
        # Old logic:
        # user = await self.get_user(user_id)
        # if user:
        #     await self.db.delete(user) # await delete
        #     await self.db.commit()
        #     return True
        # return False


async def get_user_repository(  # async def
    db: AsyncSession = Depends(get_async_db_session),  # Use get_async_db_session
) -> UserRepository:
    return UserRepository(db)
