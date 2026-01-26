from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import CursorResult, Select, case, delete, func, select

from backend.app.admin.model import SysOperationLog

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema.sys_operation_log import (
        SysOperationLogClear,
        SysOperationLogCreate,
        SysOperationLogFilter,
    )


class CRUDSysOperationLog:
    """操作日志 CRUD

    操作日志是通过中间件自动记录的，主要提供查询、删除等功能
    不提供对外的创建接口，但提供内部创建方法供中间件使用
    """

    def __init__(self) -> None:
        self.model = SysOperationLog

    async def get(self, db: 'AsyncSession', pk: int) -> SysOperationLog | None:
        """根据主键获取操作日志详情"""
        stmt = select(SysOperationLog).where(SysOperationLog.id == pk)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_trace_id(self, db: 'AsyncSession', trace_id: str) -> SysOperationLog | None:
        """根据跟踪ID获取操作日志"""
        stmt = select(SysOperationLog).where(SysOperationLog.trace_id == trace_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list_select(self, params: 'SysOperationLogFilter') -> Select[tuple[SysOperationLog]]:
        """获取操作日志列表的 Select 语句"""
        conditions: list = []

        # 模糊查询字段
        for field in ['username', 'module', 'path', 'os', 'browser', 'device', 'country', 'region', 'city']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysOperationLog, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 精确查询字段
        for field in ['trace_id', 'method', 'code', 'status', 'ip']:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysOperationLog, field)
                conditions.append(field_attr == value)

        # 范围查询（min/max 后缀）
        for field in ['cost_time']:
            field_attr = getattr(SysOperationLog, field)
            min_value = getattr(params, f'{field}_min', None)
            if min_value is not None:
                conditions.append(field_attr >= min_value)
            max_value = getattr(params, f'{field}_max', None)
            if max_value is not None:
                conditions.append(field_attr <= max_value)

        # 时间范围查询（start/end 后缀）
        for field in ['operated_time']:
            field_attr = getattr(SysOperationLog, field)
            start_value = getattr(params, f'{field}_start', None)
            if start_value is not None:
                conditions.append(field_attr >= start_value)
            end_value = getattr(params, f'{field}_end', None)
            if end_value is not None:
                conditions.append(field_attr <= end_value)

        # 构建查询语句, 按操作时间降序排列（最新的在前）
        return select(SysOperationLog).where(*conditions).order_by(SysOperationLog.operated_time.desc())

    async def create(self, db: 'AsyncSession', params: 'SysOperationLogCreate') -> SysOperationLog:
        """创建操作日志（内部方法，由中间件调用）"""
        log = SysOperationLog(**params.model_dump())
        db.add(log)
        await db.flush()
        return log

    async def batch_create(
        self, db: 'AsyncSession', params_list: list['SysOperationLogCreate']
    ) -> list[SysOperationLog]:
        """批量创建操作日志（内部方法）"""
        if not params_list:
            return []

        logs = [SysOperationLog(**params.model_dump()) for params in params_list]
        db.add_all(logs)
        await db.flush()
        return logs

    async def delete(self, db: 'AsyncSession', pk: int) -> int:
        """删除操作日志"""
        stmt = delete(SysOperationLog).where(SysOperationLog.id == pk)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_delete(self, db: 'AsyncSession', log_ids: list[int]) -> int:
        """批量删除操作日志"""
        if not log_ids:
            return 0

        stmt = delete(SysOperationLog).where(SysOperationLog.id.in_(log_ids))
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def clear_by_conditions(self, db: 'AsyncSession', params: 'SysOperationLogClear') -> int:
        """根据条件清理操作日志"""
        conditions: list = []

        # 精确查询字段
        for field in ['status']:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysOperationLog, field)
                conditions.append(field_attr == value)

        # 模糊查询字段
        for field in ['module']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysOperationLog, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 时间范围：清理指定时间之前的日志
        if params.before_time is not None:
            conditions.append(SysOperationLog.operated_time < params.before_time)

        if not conditions:
            return 0

        stmt = delete(SysOperationLog).where(*conditions)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def get_statistics(self, db: 'AsyncSession', params: 'SysOperationLogFilter') -> dict[str, Any] | None:
        """获取操作日志统计数据"""
        # 复用查询条件
        list_stmt = await self.get_list_select(params)
        base_conditions = list_stmt.whereclause

        # 构建统计查询
        stmt = select(
            func.count(SysOperationLog.id).label('total_count'),
            func.sum(case((SysOperationLog.status == 1, 1), else_=0)).label('success_count'),
            func.sum(case((SysOperationLog.status == 0, 1), else_=0)).label('error_count'),
            func.avg(SysOperationLog.cost_time).label('avg_cost_time'),
            func.max(SysOperationLog.cost_time).label('max_cost_time'),
            func.min(SysOperationLog.cost_time).label('min_cost_time'),
        )

        if base_conditions is not None:
            stmt = stmt.where(base_conditions)

        result = await db.execute(stmt)
        row = result.one_or_none()

        if not row:
            return None

        return {
            'total_count': row.total_count or 0,
            'success_count': row.success_count or 0,
            'error_count': row.error_count or 0,
            'avg_cost_time': round(row.avg_cost_time or 0, 2),
            'max_cost_time': row.max_cost_time or 0,
            'min_cost_time': row.min_cost_time or 0,
        }

    async def get_trend_by_date(
        self, db: 'AsyncSession', params: 'SysOperationLogFilter', days: int = 7
    ) -> list[dict[str, Any]]:
        """获取操作日志趋势（按日期统计）"""
        from sqlalchemy import Date, cast as sql_cast

        # 复用查询条件
        list_stmt = await self.get_list_select(params)
        base_conditions = list_stmt.whereclause

        # 构建按日期分组的统计查询
        stmt = (
            select(
                sql_cast(SysOperationLog.operated_time, Date).label('date'),
                func.count(SysOperationLog.id).label('total_count'),
                func.sum(case((SysOperationLog.status == 1, 1), else_=0)).label('success_count'),
                func.sum(case((SysOperationLog.status == 0, 1), else_=0)).label('error_count'),
                func.avg(SysOperationLog.cost_time).label('avg_cost_time'),
            )
            .group_by(sql_cast(SysOperationLog.operated_time, Date))
            .order_by(sql_cast(SysOperationLog.operated_time, Date).desc())
            .limit(days)
        )

        if base_conditions is not None:
            stmt = stmt.where(base_conditions)

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                'date': str(row.date),
                'total_count': row.total_count or 0,
                'success_count': row.success_count or 0,
                'error_count': row.error_count or 0,
                'avg_cost_time': round(row.avg_cost_time or 0, 2),
            }
            for row in rows
        ]

    async def get_module_statistics(
        self, db: 'AsyncSession', params: 'SysOperationLogFilter', limit: int = 10
    ) -> list[dict[str, Any]]:
        """获取操作日志模块统计（按模块分组）"""
        # 复用查询条件
        list_stmt = await self.get_list_select(params)
        base_conditions = list_stmt.whereclause

        # 构建按模块分组的统计查询
        stmt = (
            select(
                SysOperationLog.module,
                func.count(SysOperationLog.id).label('total_count'),
                (
                    func.sum(case((SysOperationLog.status == 1, 1), else_=0)) * 100.0 / func.count(SysOperationLog.id)
                ).label('success_rate'),
                func.avg(SysOperationLog.cost_time).label('avg_cost_time'),
            )
            .group_by(SysOperationLog.module)
            .order_by(func.count(SysOperationLog.id).desc())
            .limit(limit)
        )

        if base_conditions is not None:
            stmt = stmt.where(base_conditions)

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                'module': row.module,
                'total_count': row.total_count or 0,
                'success_rate': round(row.success_rate or 0, 2),
                'avg_cost_time': round(row.avg_cost_time or 0, 2),
            }
            for row in rows
        ]


sys_operation_log_crud = CRUDSysOperationLog()
