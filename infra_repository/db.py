from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from settings import Settings

settings = Settings()   # Objeto que retorna os valores de .env

if settings.DB_URL is None:
    raise RuntimeError('A variável DATABASE_URL não foi definida')

# Criação (ASYNC) de engine e sessionmaker
engine = create_async_engine(settings.DB_URL, echo=True)
async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with async_session_factory() as session:
        yield session
