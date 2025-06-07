from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_presentation.auth_router import auth_router
from api_presentation.lifespan import lifespan
from domain_entity.exceptions import AppException

app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'code': exc.code, 'message': exc.message},
    )


app.include_router(router=auth_router, prefix='/auth', tags=['auth'])
