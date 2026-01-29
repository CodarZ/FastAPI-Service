from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Response
from fastapi.security import HTTPBasicCredentials

from backend.app.admin.schema.auth import LoginRequest, LoginResponse, SwaggerLoginResponse
from backend.app.admin.service.auth import auth_service
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.database.postgresql import CurrentSessionTransaction

router = APIRouter()


@router.post('/login', summary='用户登录', response_model=ResponseSchemaModel[LoginResponse])
async def login(
    db: CurrentSessionTransaction,
    params: LoginRequest,
    response: Response,
    background_tasks: BackgroundTasks,
):
    """用户登录"""
    data = await auth_service.login(
        db=db,
        params=params,
        response=response,
        background_tasks=background_tasks,
    )
    return response_base.success(data=data)


@router.post(
    '/login/swagger',
    summary='swagger 调试专用',
    description='用于快捷获取 token 进行 swagger 认证',
    response_model=ResponseSchemaModel[SwaggerLoginResponse],
)
async def login_swagger(
    db: CurrentSessionTransaction,
    params: Annotated[HTTPBasicCredentials, Depends()],
):
    token, user = await auth_service.login_swagger(db=db, params=params)
    data = SwaggerLoginResponse(access_token=token, token_type='Bearer', user=user)
    return response_base.success(data=data)
