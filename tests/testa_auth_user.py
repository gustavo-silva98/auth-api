from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application_service.auth_service import AuthService
from domain_entity.exceptions import DuplicateUserError, PasswordNotMatch
from domain_entity.schemas import UserCreateDTO, UserFromDBDTO
from infra_repository.crud import UserCRUD


@pytest.fixture
def user_create_dto():
    return UserCreateDTO(
        username='Username_Teste',
        email='email@teste.com',
        fullname='Fullname Teste',
        pwd_plain='pwd plain Teste',
        confirm_pwd_plain='pwd plain Teste',
    )


@pytest.fixture
def mock_user_from_db():
    return UserFromDBDTO(
        id=1,
        username='Username_Teste',
        email='email@teste.com',
        fullname='Fullname Teste',
    )


async def testa_service_create_user_valido(user_create_dto, mock_user_from_db):
    mock_db = AsyncMock(spec=AsyncSession)

    usuario_criar = user_create_dto

    mock_return = mock_user_from_db

    user_crud = UserCRUD()
    user_crud.insert_user = AsyncMock(return_value=mock_return)
    user_crud.get_user_by_email = AsyncMock(return_value=None)

    result = await AuthService.create_user_from_route(
        usuario_criar, user_crud=user_crud, db=mock_db
    )

    assert result == mock_return
    user_crud.insert_user.assert_called_once()


async def testa_service_create_user_duplicated(user_create_dto):
    mock_db = AsyncMock(spec=AsyncSession)

    user_create = user_create_dto

    user_crud = UserCRUD()

    return_mock = mock_user_from_db

    user_crud.get_user_by_email = AsyncMock(retur_value=return_mock)

    with pytest.raises(DuplicateUserError):
        await AuthService.create_user_from_route(
            user=user_create, user_crud=user_crud, db=mock_db
        )


async def testa_create_user_pwd_dont_match(user_create_dto):
    mock_db = AsyncMock(spec=AsyncSession)

    user_create = user_create_dto
    user_create.pwd_plain = 'senha não bate'
    user_crud = UserCRUD()
    user_crud.get_user_by_email = AsyncMock(return_value=None)

    with pytest.raises(PasswordNotMatch):

        await AuthService.create_user_from_route(
            user=user_create, user_crud=user_crud, db=mock_db
        )
