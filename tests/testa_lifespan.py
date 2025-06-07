from unittest.mock import AsyncMock, MagicMock, patch

from api_presentation.lifespan import lifespan
from domain_entity.models import Base


async def testa_lifespan():
    mock_engine = MagicMock()
    mock_begin = AsyncMock()
    mock_conn = MagicMock()

    # Configura o comportamento assíncrono
    mock_engine.begin = MagicMock(return_value=mock_begin)
    mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_begin.__aexit__ = AsyncMock(return_value=None)
    mock_conn.run_sync = AsyncMock()
    mock_engine.dispose = AsyncMock()

    # Aplica o mock ao db_handler.engine

    with patch('infra_repository.db.db_handler.engine', mock_engine):
        app = MagicMock()
        async with lifespan(app):
            # Verifica chamadas durante a entrada
            mock_engine.begin.assert_called_once()
            mock_conn.run_sync.assert_awaited_once_with(
                Base.metadata.create_all
            )

        mock_engine.dispose.assert_awaited_once()
