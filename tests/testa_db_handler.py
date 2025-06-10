import pytest
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from infra_repository.db import DatabaseHandler
from settings import Settings


# Define nova declarative Base a ser criada no BD teste.
class TestBase(AsyncAttrs, DeclarativeBase):
    pass


# Define novo modelo ORM a ser tratado no banco teste
class TesteUser(TestBase):
    __tablename__ = 'teste_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(unique=True)
    fullname: Mapped[str]
    password: Mapped[str]


class TesteSettings(Settings):
    DB_URL: str = 'sqlite+aiosqlite:///:memory:'


@pytest.fixture
def get_settings():
    return TesteSettings()


@pytest.fixture
async def teste_db(get_settings):
    db_handler = DatabaseHandler(settings=get_settings, base=TestBase)
    yield db_handler
    await db_handler.engine.dispose()


@pytest.fixture
async def setup_tables(teste_db):
    async with teste_db.engine.begin() as conn:
        await teste_db.create_tables()
    yield
    async with teste_db.engine.begin() as conn:
        await conn.run_sync(teste_db.base.metadata.drop_all)


async def testa_get_db(teste_db):
    async for session in teste_db.get_db():
        assert isinstance(session, AsyncSession)


async def testa_create_tables(teste_db, setup_tables):
    async with teste_db.engine.begin() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: sync_conn.engine.dialect.get_table_names(
                sync_conn
            )
        )
        assert 'teste_user' in tables


def testa_settings(get_settings):
    assert isinstance(get_settings.DB_URL, str)


def testa_settings_subclass(get_settings):
    assert issubclass(TesteSettings, Settings)


async def testa_invalid_db_url(get_settings):
    assert isinstance(get_settings.DB_URL, str)


async def testa_get_db_session(teste_db):
    async for session in teste_db.get_db_session():
        assert isinstance(session, AsyncSession)
