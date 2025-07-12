from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from domain_entity.models import Permission, RevokedRefreshToken, Role, User
from infra_repository.crud import UserCRUD

"""
Métodos de teste para a classe UserCRUD.
MÉTODOS USER CRUD:
- insert_user - OK
- delete_user_by_email - OK
- get_user_by_email - OK
- delete_all_users - // OK


"""


@pytest.fixture
def get_role():
    return Role(id=1, name='Role', description='Description Role')


@pytest.fixture
def get_perm():
    return Permission(
        id=1, scope='permission:scope', description='description permission'
    )


@pytest.fixture
def user_model():
    return User(
        username='test_user',
        email='teste@email.com',
        fullname='Test User',
        password='hashed_password',
    )


@pytest.fixture
def get_revoked_refresh_token():
    return RevokedRefreshToken(
        id=1,
        token_id=1,
        user_id=1,
        expires_at=datetime(year=2020, month=1, day=1, hour=12, minute=0),
        revoked_at=datetime(year=2020, month=1, day=1, hour=12, minute=0),
    )


@pytest.fixture
def get_db():
    return AsyncMock(spec=AsyncSession)


async def testa_crud_get_perm_by_name(get_db, get_perm):
    mock_db = get_db
    user_crud = UserCRUD()
    resultado_get = get_perm

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resultado_get
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert (
        await user_crud.get_permission_by_name('permission:scope', mock_db)
        == resultado_get
    )


async def testa_crud_get_role_by_name(get_db, get_role):
    mock_db = get_db
    user_crud = UserCRUD()
    resultado_get = get_role

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resultado_get
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert (
        await user_crud.get_role_by_name('RoleName', mock_db) == resultado_get
    )


async def testa_crud_get_perm_by_id(get_db, get_perm):
    mock_db = get_db
    user_crud = UserCRUD()
    resultado_get = get_perm

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resultado_get
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert await user_crud.get_permission_by_id(1, mock_db) == resultado_get


async def testa_crud_get_role_by_id(get_db, get_role):
    mock_db = get_db
    user_crud = UserCRUD()
    resultado_get = get_role

    mock_result = MagicMock()
    mock_unique = MagicMock()
    mock_unique.scalar_one_or_none.return_value = resultado_get
    mock_result.unique.return_value = mock_unique
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert await user_crud.get_role_by_id(1, mock_db) == resultado_get


async def testa_crud_get_user_by_id(get_db):
    mock_db = get_db
    user_crud = UserCRUD()
    resultado_get = user_model

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resultado_get
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert await user_crud.get_user_by_id(1, mock_db) == resultado_get


async def testa_get_users(get_db, user_model):
    mock_db = get_db
    user_teste = user_model
    user_crud = UserCRUD()

    # Mock the result of db.execute to have a .scalars().all() chain
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [user_teste]
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert await user_crud.get_users(mock_db) == [user_teste]


async def testa_get_permissions(get_db, get_perm):
    mock_db = get_db
    perm = get_perm
    user_crud = UserCRUD()

    # Mock the result of db.execute to have a .scalars().all() chain
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [perm]
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert await user_crud.get_permissions(mock_db) == [perm]


async def testa_get_roles(get_db, get_role):
    mock_db = get_db
    role = get_role
    user_crud = UserCRUD()

    # Mock the result of db.execute to have a .scalars().all() chain
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [role]
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    assert await user_crud.get_roles(mock_db) == [role]


async def testa_insert_permission(get_db, get_perm):
    mock_db = get_db
    perm = get_perm

    user_crud = UserCRUD()
    mock_db.add = MagicMock(return_value=perm)

    assert (
        await user_crud.insert_permission(
            permission=get_perm, async_transaction=mock_db
        )
        == perm
    )


async def testa_revoke_token(get_db, get_revoked_refresh_token):
    mock_db = get_db
    token = get_revoked_refresh_token

    user_crud = UserCRUD()
    mock_db.add = MagicMock(return_value=token)

    assert (
        await user_crud.revoke_token(
            token_to_revoke=token, async_transaction=mock_db
        )
        == token
    )


async def testa_insert_role(get_db, get_role):
    mock_db = get_db
    role = get_role

    user_crud = UserCRUD()
    mock_db.add = Mock(return_value=role)

    assert (
        await user_crud.insert_role(role=role, async_transaction=mock_db)
        == role
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


async def testa_crud_delete_role_by_id(get_db):
    mock_db = get_db
    user_crud = UserCRUD()
    mock_db.execute.return_value.rowcount = 1

    result = await user_crud.delete_role_by_id(1, async_transaction=mock_db)
    assert result == 1
    mock_db.execute.assert_called_once()


async def testa_crud_delete_perm_by_id(get_db):
    mock_db = get_db
    user_crud = UserCRUD()
    mock_db.execute.return_value.rowcount = 1

    result = await user_crud.delete_perm_by_id(1, async_transaction=mock_db)
    assert result == 1
    mock_db.execute.assert_called_once()


async def testa_crud_delete_role_by_name(get_db):
    mock_db = get_db
    user_crud = UserCRUD()
    mock_db.execute.return_value.rowcount = 1

    result = await user_crud.delete_role_by_name(
        'Permission Name', async_transaction=mock_db
    )
    assert result == 1
    mock_db.execute.assert_called_once()


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
