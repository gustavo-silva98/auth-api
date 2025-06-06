from infra_repository.db import db_handler

from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator


async def get_session() -> AsyncGenerator[AsyncSession,None]:
    async for session in db_handler.get_db():
        yield session