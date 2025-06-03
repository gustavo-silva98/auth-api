from unittest.mock import AsyncMock

import pytest
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from application_service.auth_service import AuthService, BcryptHasher
from domain_entity.exceptions import DuplicateUserError, PasswordNotMatch
from domain_entity.schemas import UserCreateDTO, UserFromDBDTO
from infra_repository.crud import UserCRUD

"""
Métodos AuthService
- create_user_from_route - OK
- login_user_from_route - //TODO
"""


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
def get_hasher():
    return BcryptHasher(
        context=CryptContext(schemes=['bcrypt'], deprecated='auto')
    )


@pytest.fixture
def mock_user_from_db():
    return UserFromDBDTO(
        id=1,
        username='Username_Teste',
        email='email@teste.com',
        fullname='Fullname Teste',
    )


async def testa_service_create_user_valido(
    user_create_dto, mock_user_from_db, get_hasher
):

    mock_db = AsyncMock(spec=AsyncSession)

    user_create = user_create_dto

    mock_return = mock_user_from_db

    user_crud = UserCRUD()
    auth_service = AuthService(get_hasher, user_crud=user_crud, db=mock_db)

    user_crud.insert_user = AsyncMock(return_value=mock_return)
    user_crud.get_user_by_email = AsyncMock(return_value=None)

    result = await auth_service.create_user_from_route(user=user_create)

    assert result == mock_return
    user_crud.insert_user.assert_called_once()


async def testa_service_create_user_duplicated(user_create_dto, get_hasher):
    mock_db = AsyncMock(spec=AsyncSession)

    user_crud = UserCRUD()

    return_mock = mock_user_from_db

    user_crud.get_user_by_email = AsyncMock(retur_value=return_mock)
    auth_service = AuthService(get_hasher, user_crud, mock_db)

    with pytest.raises(DuplicateUserError):
        await auth_service.create_user_from_route(user=user_create_dto)


async def testa_create_user_pwd_dont_match(user_create_dto, get_hasher):
    mock_db = AsyncMock(spec=AsyncSession)

    user_create = user_create_dto
    user_create.pwd_plain = 'senha não bate'
    user_crud = UserCRUD()
    user_crud.get_user_by_email = AsyncMock(return_value=None)
    auth_service = AuthService(get_hasher, user_crud, mock_db)

    with pytest.raises(PasswordNotMatch):

        await auth_service.create_user_from_route(user=user_create_dto)


"""

async def authenticate_and_get_token_pwd_unmatch(auth_request_dto):
    mock_db = AsyncMock(spec=AsyncSession)

    Hasher = AuthService.Hasher
"""
