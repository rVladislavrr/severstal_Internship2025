from fastapi import HTTPException, status
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class BaseManager:
    model: Any

    async def create(self, session: AsyncSession, data: dict):
        try:
            instance = self.model(**data)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
        except Exception as e:
            await session.rollback()
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        await session.commit()
        return instance
