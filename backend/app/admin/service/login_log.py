#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from backend.app.admin.crud.login_log import login_log_crud
from backend.app.admin.schema.login_log import LoginLogCreateParams, LoginLogDeleteParams, LoginLogListQueryParams
from backend.common.pagination import paging_data
from backend.database.postgresql import async_db_session


class LoginLogService:
    """登录日志服务类"""

    @staticmethod
    async def get_list(*, params: LoginLogListQueryParams):
        """获取分页列表"""
        async with async_db_session.begin() as db:
            stmt = await login_log_crud.get_list_select(params)

            return await paging_data(db, stmt)

    @staticmethod
    async def create(*, params: LoginLogCreateParams) -> None:
        """创建"""
        async with async_db_session.begin() as db:
            await login_log_crud.create(db, params)

    @staticmethod
    async def bulk_create(*, objs: list[LoginLogCreateParams]) -> None:
        """批量创建"""
        async with async_db_session.begin() as db:
            await login_log_crud.bulk_create(db, objs)

    @staticmethod
    async def delete(*, params: LoginLogDeleteParams) -> int:
        """批量删除"""
        async with async_db_session.begin() as db:
            count = await login_log_crud.delete(db, params.pks)
            return count

    @staticmethod
    async def delete_all() -> None:
        """清空所有"""
        async with async_db_session.begin() as db:
            await login_log_crud.delete_all(db)


login_log_service: LoginLogService = LoginLogService()
