from datetime import timedelta
from typing import Protocol

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from application_service.token_service import TokenService
from domain_entity.exceptions import (
    DuplicateUserError,
    PasswordNotMatch,
    UserNotCreated,
    WrongPassword,
)
from domain_entity.models import User
from domain_entity.schemas import (
    AuthRequestDTO,
    Token,
    UserCreateDTO,
    UserFromDBDTO,
)
from infra_repository.crud import UserCRUD
from settings import Settings


class AuthServiceProtocol(Protocol):
    async def create_user_from_route(self,user: UserCreateDTO)-> UserFromDBDTO:
        ...

    async def authenticate_get_token(self,auth_request:AuthRequestDTO)-> Token:
        ...
        
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
            ),
            self.db,
        )

        if result is None:
            raise UserNotCreated(message='Falha na criação do usuário.')

        return UserFromDBDTO(
            id=result.id,
            username=result.username,
            email=result.email,
            fullname=result.fullname,
        )

    async def authenticate_get_token(
        self, auth_request: AuthRequestDTO
    ) -> Token:
        get_user = await self.user_crud.get_user_by_username(
            auth_request.username, async_transaction=self.db
        )
        if get_user is None:
            raise UserNotCreated()

        if not self.hasher.verify(auth_request.password, get_user.password):

            raise WrongPassword()

        token_expire = timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        access_token = self.token_service.create_access_token(
            auth_request.username, expires_delta=token_expire
        )
        return Token(
            access_token=access_token, token_type='bearer'
        )   # nosec: B106
