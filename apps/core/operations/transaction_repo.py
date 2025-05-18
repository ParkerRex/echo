from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_in_transaction(
        self, callback: Callable[[AsyncSession], Awaitable[Any]]
    ) -> Any:
        """
        Execute an async function within a database transaction.

        Args:
            callback: An async function that takes the async session as parameter and returns a result

        Returns:
            The result of the callback function
        """
        try:
            result = await callback(self.db)
            await self.db.commit()
            return result
        except Exception as e:
            await self.db.rollback()
            raise e
