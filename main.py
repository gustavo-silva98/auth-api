from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_presentation.auth_router import auth_router
from api_presentation.lifespan import lifespan
from api_presentation.user_router import user_router
from domain_entity.exceptions import AppException

app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'code': exc.code, 'message': exc.message},
        headers=exc.headers,
    )


app.include_router(router=auth_router, prefix='/auth', tags=['auth'])
app.include_router(router=user_router, prefix='/users', tags=['users'])


@app.get('/health')
async def health_check():
    return {'status': 'ok'}


"""
Isso aqui não deveria ser mais compexo?

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

e se o health não estiver ok? 
E onde eu cadastro as variáveis de ambiente?
"""
