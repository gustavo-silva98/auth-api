from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from domain_entity.models import Base
from settings import Settings


# Interface de handler de banco de dados.
class DatabaseHandler:
    def __init__(self, settings: Settings, base: type[DeclarativeBase] = Base):
        self.base = base
        self.engine: AsyncEngine = create_async_engine(
            settings.DB_URL, echo=True
        )
        self.session_factory: async_sessionmaker[
            AsyncSession
        ] = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async for session in self.get_db():
            yield session
