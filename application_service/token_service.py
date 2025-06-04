from datetime import UTC, datetime, timedelta
from typing import Protocol

import jwt

from settings import Settings


class TokenService(Protocol):
    def create_access_token(
        self, username: str, expires_delta: timedelta | None
    ):
        ...


class JWTHandler(Protocol):
    def encode(self, payload: dict, key: str, algorithm: str) -> str:
        ...


class JWTLib(JWTHandler):
    def __init__(self, jwt_lib: jwt):
        self.jwt = jwt_lib

    def encode(self, payload: dict, key: str, algorithm: str) -> str:
        return self.jwt.encode(payload, key, algorithm)


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

        to_encode.update({'exp': expire})

        encoded_jwt = self.jwt_handler.encode(
            to_encode, self.settings.SECRET_KEY, self.settings.ALGORITHM
        )

        return encoded_jwt
