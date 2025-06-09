from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from application_service.auth_service import AuthService, BcryptHasher
from application_service.token_service import JWTLibHandler, JWTTokenService
from domain_entity.exceptions import (
    DuplicateUserError,
    PasswordNotMatch,
    UnauthorizedException,
    UserNotFound,
)
from domain_entity.models import User
from domain_entity.schemas import (
    Token,
    UserCreateDTO,
    UserFromDBDTO,
)
from infra_repository.crud import UserCRUD
from settings import Settings

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
def get_token_service():
    settings = Settings()
    jwt_handler = JWTLibHandler()
    return JWTTokenService(jwt_handler=jwt_handler, settings=settings)


@pytest.fixture
def get_settings():
    return Settings()


@pytest.fixture
def mock_user_from_db():
    return UserFromDBDTO(
        id=1,
        username='Username_Teste',
        email='email@teste.com',
        fullname='Fullname Teste',
    )


@pytest.fixture
def mock_user_class():
    return User(
        id=1,
        username='Username_Teste',
        email='email@teste.com',
        fullname='Fullname Teste',
        password='password_teste',
        active=True,
    )


@pytest.fixture
def auth_request_dto():
    return OAuth2PasswordRequestForm(
        username='username_teste', password='password_teste'
    )


async def testa_service_create_user_valido(
    user_create_dto, mock_user_from_db, get_hasher
):

    mock_db = AsyncMock(spec=AsyncSession)

    user_create = user_create_dto

    mock_return = mock_user_from_db

    user_crud = UserCRUD()
    mock_settings = Mock()
    mock_token_service = Mock()
    auth_service = AuthService(
        get_hasher,
        user_crud=user_crud,
        db=mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )

    user_crud.insert_user = AsyncMock(return_value=mock_return)
    user_crud.get_user_by_email = AsyncMock(return_value=None)

    result = await auth_service.create_user_from_route(user=user_create)

    assert result == mock_return
    user_crud.insert_user.assert_called_once()


async def testa_service_create_user_none(
    user_create_dto, mock_user_from_db, get_hasher
):

    mock_db = AsyncMock(spec=AsyncSession)

    user_create = user_create_dto

    user_crud = UserCRUD()
    mock_settings = Mock()
    mock_token_service = Mock()
    auth_service = AuthService(
        get_hasher,
        user_crud=user_crud,
        db=mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )

    user_crud.insert_user = AsyncMock(return_value=None)
    user_crud.get_user_by_email = AsyncMock(return_value=None)

    with pytest.raises(UserNotFound):
        await auth_service.create_user_from_route(user=user_create)


async def testa_service_create_user_duplicated(user_create_dto, get_hasher):
    mock_db = AsyncMock(spec=AsyncSession)

    user_crud = UserCRUD()

    return_mock = mock_user_from_db

    user_crud.get_user_by_email = AsyncMock(return_value=return_mock)
    mock_settings = Mock()
    mock_token_service = Mock()
    auth_service = AuthService(
        get_hasher,
        user_crud,
        mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )

    with pytest.raises(DuplicateUserError):
        await auth_service.create_user_from_route(user=user_create_dto)


async def testa_create_user_pwd_unmatch(user_create_dto, get_hasher):
    mock_db = AsyncMock(spec=AsyncSession)

    user_create = user_create_dto
    user_create.pwd_plain = 'senha não bate'
    user_crud = UserCRUD()
    user_crud.get_user_by_email = AsyncMock(return_value=None)
    mock_settings = Mock()
    mock_token_service = Mock()
    auth_service = AuthService(
        get_hasher,
        user_crud,
        mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )

    with pytest.raises(PasswordNotMatch):

        await auth_service.create_user_from_route(user=user_create_dto)


async def testa_create_user_valid(
    user_create_dto, get_hasher, mock_user_from_db
):
    mock_db = AsyncMock(spec=AsyncSession)

    user_crud = UserCRUD()
    user_crud.get_user_by_email = AsyncMock(return_value=None)
    user_crud.insert_user = AsyncMock(return_value=mock_user_from_db)

    mock_settings = Mock()
    mock_token_service = Mock()
    auth_service = AuthService(
        get_hasher,
        user_crud=user_crud,
        db=mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )

    result = await auth_service.create_user_from_route(user_create_dto)

    assert result == mock_user_from_db


async def testa_authenticate_get_token_pwd_unmatch(
    auth_request_dto, get_hasher, mock_user_class
):

    mock_db = AsyncMock(spec=AsyncSession)

    hasher = get_hasher

    hasher.verify = Mock(return_value=False)

    user_crud = UserCRUD()
    user_crud.get_user_by_username = AsyncMock(return_value=mock_user_class)

    mock_settings = Mock()
    mock_token_service = Mock()
    auth_service = AuthService(
        hasher,
        user_crud,
        mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )
    auth_dto = auth_request_dto

    with pytest.raises(UnauthorizedException):
        await auth_service.authenticate_get_token(auth_dto)


async def testa_authenticate_get_token_user_invalid(
    auth_request_dto, get_hasher
):
    mock_db = AsyncMock(spec=AsyncSession)

    hasher = get_hasher
    user_crud = UserCRUD()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db.execute.return_value = mock_result

    auth_dto = auth_request_dto
    mock_settings = Mock()
    mock_token_service = Mock()
    auth_service = AuthService(
        hasher,
        user_crud,
        mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )

    with pytest.raises(UserNotFound):

        await auth_service.authenticate_get_token(auth_dto)


async def testa_authenticate_get_token_user_valid(
    auth_request_dto,
    get_hasher,
    mock_user_class,
    get_settings,
    get_token_service,
):
    mock_db = AsyncMock(spec=AsyncSession)

    hasher = get_hasher

    hasher.verify = MagicMock(return_value=True)

    user_crud = UserCRUD()
    user_crud.get_user_by_username = AsyncMock(return_value=mock_user_class)

    mock_settings = get_settings
    mock_token_service = get_token_service
    auth_service = AuthService(
        hasher,
        user_crud,
        mock_db,
        settings=mock_settings,
        token_service=mock_token_service,
    )
    auth_dto = auth_request_dto

    result = await auth_service.authenticate_get_token(auth_dto)

    assert isinstance(result, Token)


# Testes Bcrypt Hasher estão abaixo :


def testa_bcrypt_hash(get_hasher):
    hash = get_hasher.hash('senha_teste')

    assert get_hasher.verify('senha_teste', hash)
