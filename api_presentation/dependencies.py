from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from application_service.auth_service import (
    AuthService,
    AuthServiceProtocol,
    BcryptHasher,
    HasherProtocol,
)
from application_service.token_service import (
    JWTLibHandler,
    JWTTokenService,
    TokenService,
)
from infra_repository.crud import UserCRUD
from infra_repository.db import db_handler
from settings import Settings

_settings_singleton = None
_crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_handler.get_db():
        async with session.begin():
            yield session


def get_bcrypt_hasher():
    return BcryptHasher(context=_crypt_context)


def get_user_crud() -> UserCRUD:
    return UserCRUD()


def get_settings() -> Settings:
    global _settings_singleton
    if _settings_singleton is None:
        _settings_singleton = Settings()
    return _settings_singleton


def get_jwt_token_service() -> TokenService:
    settings = Settings()
    jwt_handler = JWTLibHandler()
    return JWTTokenService(jwt_handler=jwt_handler, settings=settings)


def get_auth_service(
    hasher: Annotated[HasherProtocol, Depends(get_bcrypt_hasher)],
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
    db: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    token_service: Annotated[TokenService, Depends(get_jwt_token_service)],
) -> AuthServiceProtocol:

    return AuthService(
        hasher=hasher,
        user_crud=user_crud,
        db=db,
        settings=settings,
        token_service=token_service,
    )


oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/auth-token')
