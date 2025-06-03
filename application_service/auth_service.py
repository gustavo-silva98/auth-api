from typing import Protocol

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from domain_entity.exceptions import DuplicateUserError, PasswordNotMatch
from domain_entity.models import User
from domain_entity.schemas import UserCreateDTO
from infra_repository.crud import UserCRUD


class HasherProtocol(Protocol):
    def hash(self,password : str) -> str:
        ...

class BcryptHasher(HasherProtocol):
    def __init__(self,context: CryptContext):
        self.context = context

    def hash(self,password: str) -> str:
        return self.context.hash(password)
    


class AuthService:
    def __init__(self,hasher: HasherProtocol,user_crud: UserCRUD,db: AsyncSession):
        self.hasher = hasher
        self.user_crud = user_crud
        self.db = db
    
    async def create_user_from_route(self,user : UserCreateDTO):

        get_user = await self.user_crud.get_user_by_email(
            email= user.email,async_transaction=self.db
        )

        if get_user:
            raise DuplicateUserError("Usuário já cadastrado.")
        
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
            self.db
        )

        return result

