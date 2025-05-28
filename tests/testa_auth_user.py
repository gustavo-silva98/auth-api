from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from application_service.auth_service import AuthService
from domain_entity.schemas import UserCreateDTO, UserResponseDTO
from infra_repository.crud import UserCRUD


async def testa_service_create_user_valido():
    mock_db = AsyncMock(spec=AsyncSession)

    usuario_criar = UserCreateDTO(
        username='Username_Teste',
        email='email@teste.com',
        fullname='Fullname Teste',
        pwd_plain='pwd plain Teste',
        confirm_pwd_plain='pwd plain Teste',
    )

    mock_return = UserResponseDTO(
        id=1,
        username='Username_Teste',
        email='email@teste.com',
        fullname='Fullname Teste',
    )

    user_crud = UserCRUD()
    user_crud.insert_user = AsyncMock(return_value=mock_return)

    result = await AuthService.create_user_from_route(
        usuario_criar, user_crud=user_crud, db=mock_db
    )

    assert result == mock_return
    assert user_crud.insert_user.assert_called_once()
