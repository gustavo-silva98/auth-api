from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    username: str = Field(
        min_length=6, max_length=20, description='Username/Login do usuário.'
    )
    email: EmailStr
    fullname: str = Field(description='Nome completo')
    pwd_plain: str = Field(description='Campo de senha plain text.')
    confirm_pwd_plain: str = Field(
        description='Campo de confirmação de senha.'
    )


class UserFromDBDTO(BaseModel):
    id: int
    username: str
    email: str
    fullname: str


class Token(BaseModel):
    access_token: str
    token_type: str
