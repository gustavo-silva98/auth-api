from datetime import UTC, datetime, timedelta
from typing import Protocol, runtime_checkable

import jwt

from settings import Settings


@runtime_checkable
class TokenService(Protocol):
    def create_access_token(
        self, username: str, expires_delta: timedelta | None
    ) -> str:
        ...  # pragma: no cover


class JWTHandler(Protocol):
    def encode(self, payload: dict, key: str, algorithm: str) -> str:
        ...   # pragma: no cover


class JWTLibHandler(JWTHandler):
    def encode(self, payload: dict, key: str, algorithm: str) -> str:
        encode = jwt.encode(payload, key, algorithm)
        return encode


class JWTTokenService(TokenService):
    def __init__(self, jwt_handler: JWTHandler, settings: Settings):
        self.jwt_handler = jwt_handler
        self.settings = settings

    def create_access_token(
        self, username: str, expires_delta: timedelta | None = None
    ):
        to_encode = {'sub': username}

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta

        to_encode['exp'] = str(int(expire.timestamp()))

        encoded_jwt = self.jwt_handler.encode(
            to_encode, self.settings.SECRET_KEY, self.settings.ALGORITHM
        )

        return encoded_jwt
