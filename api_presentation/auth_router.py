from fastapi import APIRouter, Depends
from domain_entity.schemas import UserCreateDTO,UserFromDBDTO
from application_service.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from api_presentation.dependencies import get_session


router = APIRouter()

@router.post("/create-user",response_model=UserFromDBDTO)
async def auth_route_create_user(user_data:UserCreateDTO,db: AsyncSession = Depends(get_session)):
    pass
