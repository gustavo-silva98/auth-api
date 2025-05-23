from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings import Settings


# Interface de handler de banco de dados.
class DatabaseHandler:
    def __init__(self, settings: Settings):
        self.engine: AsyncEngine = create_async_engine(
            settings.DB_URL, echo=True
        )
        self.session_factory: async_sessionmaker[
            AsyncSession
        ] = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session
