from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain_entity.models import User


class UserCRUD:
    @staticmethod
    async def insert_user(
        user: User, async_transaction: AsyncSession
    ) -> User | None:
        async_transaction.add(user)
        await async_transaction.flush()
        await async_transaction.refresh(user)
        return user

    @staticmethod
    async def delete_user_by_email(
        email: str, async_transaction: AsyncSession
    ) -> int:
        query = delete(User).where(User.email == email)

        result = await async_transaction.execute(query)
        return result.rowcount

    @staticmethod
    async def get_user_by_email(
        email: str, async_transaction: AsyncSession
    ) -> User | None:
        query = select(User).where(User.email == email)

        result = await async_transaction.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_all_users(async_transaction: AsyncSession) -> int:
        result = await async_transaction.execute(delete(User))

        return result.rowcount

    @staticmethod
    async def get_user_by_username(
        username: str, async_transaction: AsyncSession
    ) -> User | None:

        query = select(User).where(User.username == username)

        result = await async_transaction.execute(query)

        return result.scalar_one_or_none()
