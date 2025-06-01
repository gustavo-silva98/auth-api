from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from domain_entity.exceptions import DuplicateUserError, PasswordNotMatch
from domain_entity.models import User
from domain_entity.schemas import UserCreateDTO
from infra_repository.crud import UserCRUD


class AuthService:
    @staticmethod
    async def create_user_from_route(
        user: UserCreateDTO, user_crud: UserCRUD, db: AsyncSession
    ):
        get_user = await user_crud.get_user_by_email(
            email=user.email, async_transaction=db
        )
        if get_user:
            raise DuplicateUserError('Usuário já cadastrado.')

        if user.pwd_plain != user.confirm_pwd_plain:
            print(user.confirm_pwd_plain)
            raise PasswordNotMatch()

        pwd_hash = Hasher.hash_password(user.pwd_plain)

        result = await user_crud.insert_user(
            User(
                username=user.username,
                email=user.email,
                fullname=user.fullname,
                password=pwd_hash,
            ),
            db,
        )
        return result


class Hasher:
    __pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @staticmethod
    def hash_password(password):
        return Hasher.__pwd_context.hash(password)
