#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from backend.app.admin.schema.user import UserCreateEmail
from backend.app.admin.service.user import user_service
from backend.common.response.base import ResponseModel, response_base

router = APIRouter()


@router.post('/register', summary='注册用户')
async def register_user(obj: UserCreateEmail) -> ResponseModel:
    await user_service.register(obj=obj)
    return response_base.success()
