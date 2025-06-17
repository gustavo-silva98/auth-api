from datetime import timedelta
from typing import Protocol, runtime_checkable

from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
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
from domain_entity.models import Permission, Role, User
from domain_entity.schemas import (
    CreateRoleDTO,
    RefreshTokenRequest,
    Token,
    UserCreateDTO,
    UserFromDBDTO,
    UserRolePermissionDTO,
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

    async def get_current_active_user(
        self, token: str, required_perms: SecurityScopes
    ) -> UserFromDBDTO:
        ...

    async def create_roles_with_permissions(
        self, role_data: CreateRoleDTO
    ) -> Role:
        ...

    async def delete_role_by_name(self, role_name: str) -> dict:
        ...

    async def assign_role_to_user(self, role_id: int, user_id: int) -> dict:
        ...

    async def list_roles_and_permissions_for_user_id(
        self, user_id: int
    ) -> UserRolePermissionDTO:
        ...


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
        permissions = []
        for role in get_user.roles:
            for permission in role.permissions:
                permissions.append(permission.scope)

        access_token = self.token_service.create_access_token(
            auth_request.username,
            permissions=permissions,
            expires_delta=acces_token_expire,
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

            permissions = []
            for role in get_user.roles:
                for permission in role.permissions:
                    permissions.append(permission.scope)

            access_token = self.token_service.create_access_token(
                get_user.username,
                permissions=permissions,
                expires_delta=access_token_expire,
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

    async def get_current_active_user(
        self, token: str, required_perms: SecurityScopes
    ) -> UserFromDBDTO:

        authenticate_value = 'Bearer'
        if required_perms.scopes:
            authenticate_value = f'Bearer scope={required_perms.scope_str}'

        payload = self.token_service.decode_token(token=token)
        username = payload.get('sub')
        user_perms = payload.get('perms')

        if not username or not user_perms:
            raise UnauthorizedException(bearer=authenticate_value)

        user_perms = user_perms.split(',')

        result = await self.user_crud.get_user_by_username(
            username=username, async_transaction=self.db
        )
        if not result:
            raise UnauthorizedException(bearer=authenticate_value)
        if not result.active:
            raise UnauthorizedException(bearer=authenticate_value)

        for permission in required_perms.scopes:
            if permission not in user_perms:
                raise UnauthorizedException(bearer=authenticate_value)

        return UserFromDBDTO(
            id=result.id,
            username=result.username,
            email=result.email,
            fullname=result.fullname,
        )

    async def create_roles_with_permissions(
        self, role_data: CreateRoleDTO
    ) -> Role:
        permissions = []

        for permission in role_data.permissions:
            result = await self.user_crud.get_permission_by_name(
                permission.permission, self.db
            )
            print(result)
            if not result:
                perm = Permission(
                    scope=permission.permission,
                    description=permission.description,
                )
                insert_perm = await self.user_crud.insert_permission(
                    permission=perm, async_transaction=self.db
                )
                permissions.append(insert_perm)
                print(permissions)

        role = Role(
            name=role_data.name,
            description=role_data.description,
            permissions=permissions,
        )
        insert_role = await self.user_crud.insert_role(
            role=role, async_transaction=self.db
        )
        if insert_role:
            return insert_role
        else:
            raise BadRequest('Failed to create role with permissions.')

    async def delete_role_by_name(self, role_name: str):
        delete = await self.user_crud.delete_role(
            role_name=role_name, async_transaction=self.db
        )
        if delete <= 0:
            raise BadRequest('Role não encontrada')

        return {'Roles deletadas': delete}

    async def assign_role_to_user(self, role_id: int, user_id: int):
        user = await self.user_crud.get_user_by_id(
            user_id=user_id, async_transaction=self.db
        )

        role = await self.user_crud.get_role_by_id(
            role_id=role_id, async_transaction=self.db
        )

        if not user or not role:
            raise UserNotFound()

        if role not in user.roles:
            user.roles.append(role)
            await self.db.commit()

            return {
                'message': f'Role {role.name} assigned to user {user.username}'
            }
        else:
            raise BadRequest(
                f'Role {role} already assigned to user {user.username}'
            )

    async def list_roles_and_permissions_for_user_id(self, user_id: int):

        result = await self.user_crud.get_roles_and_permissions_for_user_id(
            user_id=user_id, async_transaction=self.db
        )

        if not result:
            raise UserNotFound()

        return UserRolePermissionDTO.model_validate(result.roles)
