#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.admin.schema.operation_log import (
    OperationLogDeleteParams,
    OperationLogDetail,
    OperationLogListQueryParams,
)
from backend.app.admin.service.operation_log import operation_log_service
from backend.common.enum.custom import StatusEnum
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.base import ResponseModel, ResponseSchemaModel, response_base
from backend.common.response.code import CustomResponse
from backend.common.security.jwt import DependsJWTAuth

router = APIRouter()


@router.get('/list', summary='分页获取操作日志列表', dependencies=[DependsJWTAuth, DependsPagination])
async def get_operation_log_list(
    username: Annotated[str | None, Query(description='操作用户')] = None,
    moudle: Annotated[str | None, Query(description='操作模块')] = None,
    path: Annotated[str | None, Query(description='请求路径')] = None,
    method: Annotated[str | None, Query(description='请求方式')] = None,
    code: Annotated[str | None, Query(description='操作状态码')] = None,
    ip: Annotated[str | None, Query(description='IP地址')] = None,
    country: Annotated[str | None, Query(description='国家')] = None,
    region: Annotated[str | None, Query(description='地区')] = None,
    city: Annotated[str | None, Query(description='城市')] = None,
    status: Annotated[StatusEnum | None, Query(description='操作状态（0异常 1正常）')] = None,
) -> ResponseSchemaModel[PageData[OperationLogDetail]]:
    """获取操作日志分页列表"""
    params = OperationLogListQueryParams(
        username=username,
        moudle=moudle,
        path=path,
        method=method.upper() if method else None,
        code=code,
        ip=ip,
        country=country,
        region=region,
        city=city,
        status=status,
    )
    data = await operation_log_service.get_list(params=params)
    return response_base.success_with_schema(data=PageData[OperationLogDetail](**data))


@router.delete('/delete', summary='批量删除操作日志', dependencies=[DependsJWTAuth])
async def delete_operation_logs(params: OperationLogDeleteParams) -> ResponseModel:
    """批量删除操作日志"""
    count = await operation_log_service.delete(params=params)
    if count > 0:
        return response_base.success(res=CustomResponse(code=200, msg=f'成功删除 {count} 条操作日志'))
    return response_base.fail(res=CustomResponse(code=400, msg='删除失败，未找到相关记录'))


@router.delete('/clear', summary='清空所有操作日志', dependencies=[DependsJWTAuth])
async def clear_all_operation_logs() -> ResponseModel:
    """清空所有操作日志"""
    await operation_log_service.delete_all()
    return response_base.success(res=CustomResponse(code=200, msg='成功清空所有操作日志'))
