#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends

from backend.app.admin.schema.operation_log import (
    OperationLogDeleteParams,
    OperationLogDetail,
    OperationLogListQueryParams,
)
from backend.app.admin.service.operation_log import operation_log_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.base import ResponseModel, ResponseSchemaModel, response_base
from backend.common.response.code import CustomResponse
from backend.common.security.jwt import DependsJWTAuth

router = APIRouter()


@router.get('/list', summary='分页获取操作日志列表', dependencies=[DependsPagination])
async def get_operation_log_list(
    params: OperationLogListQueryParams = Depends(),
) -> ResponseSchemaModel[PageData[OperationLogDetail]]:
    """获取操作日志分页列表"""
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
