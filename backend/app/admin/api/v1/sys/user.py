#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Path, Query
from pydantic import EmailStr

from backend.app.admin.schema.user import (
    UserDetail,
    UserDetailWithSocials,
    UserListQueryParams,
    UserRegisterParams,
    UserUpdateParams,
)
from backend.app.admin.service.user import user_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.base import ResponseModel, ResponseSchemaModel, response_base
from backend.common.response.code import CustomResponse
from backend.common.security.jwt import DependsJWTAuth

router = APIRouter()


@router.post('/register', summary='注册用户')
async def user_register(params: UserRegisterParams) -> ResponseModel:
    await user_service.register(params=params)
    return response_base.success(res=CustomResponse(code=200, msg='注册成功'))


@router.get('/list', summary='分页获取用户列表', dependencies=[DependsJWTAuth, DependsPagination])
async def get_user_list(
    username: Annotated[str | None, Query(description='用户名')] = None,
    nickname: Annotated[str | None, Query(description='昵称')] = None,
    email: Annotated[EmailStr | None, Query(description='邮箱')] = None,
    phone: Annotated[str | None, Query(description='手机号')] = None,
    gender: Annotated[int | None, Query(description='性别(0女 1男 3未知)')] = None,
    status: Annotated[int | None, Query(description='用户账号状态(0停用 1正常)')] = None,
    is_staff: Annotated[bool | None, Query(description='是否可以登录后台管理')] = None,
    is_verified: Annotated[bool | None, Query(description='是否实名认证')] = None,
) -> ResponseSchemaModel[PageData[UserDetail]]:
    # 转换为原有的参数格式
    query_params = UserListQueryParams(
        username=username,
        nickname=nickname,
        email=email,
        phone=phone,
        gender=gender,
        status=status,
        is_staff=is_staff,
        is_verified=is_verified,
    )
    data = await user_service.get_list(params=query_params)
    return response_base.success_with_schema(data=PageData[UserDetail](**data))


@router.get('/{pk}', summary='获取用户信息', dependencies=[DependsJWTAuth])
async def get_user_detail(pk: Annotated[int, Path(description='用户 ID')]) -> ResponseSchemaModel[UserDetail]:
    user = await user_service.get_userinfo(pk=pk)
    user_detail = UserDetail.model_validate(user)
    return response_base.success_with_schema(data=user_detail)


@router.get('/{pk}/social', summary='获取用户信息（包含第三方授权信息）', dependencies=[DependsJWTAuth])
async def get_user_detail_with_social(
    pk: Annotated[int, Path(description='用户 ID')],
) -> ResponseSchemaModel[UserDetailWithSocials]:
    user_detail = await user_service.get_userinfo_with_socials(pk=pk)
    return response_base.success_with_schema(data=user_detail)


@router.delete('/{pk}', summary='删除用户', dependencies=[DependsJWTAuth])
async def delte_user(pk: Annotated[int, Path(description='用户 ID')]) -> ResponseModel:
    count = await user_service.delete(pk=pk)
    if count > 0:
        return response_base.success(res=CustomResponse(code=200, msg='删除成功'))
    return response_base.fail(res=CustomResponse(code=400, msg='删除失败'))


@router.put('/{pk}', summary='更新用户信息', dependencies=[DependsJWTAuth])
async def update_user(pk: Annotated[int, Path(description='用户 ID')], params: UserUpdateParams) -> ResponseModel:
    count = await user_service.update(pk=pk, params=params)
    if count > 0:
        return response_base.success(res=CustomResponse(code=200, msg='修改用户信息成功'))
    return response_base.fail(res=CustomResponse(code=400, msg='修改用户信息失败'))
