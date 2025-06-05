from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_entity.models import Base
from infra_repository.db import DatabaseHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria tabelas (se necessário) usando a engine diretamente
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Encerra o pool de conexões ao final
    await engine.dispose()
