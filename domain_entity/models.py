from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    email: Mapped[str]
    fullname: Mapped[str]
    password: Mapped[str]

    def __repr__(self) -> str:
        return f'User (id={self.id}, username={self.username},'
        f'email={self.email}, fullname={self.fullname})'
