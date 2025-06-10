from typing import Annotated

from fastapi import APIRouter, Depends

from api_presentation.dependencies import get_auth_service
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import (
    UserCreateDTO,
    UserFromDBDTO,
)

user_router = APIRouter()


@user_router.post('/create-user', response_model=UserFromDBDTO)
async def auth_route_create_user(
    user_data: UserCreateDTO,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.create_user_from_route(user_data)


@user_router.get('/get_users')
async def get_users(
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):

    return await auth_service.get_users()
