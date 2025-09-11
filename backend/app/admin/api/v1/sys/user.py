#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from backend.app.admin.schema.user import UserRegisterParams
from backend.app.admin.service.user import user_service
from backend.common.response.base import ResponseModel, response_base
from backend.common.response.code import CustomResponse

router = APIRouter()


@router.post('/register', summary='注册用户')
async def user_register(params: UserRegisterParams) -> ResponseModel:
    await user_service.register(params=params)
    return response_base.success(res=CustomResponse(code=200, msg='注册成功'))
