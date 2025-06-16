from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    fullname: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PermissionItemDTO(BaseModel):
    """
    Schema
        permission: str
        description: str
    """

    permission: str
    description: str


class CreateRoleDTO(BaseModel):
    """
    *Schema*
        name: str
        permissions: list[PermissionItemDTO]
        ~~~
        *Example:*
        name : RoleTeste
        permissions: [{permission:"users:write",description:"Descrição da permissao"}]
    """

    name: str
    description: str
    permissions: list[PermissionItemDTO]
