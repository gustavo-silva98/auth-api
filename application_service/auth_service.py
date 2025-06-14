from datetime import timedelta
from typing import Protocol, runtime_checkable

from fastapi.security import OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from application_service.token_service import TokenService
from domain_entity.exceptions import (
    BadRequest,
    DuplicateUserError,
    PasswordNotMatch,
    UnauthorizedException,
    UserNotFound,
)
from domain_entity.models import User
from domain_entity.schemas import (
    RefreshTokenRequest,
    Token,
    UserCreateDTO,
    UserFromDBDTO,
)
from infra_repository.crud import UserCRUD
from settings import Settings


@runtime_checkable
class AuthServiceProtocol(Protocol):
    user_crud: UserCRUD

    async def create_user_from_route(
        self, user: UserCreateDTO
    ) -> UserFromDBDTO:
        ...   # pragma: no cover

    async def authenticate_get_token(
        self, auth_request: OAuth2PasswordRequestForm
    ) -> Token:
        ...   # pragma: no cover

    async def refresh_access_token(
        self, refresh_token: RefreshTokenRequest
    ) -> Token:
        ...   # pragma: no cover

    async def get_users(self) -> list:
        ...   # pragma: no cover

    async def get_users_me(self, token) -> UserFromDBDTO:
        ...   # pragma: no cover


@runtime_checkable
class HasherProtocol(Protocol):
    def hash(self, password: str) -> str:
        ...   # pragma: no cover

    def verify(self, password: str, hash_password: str) -> bool:
        ...   # pragma: no cover


class BcryptHasher(HasherProtocol):
    def __init__(self, context: CryptContext):
        self.context = context

    def hash(self, password: str) -> str:
        return self.context.hash(password)

    def verify(self, password: str, hash_password: str) -> bool:
        return self.context.verify(password, hash_password)


class AuthService:
    def __init__(
        self,
        hasher: HasherProtocol,
        user_crud: UserCRUD,
        db: AsyncSession,
        settings: Settings,
        token_service: TokenService,
    ):
        self.hasher = hasher
        self.user_crud = user_crud
        self.db = db
        self.settings = settings
        self.token_service = token_service

    async def create_user_from_route(
        self, user: UserCreateDTO
    ) -> UserFromDBDTO:

        get_user = await self.user_crud.get_user_by_email(
            email=user.email, async_transaction=self.db
        )

        if get_user:
            raise DuplicateUserError('Usuário já cadastrado.')

        if user.pwd_plain != user.confirm_pwd_plain:
            raise PasswordNotMatch()

        pwd_hash = self.hasher.hash(user.pwd_plain)

        result = await self.user_crud.insert_user(
            User(
                username=user.username,
                email=user.email,
                fullname=user.fullname,
                password=pwd_hash,
                active=True,
            ),
            self.db,
        )

        if result is None:
            raise UserNotFound(message='Falha na criação do usuário.')

        return UserFromDBDTO(
            id=result.id,
            username=result.username,
            email=result.email,
            fullname=result.fullname,
        )

    async def authenticate_get_token(
        self, auth_request: OAuth2PasswordRequestForm
    ) -> Token:

        get_user = await self.user_crud.get_user_by_username(
            auth_request.username, async_transaction=self.db
        )
        if get_user is None:
            raise UserNotFound()

        if not self.hasher.verify(auth_request.password, get_user.password):

            raise UnauthorizedException()

        acces_token_expire = timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token_expire = timedelta(
            days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        access_token = self.token_service.create_access_token(
            auth_request.username, expires_delta=acces_token_expire
        )
        refresh_token = self.token_service.create_refresh_token(
            auth_request.username, expires_delta=refresh_token_expire
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
        )   # nosec: B106

    async def refresh_access_token(self, refresh_token: RefreshTokenRequest):
        try:
            payload = self.token_service.jwt_handler.decode(
                jwt_token=str(refresh_token),
                key=self.settings.SECRET_KEY,
                algorithm=self.settings.ALGORITHM,
            )
            if payload.get('token_type') != 'refresh':
                raise BadRequest('Token_type Inválido')

            username = payload.get('sub')
            get_user = await self.user_crud.get_user_by_username(
                str(username), async_transaction=self.db
            )
            if get_user is None:
                raise UserNotFound()
            # Se usuário foi encontrado, cria novo access token e refresh_token
            access_token_expire = timedelta(
                minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            refresh_token_expire = timedelta(
                days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

            access_token = self.token_service.create_access_token(
                get_user.username, expires_delta=access_token_expire
            )
            new_refresh_token = self.token_service.create_refresh_token(
                get_user.username, expires_delta=refresh_token_expire
            )
            # // NECESSÁRIO FLUXO DE REVOGAR ANTIGO REFRESH TOKEN TODO
            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type='bearer',
            )   # nosec: B106

        except PyJWTError as err:
            raise UnauthorizedException() from err

    async def get_users(self):
        users = await self.user_crud.get_users(async_transaction=self.db)
        if not users:
            return []
        if isinstance(users, User):
            users = [users]
        return [UserFromDBDTO.model_validate(u) for u in users]

    async def get_users_me(self, token: str) -> UserFromDBDTO:
        try:
            payload = self.token_service.jwt_handler.decode(
                token, self.settings.SECRET_KEY, self.settings.ALGORITHM
            )
            username = payload.get('sub')
            if username is None:
                raise UnauthorizedException()

        except PyJWTError as err:
            raise UnauthorizedException() from err

        get_user = await self.user_crud.get_user_by_username(
            username=username, async_transaction=self.db
        )
        if get_user is None:
            raise UnauthorizedException()
        return UserFromDBDTO.model_validate(get_user)
