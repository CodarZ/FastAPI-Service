#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.admin.schema.user import UserDetail, UserRegisterParams
from backend.app.admin.service.user import user_service
from backend.common.response.base import ResponseModel, response_base
from backend.common.response.code import CustomResponse

router = APIRouter()


@router.post('/register', summary='注册用户')
async def user_register(params: UserRegisterParams) -> ResponseModel:
    await user_service.register(params=params)
    return response_base.success(res=CustomResponse(code=200, msg='注册成功'), data={'hello', '欢迎来到我的世界'})


@router.get('/{pk}', summary='获取用户信息')
async def get_userinfo(pk: Annotated[int, Path(description='用户 ID')]):
    user = await user_service.get_userinfo(pk=pk)
    user_detail = UserDetail.model_validate(user)
    return response_base.success(data=user_detail)
