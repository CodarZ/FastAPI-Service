from typing import TYPE_CHECKING

from backend.app.admin.crud import sys_operation_log_crud
from backend.app.admin.schema.sys_operation_log import (
    SysOperationLogBatchDelete,
    SysOperationLogClear,
    SysOperationLogCreate,
    SysOperationLogDetail,
    SysOperationLogFilter,
    SysOperationLogListItem,
    SysOperationLogModuleStats,
    SysOperationLogStatistics,
    SysOperationLogTrend,
)
from backend.common.exception import errors
from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SysOperationLogService:
    """操作日志服务类"""

    @staticmethod
    async def _get_log_or_404(db: 'AsyncSession', pk: int):
        """获取操作日志, 不存在则抛出 NotFoundError"""
        log = await sys_operation_log_crud.get(db, pk)
        if not log:
            raise errors.NotFoundError(msg='操作日志不存在')
        return log

    @staticmethod
    async def get_log_detail(*, db: 'AsyncSession', pk: int) -> SysOperationLogDetail:
        """获取操作日志详情"""
        log = await SysOperationLogService._get_log_or_404(db, pk)
        return SysOperationLogDetail.model_validate(log)

    @staticmethod
    async def get_log_by_trace_id(*, db: 'AsyncSession', trace_id: str) -> SysOperationLogDetail:
        """根据跟踪ID获取操作日志"""
        log = await sys_operation_log_crud.get_by_trace_id(db, trace_id)
        if not log:
            raise errors.NotFoundError(msg='操作日志不存在')
        return SysOperationLogDetail.model_validate(log)

    @staticmethod
    async def get_list(*, params: SysOperationLogFilter) -> list[SysOperationLogListItem]:
        """获取操作日志列表（支持多条件过滤）"""
        async with async_session.begin() as db:
            stmt = await sys_operation_log_crud.get_list_select(params)
            result = await db.scalars(stmt)
            logs = result.all()
            # 在 session 内完成序列化, 避免 DetachedInstanceError
            return [SysOperationLogListItem.model_validate(log) for log in logs]

    @staticmethod
    async def create(*, db: 'AsyncSession', params: SysOperationLogCreate):
        """创建操作日志（内部方法, 供中间件调用）

        注意：
            - 此方法仅供内部使用, 不对外暴露 API
            - 通常由访问日志中间件自动调用
            - 使用 DataClassBase 模式, 直接通过构造函数创建
        """
        await sys_operation_log_crud.create(db, params)

    @staticmethod
    async def batch_create(*, db: 'AsyncSession', params_list: list[SysOperationLogCreate]) -> list[int]:
        """批量创建操作日志"""
        if not params_list:
            return []

        logs = await sys_operation_log_crud.batch_create(db, params_list)
        return [log.id for log in logs]

    @staticmethod
    async def delete(*, db: 'AsyncSession', pk: int) -> int:
        """删除操作日志"""
        await SysOperationLogService._get_log_or_404(db, pk)
        return await sys_operation_log_crud.delete(db, pk)

    @staticmethod
    async def batch_delete(*, db: 'AsyncSession', params: SysOperationLogBatchDelete) -> dict[str, int]:
        """批量删除操作日志

        Returns:
            - deleted_count: 实际删除的数量
        """
        log_ids = params.log_ids
        deleted_count = await sys_operation_log_crud.batch_delete(db, log_ids)

        return {
            'deleted_count': deleted_count,
        }

    @staticmethod
    async def clear(*, db: 'AsyncSession', params: SysOperationLogClear) -> dict[str, int]:
        """清理操作日志（按条件批量删除）

        常见场景：
            - 清理指定时间之前的日志
            - 清理异常状态的日志
            - 清理特定模块的日志

        Returns:
            - cleared_count: 实际清理的数量
        """
        cleared_count = await sys_operation_log_crud.clear_by_conditions(db, params)

        return {
            'cleared_count': cleared_count,
        }

    @staticmethod
    async def get_statistics(*, params: SysOperationLogFilter) -> SysOperationLogStatistics:
        """获取操作日志统计信息

        统计内容：
            - 总数量
            - 成功/异常数量
            - 平均/最大/最小耗时
        """
        async with async_session.begin() as db:
            stats = await sys_operation_log_crud.get_statistics(db, params)
            if not stats:
                # 返回空统计数据
                return SysOperationLogStatistics(
                    total_count=0,
                    success_count=0,
                    error_count=0,
                    avg_cost_time=0.0,
                    max_cost_time=0.0,
                    min_cost_time=0.0,
                )
            return SysOperationLogStatistics(**stats)

    @staticmethod
    async def get_trend(*, params: SysOperationLogFilter, days: int = 7) -> list[SysOperationLogTrend]:
        """获取操作日志趋势（按日期统计）

        Args:
            params: 查询条件
            days: 统计天数, 默认最近7天

        Returns:
            按日期分组的趋势数据列表
        """
        async with async_session.begin() as db:
            trends = await sys_operation_log_crud.get_trend_by_date(db, params, days)
            return [SysOperationLogTrend(**trend) for trend in trends]

    @staticmethod
    async def get_module_statistics(
        *, params: SysOperationLogFilter, limit: int = 10
    ) -> list[SysOperationLogModuleStats]:
        """获取操作日志模块统计（按模块分组）

        Args:
            params: 查询条件
            limit: 返回数量限制, 默认前10个

        Returns:
            按调用次数降序排列的模块统计列表
        """
        async with async_session.begin() as db:
            stats = await sys_operation_log_crud.get_module_statistics(db, params, limit)
            return [SysOperationLogModuleStats(**stat) for stat in stats]


sys_operation_log_service = SysOperationLogService()
