from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api_presentation.dependencies import (
    get_auth_service,
    oauth_scheme,
)
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import (
    RefreshTokenRequest,
    Token,
    UserCreateDTO,
    UserFromDBDTO,
)

auth_router = APIRouter()


@auth_router.post('/create-user', response_model=UserFromDBDTO)
async def auth_route_create_user(
    user_data: UserCreateDTO,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.create_user_from_route(user_data)


@auth_router.post('/auth-token', response_model=Token)
async def auth_get_token(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):

    return await auth_service.authenticate_get_token(user_data)


@auth_router.post('/refresh')
async def refresh_access_token(
    refresh_token: RefreshTokenRequest,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):

    return await auth_service.refresh_access_token(refresh_token)


@auth_router.get('/protected-route')
async def protected_route(token: Annotated[str, Depends(oauth_scheme)]):
    return {'message': f'Você conseguiu autenticar - Token: {token}'}
