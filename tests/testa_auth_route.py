from unittest.mock import AsyncMock, create_autospec

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api_presentation.auth_router import auth_router
from api_presentation.dependencies import get_auth_service
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import (
    RefreshTokenRequest,
    Token,
    UserFromDBDTO,
)
from infra_repository.crud import UserCRUD


@pytest.fixture
def mock_auth_service():
    service = create_autospec(AuthServiceProtocol)

    service.create_user_from_route = AsyncMock()
    service.authenticate_get_token = AsyncMock()
    service.refresh_access_token = AsyncMock()

    service.user_crud = create_autospec(UserCRUD, instance=True)
    service.user_crud.get_user_by_username = AsyncMock()

    return service


@pytest.fixture
def client(mock_auth_service):
    app = FastAPI()
    app.include_router(auth_router)

    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    return TestClient(app)


"""
async def testa_create_user_success(client, mock_auth_service):
    mock_user = UserFromDBDTO(
        id=1,
        username='username_teste',
        email='email@teste.com',
        fullname='Teste da Silva',
    )
    mock_auth_service.create_user_from_route.return_value = mock_user

    user_data = UserCreateDTO(
        username='username_teste',
        email='email@teste.com',
        fullname='Teste da Silva',
        pwd_plain='senha',
        confirm_pwd_plain='senha',
    )
    response = client.post('/create-user', json=user_data.model_dump())

    assert response.status_code == 200
    assert response.json() == mock_user.model_dump()
    mock_auth_service.create_user_from_route.assert_called_once_with(
        UserCreateDTO(
            username='username_teste',
            email='email@teste.com',
            fullname='Teste da Silva',
            pwd_plain='senha',
            confirm_pwd_plain='senha',
        )
    )
"""


async def testa_auth_token_success(client, mock_auth_service):
    mock_token = Token(
        access_token='access123',
        refresh_token='refresh123',
        token_type='bearer',
    )
    mock_user = UserFromDBDTO(
        id=1,
        username='username_teste',
        email='email@teste.com',
        fullname='Teste da Silva',
    )

    mock_auth_service.authenticate_get_token.return_value = mock_token
    mock_auth_service.user_crud.get_user_by_username.return_value = mock_user

    form_data = {'username': 'string', 'password': 'string'}

    response = client.post(
        '/auth-token',
        data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    print(response)
    assert response.status_code == 200
    assert response.json() == mock_token.model_dump()
    mock_auth_service.authenticate_get_token.assert_called_once()


async def testa_refresh_token_success(client, mock_auth_service):
    new_token = Token(
        access_token='new_access',
        refresh_token='new_refresh',
        token_type='bearer',
    )
    mock_user = UserFromDBDTO(
        id=1,
        username='username_teste',
        email='email@teste.com',
        fullname='Teste da Silva',
    )

    mock_auth_service.refresh_access_token.return_value = new_token
    user_crud = UserCRUD()
    user_crud.get_user_by_username.return_value = mock_user

    refresh_data = RefreshTokenRequest(refresh_token='old_refresh')

    response = client.post('/refresh', json=refresh_data.model_dump())

    assert response.status_code == 200
    assert response.json() == new_token.model_dump()
    mock_auth_service.refresh_access_token.assert_called_once_with(
        refresh_data.refresh_token
    )
