from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

import jwt
from jwt import PyJWTError

from domain_entity.exceptions import UnauthorizedException
from settings import Settings


class JWTHandler(Protocol):
    def encode(self, payload: dict, key: str, algorithm: str) -> str:
        ...   # pragma: no cover

    def decode(
        self,
        jwt_token: str,
        key: str,
        algorithm: str,
        options: dict[str, Any] | None = None,
    ) -> dict:

        ...   # pragma: no cover1


class JWTLibHandler(JWTHandler):
    def encode(self, payload: dict, key: str, algorithm: str) -> str:
        encode = jwt.encode(payload, key, algorithm)
        return encode

    def decode(
        self,
        jwt_token: str,
        key: str,
        algorithm: str,
        options: dict[str, Any] | None = None,
    ) -> dict:

        decode = jwt.decode(
            jwt=jwt_token, key=key, algorithms=algorithm, options=options
        )

        return decode


@runtime_checkable
class TokenService(Protocol):
    jwt_handler: JWTHandler
    settings: Settings

    def create_access_token(
        self,
        username: str,
        permissions: list[str],
        expires_delta: timedelta | None,
    ) -> str:
        ...  # pragma: no cover

    def create_refresh_token(
        self, username: str, expires_delta: timedelta | None
    ) -> str:
        ...   # pragma: no cover

    def decode_token(self, token: str) -> dict:
        ...   # pragma: no cover


class JWTTokenService(TokenService):
    def __init__(self, jwt_handler: JWTHandler, settings: Settings):
        self.jwt_handler = jwt_handler
        self.settings = settings

    def create_access_token(
        self,
        username: str,
        permissions: list[str],
        expires_delta: timedelta | None = None,
    ):
        to_encode = {'sub': username}

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta

        to_encode['exp'] = str(int(expire.timestamp()))
        to_encode['token_type'] = 'access'  # nosec: B105
        to_encode['perms'] = ','.join(permissions)

        encoded_jwt = self.jwt_handler.encode(
            to_encode, self.settings.SECRET_KEY, self.settings.ALGORITHM
        )

        return encoded_jwt

    def create_refresh_token(
        self, username: str, expires_delta: timedelta | None = None
    ):

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta

        to_encode = {'sub': username, 'exp': expire, 'token_type': 'refresh'}
        to_encode['jti'] = str(uuid4())

        encoded_jwt = self.jwt_handler.encode(
            to_encode, self.settings.SECRET_KEY, self.settings.ALGORITHM
        )

        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        try:
            return self.jwt_handler.decode(
                token, self.settings.SECRET_KEY, self.settings.ALGORITHM
            )
        except PyJWTError as err:
            raise UnauthorizedException() from err
