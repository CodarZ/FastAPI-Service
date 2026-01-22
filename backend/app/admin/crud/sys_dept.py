from typing import TYPE_CHECKING

from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import SysDept

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema import SysDeptCreate, SysDeptFilter, SysDeptUpdate


class CRUDSysDept(CRUDPlus[SysDept]):
    """部门 CRUD"""

    async def get(self, db: AsyncSession, pk: int) -> SysDept | None:
        """根据主键获取部门信息（预加载 parent）"""
        stmt = select(SysDept).where(SysDept.id == pk).options(selectinload(SysDept.parent))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_column(self, db: AsyncSession, column: str, value: str) -> SysDept | None:
        """根据指定列名和值获取部门信息"""
        column_attr = getattr(SysDept, column)
        stmt = select(SysDept).where(column_attr == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_children(self, db: AsyncSession, pk: int) -> SysDept | None:
        """获取部门（预加载子部门列表）"""
        stmt = select(SysDept).where(SysDept.id == pk).options(selectinload(SysDept.children))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_full_detail(self, db: AsyncSession, pk: int) -> SysDept | None:
        """获取部门完整详情（预加载子级）

        注意：parent 已通过 lazy='selectin' 自动加载，这里只需预加载 children
        """
        stmt = select(SysDept).where(SysDept.id == pk).options(selectinload(SysDept.children))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_existing_ids(self, db: AsyncSession, ids: list[int]) -> list[int]:
        """获取指定列表中实际存在的部门 ID"""
        stmt = select(SysDept.id).where(SysDept.id.in_(ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_list_select(self, params: SysDeptFilter) -> Select:
        """获取部门列表的 Select 语句"""

        filters = {}

        # 模糊查询字段
        for field in ['title', 'leader']:
            value = getattr(params, field, None)
            if value:
                filters[f'{field}__like'] = f'%{value}%'

        # 精确查询字段
        for field in ['status', 'parent_id']:
            value = getattr(params, field, None)
            if value is not None:
                filters[field] = value

        # 时间范围查询
        for column in ['created_time']:
            for suffix, op in [('start', 'ge'), ('end', 'le')]:
                param = f'{column}_{suffix}'
                value = getattr(params, param, None)
                if value is not None:
                    filters[f'{column}__{op}'] = value

        stmt = await self.select_order('id', 'desc', **filters)
        # 预加载 parent 关系，避免延迟加载导致 DetachedInstanceError
        return stmt.options(selectinload(SysDept.parent))

    async def create(self, db: AsyncSession, params: SysDeptCreate) -> SysDept:
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

    async def update(self, db: AsyncSession, pk: int, params: SysDeptUpdate) -> int:
        """更新部门信息"""

        await self.update_model(db, pk, params)
        return 1

    async def update_by_column(self, db: AsyncSession, pk: int, column: str, value) -> int:
        """根据指定 列名和值 更新部门信息（支持任意类型）"""
        return await self.update_model(db, pk, {column: value})

    async def batch_update_status(self, db: AsyncSession, dept_ids: list[int], status: int) -> int:
        """批量更新部门状态"""
        if not dept_ids:
            return 0

        stmt = update(SysDept).where(SysDept.id.in_(dept_ids)).values(status=status)
        result = await db.execute(stmt)
        return getattr(result, 'rowcount', 0)

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """删除部门"""
        return await self.delete_model(db, pk)

    async def batch_delete(self, db: AsyncSession, dept_ids: list[int]) -> int:
        """批量删除部门"""
        if not dept_ids:
            return 0

        stmt = delete(SysDept).where(SysDept.id.in_(dept_ids))
        result = await db.execute(stmt)
        return getattr(result, 'rowcount', 0)


sys_dept_crud = CRUDSysDept(SysDept)
