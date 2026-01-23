from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import CursorResult, Select, delete, select, update
from sqlalchemy.orm import selectinload

from backend.app.admin.model import SysDept

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema import SysDeptCreate, SysDeptFilter, SysDeptUpdate


class CRUDSysDept:
    """部门 CRUD"""

    def __init__(self) -> None:
        self.model = SysDept

    async def get(self, db: 'AsyncSession', pk: int) -> SysDept | None:
        """根据主键获取部门信息（预加载 parent）"""
        stmt = select(SysDept).where(SysDept.id == pk).options(selectinload(SysDept.parent))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_column(self, db: 'AsyncSession', column: str, value: str) -> SysDept | None:
        """根据指定列名和值获取部门信息"""
        column_attr = getattr(SysDept, column)
        stmt = select(SysDept).where(column_attr == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_children(self, db: 'AsyncSession', pk: int) -> SysDept | None:
        """获取部门（预加载子部门列表）"""
        stmt = select(SysDept).where(SysDept.id == pk).options(selectinload(SysDept.children))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_existing_ids(self, db: 'AsyncSession', ids: list[int]) -> list[int]:
        """获取指定列表中实际存在的部门 ID"""
        stmt = select(SysDept.id).where(SysDept.id.in_(ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_list_select(self, params: 'SysDeptFilter') -> Select[tuple[SysDept]]:
        """获取部门列表的 Select 语句"""
        conditions: list = []

        # 模糊查询字段
        for field in ['title', 'leader']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysDept, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 精确查询字段
        for field in ['status', 'parent_id']:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysDept, field)
                conditions.append(field_attr == value)

        # 时间范围查询
        for field in ['created_time']:
            field_attr = getattr(SysDept, field)
            start_value = getattr(params, f'{field}_start', None)
            if start_value is not None:
                conditions.append(field_attr >= start_value)
            end_value = getattr(params, f'{field}_end', None)
            if end_value is not None:
                conditions.append(field_attr <= end_value)

        # 构建查询语句，按 id 降序排列
        stmt = select(SysDept).where(*conditions).order_by(SysDept.id.desc())
        # 预加载 parent 关系，避免延迟加载导致 DetachedInstanceError
        return stmt.options(selectinload(SysDept.parent))

    async def create(self, db: 'AsyncSession', params: 'SysDeptCreate') -> SysDept:
        """创建部门"""

        # 加载 parent 关联对象（如果有 parent_id）
        # 在 MappedAsDataclass 模式下，必须传入关联对象而非仅外键
        parent = None
        if params.parent_id is not None:
            parent = await db.get(SysDept, params.parent_id)

        dept = SysDept(**params.model_dump(), parent=parent)

        db.add(dept)
        await db.flush()

        return dept

    async def update(self, db: 'AsyncSession', pk: int, params: 'SysDeptUpdate') -> int:
        """更新部门信息"""
        data = params.model_dump(exclude_unset=True)
        if not data:
            return 0

        stmt = update(SysDept).where(SysDept.id == pk).values(**data)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def update_by_column(self, db: 'AsyncSession', pk: int, column: str, value: Any) -> int:
        """根据指定列名和值更新部门信息"""
        stmt = update(SysDept).where(SysDept.id == pk).values(**{column: value})
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_update_status(self, db: 'AsyncSession', dept_ids: list[int], status: int) -> int:
        """批量更新部门状态"""
        if not dept_ids:
            return 0

        stmt = update(SysDept).where(SysDept.id.in_(dept_ids)).values(status=status)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def delete(self, db: 'AsyncSession', pk: int) -> int:
        """删除部门"""
        stmt = delete(SysDept).where(SysDept.id == pk)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_delete(self, db: 'AsyncSession', dept_ids: list[int]) -> int:
        """批量删除部门"""
        if not dept_ids:
            return 0

        stmt = delete(SysDept).where(SysDept.id.in_(dept_ids))
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount


sys_dept_crud = CRUDSysDept()
