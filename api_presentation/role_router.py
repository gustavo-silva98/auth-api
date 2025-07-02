from typing import Annotated

from fastapi import APIRouter, Depends

from api_presentation.dependencies import get_auth_service
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import (
    CreateRoleDTO,
    PermissionItemDTO,
    UserRolePermissionDTO,
)

role_router = APIRouter()


@role_router.post('/roles')
async def create_role(
    role_data: CreateRoleDTO,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.create_roles_with_permissions(role_data)


@role_router.post('/permission')
async def create_permission(
    permission_data: PermissionItemDTO,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.create_perms_with_permissions(permission_data)


@role_router.delete('/roles')
async def delete_role_by_name(
    role_name: str,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
) -> dict:
    return await auth_service.delete_role_by_name(role_name)


@role_router.get('/')
async def get_roles(
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)]
):
    return await auth_service.get_roles()


@role_router.get('/permission')
async def get_pemissions(
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)]
):
    return await auth_service.get_permissions()


@role_router.post('/update')
async def assign_perm_to_role(
    permission_id: int,
    role_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):

    return await auth_service.assign_permission_to_role(
        role_id=role_id, perm_id=permission_id
    )


@role_router.delete('/{id}')
async def delete_role_by_id(
    role_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
) -> dict:

    return await auth_service.delete_role_by_id(role_id=role_id)


@role_router.delete('/permission/{permission_id}')
async def delete_permission_by_id(
    role_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    return await auth_service.delete_permission_by_id(permission_id=role_id)


@role_router.post('/{user_id}/update')
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


@role_router.get('/{user_id}/list')
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


@role_router.get('/{role_id}')
async def get_role_by_id(
    role_id: int,
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    """
    Obtém uma função (role) pelo seu ID.

    Args:
        role_id (int): O ID da função (role) a ser recuperada.
        auth_service (Annotated[AuthServiceProtocol, Depends]):
            Serviço de autenticação responsável pelas operações relacionadas
            a funções.

    Returns:
        Role: Objeto da função correspondente ao ID fornecido.

    Raises:
        HTTPException: Se a função não for encontrada ou ocorrer um erro durante a busca
    """
    return await auth_service.return_role_by_id(role_id)


# TODO  TESTES Endpoint para listar todas as roles
# TODO TESTES Endpoint para associar role a permissão

# // TODO TESTE Endpoint para criar permission
# // TODO  TESTE Endpoint para deletar permission
# TODO  TESTE Endpoint para listar todas as permissions
# TODO Validar Get Roles List User ID
