#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from sqlalchemy import Select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model.operation_log import OperationLog
from backend.app.admin.schema.operation_log import OperationLogCreateParams, OperationLogListQueryParams


class OperationLogCRUD(CRUDPlus[OperationLog]):
    """请求操作日志数据库操作类"""

    async def create(self, db: AsyncSession, params: OperationLogCreateParams) -> None:
        """创建一个"""
        await self.create_model(db, params)

    async def bulk_create(self, db: AsyncSession, objs: list[OperationLogCreateParams]) -> None:
        """批量创建"""
        await self.create_models(db, objs)

    async def get(self, db: AsyncSession, pk: int):
        """根据 pk 获取详情"""
        return await self.select_model(db, pk)

    async def get_by_column(self, db: AsyncSession, column: str, value: str):
        """根据指定列名和值获取 详情"""
        return await self.select_model_by_column(db, **{column: value})  # type: ignore

    async def get_list_select(self, params: OperationLogListQueryParams) -> Select:
        """获取 列表"""
        filters = {}

        # 模糊查询字段
        for field in ['username', 'moudle', 'path', 'ip', 'country', 'region', 'city']:
            value = getattr(params, field, None)
            if value:
                filters[f'{field}__like'] = f'%{value}%'

        # 精确匹配字段
        for field in ['method', 'code', 'status']:
            value = getattr(params, field, None)
            if value is not None:
                filters[field] = value

        return await self.select_order('id', 'desc', **filters)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """批量删除"""
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    @staticmethod
    async def delete_all(db: AsyncSession) -> None:
        """删除所有日志"""
        await db.execute(sa_delete(OperationLog))


operation_log_crud = OperationLogCRUD(OperationLog)
