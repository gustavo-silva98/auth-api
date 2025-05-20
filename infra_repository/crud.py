from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from domain_entity.models import User


class UserCRUD:
    @staticmethod
    async def insert_user(
        user: User, async_transaction: AsyncSession
    ) -> User | None:
        try:
            async_transaction.add(user)
            await async_transaction.flush()
            await async_transaction.refresh(user)
            return user
        except IntegrityError as e:
            print(f'Erro de integridade: {e}')
            return None

    @staticmethod
    async def delete_user_by_email(
        email: str, async_transaction: AsyncSession
    ) -> int:

        query = delete(User).where(User.email == email)

        result = await async_transaction.execute(query)
        return result.rowcount

    @staticmethod
    async def get_user_by_email(email: str, async_transaction: AsyncSession):
        query = select(User).where(User.email == email)

        try:
            result = await async_transaction.execute(query)
            return result.scalar_one_or_none
        except SQLAlchemyError as e:
            return f'Erro ao selecionar o usuário: {e}'

    @staticmethod
    async def delete_all_users(async_transaction: AsyncSession) -> int:
        result = await async_transaction.execute(delete(User))

        return result.rowcount
