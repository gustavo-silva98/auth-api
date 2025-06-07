from collections.abc import AsyncGenerator

import pytest
from passlib.context import CryptContext

from api_presentation.dependencies import (
    _crypt_context,
    _settings_singleton,
    get_auth_service,
    get_bcrypt_hasher,
    get_jwt_token_service,
    get_session,
    get_settings,
    get_user_crud,
)
from application_service.auth_service import (
    AuthServiceProtocol,
    HasherProtocol,
)
from application_service.token_service import TokenService
from infra_repository.crud import UserCRUD
from settings import Settings


@pytest.fixture
def get_context():
    return _crypt_context


@pytest.fixture
def get_settings_singleton():
    return _settings_singleton


@pytest.fixture
async def get_session_fixture():
    async for session in get_session():
        yield session


async def testa_get_session():
    session = get_session()

    assert isinstance(session, AsyncGenerator)


async def testa_get_hasher(get_context):
    assert isinstance(get_context, CryptContext)
    hasher = get_bcrypt_hasher()
    assert isinstance(hasher, HasherProtocol)


async def testa_get_user_crud():
    user = get_user_crud()
    assert isinstance(user, UserCRUD)


async def testa_get_settings(get_settings_singleton):
    singleton = get_settings_singleton
    assert singleton is None
    assert isinstance(get_settings(), Settings)


async def testa_get_jwt_service():
    assert isinstance(get_jwt_token_service(), TokenService)


async def testa_auth_service(get_session_fixture):
    auth_serv = get_auth_service(
        hasher=get_bcrypt_hasher(),
        user_crud=get_user_crud(),
        db=get_session_fixture,
        settings=get_settings(),
        token_service=get_jwt_token_service(),
    )
    assert isinstance(auth_serv, AuthServiceProtocol)
