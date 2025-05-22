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
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def create_engine(self, settings: Settings) -> None:
        self.engine = create_async_engine(settings.DB_URL, echo=True)

    def create_session_factory(self) -> None:
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        if self.session_factory is None:
            self.create_session_factory()

        async with self.session_factory() as session:
            yield session


settings = Settings()   # Objeto que retorna os valores de .env

if settings.DB_URL is None:
    raise RuntimeError('A variável DATABASE_URL não foi definida')
