from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.admin.schema.login_log import (
    LoginLogDeleteParams,
    LoginLogDetail,
    LoginLogListQueryParams,
)
from backend.app.admin.service.login_log import login_log_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.request.query import create_dependency
from backend.common.response.base import ResponseModel, ResponseSchemaModel, response_base
from backend.common.response.code import CustomResponse
from backend.common.security.jwt import DependsJWTAuth

router = APIRouter()


@router.get('/list', summary='分页获取登录日志列表', dependencies=[DependsJWTAuth, DependsPagination])
async def get_login_log_list(
    params: Annotated[LoginLogListQueryParams, Depends(create_dependency(LoginLogListQueryParams))],
) -> ResponseSchemaModel[PageData[LoginLogDetail]]:
    """获取登录日志分页列表"""
    data = await login_log_service.get_list(params=params)
    return response_base.success_with_schema(data=PageData[LoginLogDetail](**data))


@router.delete('/delete', summary='批量删除登录日志', dependencies=[DependsJWTAuth])
async def delete_login_logs(params: LoginLogDeleteParams) -> ResponseModel:
    """批量删除登录日志"""
    count = await login_log_service.delete(params=params)
    if count > 0:
        return response_base.success(res=CustomResponse(code=200, msg=f'成功删除 {count} 条登录日志'))
    return response_base.fail(res=CustomResponse(code=400, msg='删除失败，未找到相关记录'))


@router.delete('/clear', summary='清空所有登录日志', dependencies=[DependsJWTAuth])
async def clear_all_login_logs() -> ResponseModel:
    """清空所有登录日志"""
    await login_log_service.delete_all()
    return response_base.success(res=CustomResponse(code=200, msg='成功清空所有登录日志'))
