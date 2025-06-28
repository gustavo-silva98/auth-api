from typing import Annotated

from fastapi import APIRouter, Depends

from api_presentation.dependencies import get_auth_service
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import CreateRoleDTO, UserRolePermissionDTO

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
) -> dict:
    return await auth_service.delete_role_by_name(role_name)


@role_router.delete('/roles/{id}')
async def delete_role_by_id(
    role_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
) -> dict:

    return await auth_service.delete_role_by_id(role_id=role_id)


@role_router.post('/roles/{user_id}/update')
async def assign_role(
    user_id: int,
    role_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    """
    Assigns a role to a user.

    Args:
        user_id (int): The ID of the user to whom the role will be assigned.
        role_id (int): The ID of the role to be assigned to the user.
        auth_service (Annotated[AuthServiceProtocol, Depends]):
            The authentication service instance used to perform the operation.

    Returns:
        dict: A dictionary containing the result of the role assignment operation.
    """
    return await auth_service.assign_role_to_user(
        role_id=role_id, user_id=user_id
    )


@role_router.get('/roles/{user_id}/list')
async def get_roles_list_user_id(
    user_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
) -> UserRolePermissionDTO:
    """
    Get roles for a user

    Args:
        user_id (int): User ID recebido como query parameter
        auth_service (Annotated[AuthServiceProtocol, Depends): _Método que trás
        instancia de auth_service_

    Returns:
        UserRolePermissionDTO: _DTO que retorna Permissões e informações de usuário_
    """
    return await auth_service.list_roles_and_permissions_for_user_id(
        user_id=user_id
    )


# //TODO Fazer endpoint GET ROLE BY ID


@role_router.get('/{role_id}')
async def get_role_by_id(
    role_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.return_role_by_id(role_id)
