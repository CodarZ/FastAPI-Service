#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials

from backend.app.admin.schema.token import SwaggerToken
from backend.app.admin.service.auth import auth_service
from backend.common.response.base import ResponseModel

router = APIRouter()


@router.post('/login/swagger', summary='swagger 调试', description='用于快捷获取 token 进行 swagger 认证')
async def swagger_login(obj: Annotated[HTTPBasicCredentials, Depends()]):
    token, user = await auth_service.swagger_login(obj=obj)
    return ResponseModel(data=SwaggerToken(access_token=token, token_type='Bearer', user=user))
