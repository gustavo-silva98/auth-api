from typing import Annotated

from fastapi import APIRouter, Depends

from api_presentation.dependencies import get_auth_service
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import CreateRoleDTO

role_router = APIRouter()


@role_router.post('/roles')
async def create_role(
    role_data: CreateRoleDTO,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.create_roles_with_permissions(role_data)


@role_router.delete('/roles')
async def delete_role_by_name(
    role_name: str,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.delete_role_by_name(role_name)
