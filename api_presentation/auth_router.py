from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_presentation.dependencies import get_auth_service, get_session
from application_service.auth_service import AuthServiceProtocol
from domain_entity.schemas import UserCreateDTO, UserFromDBDTO

router = APIRouter()


@router.post('/create-user', response_model=UserFromDBDTO)
async def auth_route_create_user(
    user_data: UserCreateDTO,
    db: Annotated[AsyncSession, Depends(get_session)],
    auth_service: Annotated[AuthServiceProtocol, Depends(get_auth_service)],
):
    pass
