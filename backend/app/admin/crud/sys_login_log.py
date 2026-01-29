from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import CursorResult, Select, case, delete, func, select

from backend.app.admin.model import SysLoginLog
from backend.app.admin.schema.sys_login_log import SysLoginLogStatistics

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema.sys_login_log import SysLoginLogClear, SysLoginLogCreate, SysLoginLogFilter


class CRUDSysLoginLog:
    """登录日志 CRUD"""

    def __init__(self) -> None:
        self.model = SysLoginLog

    async def get(self, db: 'AsyncSession', pk: int) -> SysLoginLog | None:
        """根据主键获取登录日志详情"""
        stmt = select(SysLoginLog).where(SysLoginLog.id == pk)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list_select(self, params: 'SysLoginLogFilter') -> Select[tuple[SysLoginLog]]:
        """获取登录日志列表的 Select 语句"""
        conditions: list = []

        # 模糊查询字段
        for field in ['username', 'city', 'os', 'browser']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysLoginLog, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 精确查询字段
        for field in ['user_id', 'status', 'ip']:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysLoginLog, field)
                conditions.append(field_attr == value)

        # 时间范围查询（start/end 后缀）
        for field in ['login_time']:
            field_attr = getattr(SysLoginLog, field)
            start_value = getattr(params, f'{field}_start', None)
            if start_value is not None:
                conditions.append(field_attr >= start_value)
            end_value = getattr(params, f'{field}_end', None)
            if end_value is not None:
                conditions.append(field_attr <= end_value)

        # 构建查询语句, 按登录时间降序排列（最新的在前）
        return select(SysLoginLog).where(*conditions).order_by(SysLoginLog.login_time.desc())

    async def create(self, db: 'AsyncSession', params: SysLoginLogCreate) -> SysLoginLog:
        """创建登录日志"""

        log = SysLoginLog(**params.model_dump())
        db.add(log)
        await db.flush()
        return log

    async def batch_create(self, db: 'AsyncSession', params_list: list[SysLoginLogCreate]) -> list[SysLoginLog]:
        """批量创建登录日志"""

        if not params_list:
            return []

        logs = [SysLoginLog(**params.model_dump()) for params in params_list]
        db.add_all(logs)
        await db.flush()
        return logs

    async def delete(self, db: 'AsyncSession', pk: int) -> int:
        """删除单条登录日志"""
        stmt = delete(SysLoginLog).where(SysLoginLog.id == pk)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_delete(self, db: 'AsyncSession', log_ids: list[int]) -> int:
        """批量删除登录日志"""
        if not log_ids:
            return 0

        stmt = delete(SysLoginLog).where(SysLoginLog.id.in_(log_ids))
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def clear_by_conditions(self, db: 'AsyncSession', params: 'SysLoginLogClear') -> int:
        """按条件清理登录日志"""
        conditions: list = []

        # 时间条件
        if params.before_time is not None:
            conditions.append(SysLoginLog.login_time < params.before_time)

        # 状态条件
        if params.status is not None:
            conditions.append(SysLoginLog.status == params.status)

        if not conditions:
            # 如果没有任何条件，为安全起见不执行删除
            return 0

        stmt = delete(SysLoginLog).where(*conditions)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def get_statistics(self, db: 'AsyncSession', params: 'SysLoginLogFilter') -> SysLoginLogStatistics:
        """获取登录日志统计信息"""
        conditions = await self._build_filter_conditions(params)

        stmt = select(
            func.count(SysLoginLog.id).label('total_count'),
            func.sum(case((SysLoginLog.status == 1, 1), else_=0)).label('success_count'),
            func.sum(case((SysLoginLog.status == 0, 1), else_=0)).label('error_count'),
        ).where(*conditions)

        result = await db.execute(stmt)
        row = result.one_or_none()

        if not row:
            return SysLoginLogStatistics(total_count=0, success_count=0, error_count=0)

        return SysLoginLogStatistics(
            total_count=row.total_count or 0,
            success_count=row.success_count or 0,
            error_count=row.error_count or 0,
        )

    async def _build_filter_conditions(self, params: 'SysLoginLogFilter') -> list:
        """构建过滤条件（用于统计等复用）"""
        conditions: list = []

        # 模糊查询字段
        for field in ['username', 'city', 'os', 'browser']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysLoginLog, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 精确查询字段
        for field in ['user_id', 'status', 'ip']:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysLoginLog, field)
                conditions.append(field_attr == value)

        # 时间范围查询
        if params.login_time_start is not None:
            conditions.append(SysLoginLog.login_time >= params.login_time_start)
        if params.login_time_end is not None:
            conditions.append(SysLoginLog.login_time <= params.login_time_end)

        return conditions


sys_login_log_crud = CRUDSysLoginLog()
