from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from domain_entity.models import Permission, RevokedRefreshToken, Role, User


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

        query = (
            select(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .where(User.username == username)
        )

        result = await async_transaction.execute(query)

        return result.unique().scalar_one_or_none()

    @staticmethod
    async def get_users(async_transaction: AsyncSession):

        query = select(User)

        result = await async_transaction.execute(query)
        return result.scalars()

    @staticmethod
    async def get_permission_by_name(
        permission: str, async_transaction: AsyncSession
    ):
        query = select(Permission).where(Permission.scope == permission)
        result = await async_transaction.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def insert_permission(
        permission: Permission, async_transaction: AsyncSession
    ) -> Permission:

        async_transaction.add(permission)
        await async_transaction.flush()
        await async_transaction.refresh(permission)
        return permission

    @staticmethod
    async def insert_role(role: Role, async_transaction: AsyncSession) -> Role:

        async_transaction.add(role)
        await async_transaction.flush()
        await async_transaction.refresh(role)
        return role

    @staticmethod
    async def delete_role(
        role_name: str, async_transaction: AsyncSession
    ) -> int:
        query = delete(Role).where(Role.name == role_name)
        result = await async_transaction.execute(query)

        return result.rowcount

    @staticmethod
    async def get_user_by_id(user_id: int, async_transaction: AsyncSession):
        query = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        result = await async_transaction.execute(query)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_by_id(role_id: int, async_transaction: AsyncSession):
        query = select(Role).where(Role.id == role_id)
        result = await async_transaction.execute(query)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_roles_and_permissions_for_user_id(
        user_id: int, async_transaction: AsyncSession
    ):
        query = (
            select(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .where(User.id == user_id)
        )
        result = await async_transaction.execute(query)
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def revoke_token(
        token_to_revoke: RevokedRefreshToken, async_transaction: AsyncSession
    ) -> RevokedRefreshToken:

        async_transaction.add(token_to_revoke)
        await async_transaction.flush()
        await async_transaction.refresh(token_to_revoke)

        return token_to_revoke

    @staticmethod
    async def is_token_revoked(
        token_id: int, async_transaction: AsyncSession
    ) -> bool:
        result = await async_transaction.execute(
            select(RevokedRefreshToken).where(
                RevokedRefreshToken.id == token_id
            )
        )
        return result.scalars().first() is not None
