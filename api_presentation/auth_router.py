from typing import Annotated

from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api_presentation.dependencies import (
    get_auth_service,
    get_current_user,
)
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import RefreshTokenRequest, Token, UserFromDBDTO

auth_router = APIRouter()


@auth_router.post('/auth-token', response_model=Token)
async def auth_get_token(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):

    return await auth_service.authenticate_get_token(user_data)


@auth_router.post('/refresh')
async def refresh_access_token(
    refresh_token: Annotated[RefreshTokenRequest, Body(...)],
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):

    return await auth_service.refresh_access_token(refresh_token.refresh_token)


@auth_router.post('/logout')
async def logout(
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
    current_user: Annotated[UserFromDBDTO, Depends(get_current_user)],
    token: Annotated[RefreshTokenRequest, Body(...)],
):
    print(token)
    return await auth_service.revoke_token(
        token=token.refresh_token, user_id=current_user.id
    )
