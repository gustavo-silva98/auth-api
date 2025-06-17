from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_entity.models import Base
from infra_repository.db import db_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria tabelas (se necessário) usando a engine diretamente

    # 2) veja qual DB está usando (debug)
    print('↪ DATABASE URL:', db_handler.engine.url)
    async with db_handler.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Encerra o pool de conexões ao final
    await db_handler.engine.dispose()
