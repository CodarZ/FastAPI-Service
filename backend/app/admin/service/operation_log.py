#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.app.admin.crud.operation_log import operation_log_crud
from backend.app.admin.schema.operation_log import (
    OperationLogCreateParams,
    OperationLogDeleteParams,
    OperationLogListQueryParams,
)
from backend.database.postgresql import async_db_session


class OperationLogService:
    """请求操作日志服务类"""

    @staticmethod
    async def get_list(*, params: OperationLogListQueryParams):
        """获取 分页列表"""
        async with async_db_session.begin() as db:
            stmt = await operation_log_crud.get_list_select(params)
            from backend.common.pagination import paging_data

            return await paging_data(db, stmt)

    @staticmethod
    async def create(*, params: OperationLogCreateParams) -> None:
        """创建"""
        async with async_db_session.begin() as db:
            await operation_log_crud.create(db, params)

    @staticmethod
    async def bulk_create(*, objs: list[OperationLogCreateParams]) -> None:
        """批量创建"""
        async with async_db_session.begin() as db:
            await operation_log_crud.bulk_create(db, objs)

    @staticmethod
    async def delete(*, params: OperationLogDeleteParams) -> int:
        """批量删除"""
        async with async_db_session.begin() as db:
            count = await operation_log_crud.delete(db, params.pks)
            return count

    @staticmethod
    async def delete_all() -> None:
        """清空所有"""
        async with async_db_session.begin() as db:
            await operation_log_crud.delete_all(db)


operation_log_service: OperationLogService = OperationLogService()
