#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi.security import HTTPBasicCredentials
from fastapi_limiter.depends import RateLimiter

from backend.app.admin.schema.token import AuthLoginParams, AuthLoginToken, SwaggerToken
from backend.app.admin.schema.user import UserDetail
from backend.app.admin.service.auth import auth_service
from backend.common.response.base import ResponseSchemaModel, response_base

router = APIRouter()


@router.post('/swagger', summary='swagger 调试专用', description='用于快捷获取 token 进行 swagger 认证')
async def login_swagger(params: Annotated[HTTPBasicCredentials, Depends()]) -> ResponseSchemaModel[SwaggerToken]:
    token, user = await auth_service.swagger_login(params=params)
    user_detail = UserDetail.model_validate(user)
    data = SwaggerToken(access_token=token, user=user_detail)
    return response_base.success_with_schema(data=data)


@router.post(
    '/login',
    summary='用户登录',
    description='json 格式登录, 仅支持在第三方api工具调试, 例如: postman',
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
)
async def login(
    request: Request,
    response: Response,
    params: AuthLoginParams,
    background_tasks: BackgroundTasks,
) -> ResponseSchemaModel[AuthLoginToken]:
    data = await auth_service.login(
        request=request, response=response, params=params, background_tasks=background_tasks
    )
    return response_base.success_with_schema(data=data)
