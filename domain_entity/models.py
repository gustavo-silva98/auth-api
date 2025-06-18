from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(AsyncAttrs, DeclarativeBase):
    pass


# Tabela associativa para User-Role
user_role = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
)

# Tabela associativa para Role-Permission
role_permission = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column(
        'permission_id',
        Integer,
        ForeignKey('permissions.id'),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(unique=True)
    fullname: Mapped[str]
    password: Mapped[str]
    active: Mapped[bool]

    # Nova relação com roles
    roles: Mapped[list['Role']] = relationship(
        secondary=user_role, back_populates='users'
    )

    def __repr__(self) -> str:
        return (
            f'User (id={self.id}, username={self.username},'
            f'email={self.email}, fullname={self.fullname}, active={self.active})'
        )


class Role(Base):
    """
    Tablename = 'roles:

        Params
        id: int
        name: str
        permissions: list[Permission]
        description: str
    """

    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(unique=False)

    # Relações
    users: Mapped[list['User']] = relationship(
        secondary=user_role, back_populates='roles'
    )

    permissions: Mapped[list['Permission']] = relationship(
        secondary=role_permission, back_populates='roles'
    )


class Permission(Base):

    """
    Tablename = 'permissions':

        Params
            id: int
            scope: str
            description: str

    """

    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    scope: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(unique=True)

    # relação
    roles: Mapped[list['Role']] = relationship(
        secondary=role_permission, back_populates='permissions'
    )


class RevokedRefreshToken(Base):
    """
    Represents a revoked refresh token entry in the authentication system.

    Attributes:
        id (int): Primary key identifier for the revoked token record.
        token_id (int): Identifier of the refresh token that has been revoked.
        user_id (int): Identifier of the user associated with the revoked token.
        expires_at (datetime): The original expiration datetime of the refresh token.
        revoked_at (datetime): The datetime when the token was revoked.
            Defaults to the current time.
    """

    __tablename__ = 'revoked_refresh_tokens'

    """"""

    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
