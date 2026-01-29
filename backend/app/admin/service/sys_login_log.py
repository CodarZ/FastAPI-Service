from typing import TYPE_CHECKING

from backend.app.admin.crud import sys_login_log_crud
from backend.app.admin.schema.sys_login_log import (
    SysLoginLogBatchDelete,
    SysLoginLogBatchDeleteResult,
    SysLoginLogClear,
    SysLoginLogClearResult,
    SysLoginLogCreate,
    SysLoginLogDetail,
    SysLoginLogFilter,
    SysLoginLogListItem,
    SysLoginLogStatistics,
)
from backend.common.exception import errors
from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.model import SysLoginLog


class SysLoginLogService:
    """登录日志服务类"""

    @staticmethod
    async def _get_log_or_404(db: 'AsyncSession', pk: int) -> 'SysLoginLog':
        """获取登录日志, 不存在则抛出 NotFoundError"""
        log = await sys_login_log_crud.get(db, pk)
        if not log:
            raise errors.NotFoundError(msg='登录日志不存在')
        return log

    @staticmethod
    async def get_log_detail(*, db: 'AsyncSession', pk: int) -> SysLoginLogDetail:
        """获取登录日志详情"""
        log = await SysLoginLogService._get_log_or_404(db, pk)
        return SysLoginLogDetail.model_validate(log)

    @staticmethod
    async def get_list(*, params: SysLoginLogFilter) -> list[SysLoginLogListItem]:
        """获取登录日志列表（支持多条件过滤）"""
        async with async_session.begin() as db:
            stmt = await sys_login_log_crud.get_list_select(params)
            result = await db.scalars(stmt)
            logs = result.all()
            # 在 session 内完成序列化, 避免 DetachedInstanceError
            return [SysLoginLogListItem.model_validate(log) for log in logs]

    @staticmethod
    async def create(*, params: SysLoginLogCreate):
        """创建登录日志（内部方法, 供中间件调用）

        注意：
            - 此方法仅供内部使用, 不对外暴露 API
            - 通常由认证中间件/登录接口自动调用
            - 使用 DataClassBase 模式, 直接传入已构造的实例
        """
        async with async_session.begin() as db:
            await sys_login_log_crud.create(db, params)

    @staticmethod
    async def batch_create(*, db: 'AsyncSession', params_list: list[SysLoginLogCreate]) -> list[int]:
        """批量创建登录日志"""
        if not params_list:
            return []

        created_logs = await sys_login_log_crud.batch_create(db, params_list)
        return [log.id for log in created_logs]

    @staticmethod
    async def delete(*, db: 'AsyncSession', pk: int) -> int:
        """删除登录日志"""
        await SysLoginLogService._get_log_or_404(db, pk)
        return await sys_login_log_crud.delete(db, pk)

    @staticmethod
    async def batch_delete(*, db: 'AsyncSession', params: SysLoginLogBatchDelete) -> SysLoginLogBatchDeleteResult:
        """批量删除登录日志

        Returns:
            - deleted_count: 实际删除的数量
        """
        log_ids = params.log_ids
        deleted_count = await sys_login_log_crud.batch_delete(db, log_ids)

        return SysLoginLogBatchDeleteResult(deleted_count=deleted_count)

    @staticmethod
    async def clear(*, db: 'AsyncSession', params: SysLoginLogClear) -> SysLoginLogClearResult:
        """清理登录日志（按条件批量删除）

        常见场景：
            - 清理指定时间之前的日志
            - 清理异常状态的日志
            - 定期清理历史日志

        Returns:
            - cleared_count: 实际清理的数量
        """
        cleared_count = await sys_login_log_crud.clear_by_conditions(db, params)

        return SysLoginLogClearResult(cleared_count=cleared_count)

    @staticmethod
    async def get_statistics(*, params: SysLoginLogFilter) -> SysLoginLogStatistics:
        """获取登录日志统计信息

        统计内容：
            - 总数量
            - 成功/异常数量
        """
        async with async_session.begin() as db:
            return await sys_login_log_crud.get_statistics(db, params)


sys_login_log_service = SysLoginLogService()
