import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_entity.models import Base
from infra_repository.db import db_handler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria tabelas (se necessário) usando a engine diretamente

    logger.info('Iniciando aplicação', extra={'event': 'startup'})

    async with db_handler.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Encerra o pool de conexões ao final
    await db_handler.engine.dispose()
    logger.info('Finalizando aplicação', extra={'event': 'shutdown'})
