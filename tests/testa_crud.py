from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from domain_entity.models import User
from infra_repository.crud import UserCRUD

"""
Métodos de teste para a classe UserCRUD.
MÉTODOS USER CRUD:
- insert_user - OK
- delete_user_by_email - OK
- get_user_by_email - OK
- delete_all_users - // TODO


"""


@pytest.fixture
def user_model():
    return User(
        username='test_user',
        email='teste@email.com',
        fullname='Test User',
        password='hashed_password',
    )


async def testa_crud_insert_user_valido(user_model):
    mock_db = AsyncMock(spec=AsyncSession)
    user_teste = user_model

    user_crud = UserCRUD()
    await user_crud.insert_user(user=user_teste, async_transaction=mock_db)

    user_teste.id = 1  # Simulando que o ID foi atribuído após a inserção
    mock_db.add.assert_called_once_with(user_teste)
    assert (
        await user_crud.insert_user(user=user_teste, async_transaction=mock_db)
        == user_teste
    )


async def testa_crud_insert_user_invalido(user_model):
    mock_db = AsyncMock(spec=AsyncSession)
    user_teste = user_model
    user_crud = UserCRUD()

    mock_db.add.side_effect = SQLAlchemyError('Erro ao inserir usuário')
    with pytest.raises(SQLAlchemyError):
        await user_crud.insert_user(user=user_teste, async_transaction=mock_db)


async def testa_crud_delete_user_by_email_valid():
    mock_db = AsyncMock(spec=AsyncSession)
    user_crud = UserCRUD()
    mock_db.execute.return_value.rowcount = 1

    result = await user_crud.delete_user_by_email(
        'email@teste.com', async_transaction=mock_db
    )
    assert result == 1
    mock_db.execute.assert_called_once()


async def testa_crud_delete_user_by_email_invalid():
    mock_db = AsyncMock(spec=AsyncSession)
    user_crud = UserCRUD()
    mock_db.execute.return_value.rowcount = 0

    result = await user_crud.delete_user_by_email(
        'email@teste.com', async_transaction=mock_db
    )
    assert result == 0
    mock_db.execute.assert_called_once()


async def testa_crud_get_user_by_email_valido():
    mock_db = AsyncMock(spec=AsyncSession)
    user_crud = UserCRUD()

    mock_user = User(
        id=1,
        username='test_user',
        email='teste@email.com',
        fullname='Test User',
        password='hashed_password',
    )

    user_crud.get_user_by_email = AsyncMock(return_value=mock_user)
    result = await user_crud.get_user_by_email(
        email='teste@email.com', async_transaction=mock_db
    )

    assert result == mock_user


async def testa_crud_get_user_by_email_invalido():
    mock_db = AsyncMock(spec=AsyncSession)
    user_crud = UserCRUD()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db.execute.return_value = mock_result
    result = await user_crud.get_user_by_email(
        email='teste@email.com', async_transaction=mock_db
    )

    assert result is None


async def testa_crud_delete_all_users():
    mock_db = AsyncMock(spec=AsyncSession)
    user_crud = UserCRUD()

    # Simulando que 5 usuários foram deletados
    mock_db.execute.return_value.rowcount = 5

    result = await user_crud.delete_all_users(async_transaction=mock_db)

    assert result == 5
    mock_db.execute.assert_called_once()
