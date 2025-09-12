#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.admin.schema.user import UserDetail, UserListQueryParams, UserRegisterParams, UserUpdateParams
from backend.app.admin.service.user import user_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.base import ResponseModel, ResponseSchemaModel, response_base
from backend.common.response.code import CustomResponse

router = APIRouter()


@router.post('/register', summary='注册用户')
async def user_register(params: UserRegisterParams) -> ResponseModel:
    await user_service.register(params=params)
    return response_base.success(res=CustomResponse(code=200, msg='注册成功'))


@router.get('/list', summary='分页获取用户列表', dependencies=[DependsPagination])
async def get_user_list(
    params: UserListQueryParams = Depends(),
) -> ResponseSchemaModel[PageData[UserDetail]]:
    data = await user_service.get_list(params=params)
    # TODO 类型问题
    return response_base.success_with_schema(data=PageData[UserDetail](**data))


@router.get('/{pk}', summary='获取用户信息')
async def get_user_detail(pk: Annotated[int, Path(description='用户 ID')]) -> ResponseSchemaModel[UserDetail]:
    user = await user_service.get_userinfo(pk=pk)
    user_detail = UserDetail.model_validate(user)
    return response_base.success_with_schema(data=user_detail)


@router.delete('/{pk}', summary='删除用户')
async def delte_user(pk: Annotated[int, Path(description='用户 ID')]) -> ResponseModel:
    count = await user_service.delete(pk=pk)
    if count > 0:
        return response_base.success(res=CustomResponse(code=200, msg='删除成功'))
    return response_base.fail(res=CustomResponse(code=400, msg='删除失败'))


@router.put('/{pk}', summary='更新用户信息')
async def update_user(pk: Annotated[int, Path(description='用户 ID')], params: UserUpdateParams) -> ResponseModel:
    count = await user_service.update(pk=pk, params=params)
    if count > 0:
        return response_base.success(res=CustomResponse(code=200, msg='修改用户信息成功'))
    return response_base.fail(res=CustomResponse(code=400, msg='修改用户信息失败'))
