from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(unique=True)
    fullname: Mapped[str]
    password: Mapped[str]
    active: Mapped[bool]

    def __repr__(self) -> str:
        return (
            f'User (id={self.id}, username={self.username},'
            f'email={self.email}, fullname={self.fullname}, active={self.active})'
        )
