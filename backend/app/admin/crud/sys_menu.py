"""菜单 CRUD"""

from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import CursorResult, Select, delete, select, update
from sqlalchemy.orm import selectinload

from backend.app.admin.model import SysMenu

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema.sys_menu import SysMenuCreate, SysMenuFilter, SysMenuUpdate


class CRUDSysMenu:
    """菜单 CRUD

    关联：
        - parent: 上级菜单 (自引用外键)
        - children: 子菜单列表 (自引用关系)
        - roles: 角色列表 (多对多)
    """

    def __init__(self) -> None:
        self.model = SysMenu

    async def get(self, db: 'AsyncSession', pk: int) -> SysMenu | None:
        """根据主键获取菜单信息"""
        stmt = select(SysMenu).where(SysMenu.id == pk).options(selectinload(SysMenu.parent))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_column(self, db: 'AsyncSession', column: str, value: str) -> SysMenu | None:
        """根据指定列名和值获取菜单信息"""
        column_attr = getattr(SysMenu, column)
        stmt = select(SysMenu).where(column_attr == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_existing_ids(self, db: 'AsyncSession', menu_ids: list[int]) -> list[int]:
        """获取指定列表中实际存在的菜单 ID 列表"""
        stmt = select(SysMenu.id).where(SysMenu.id.in_(menu_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_list_select(self, params: 'SysMenuFilter') -> Select[tuple[SysMenu]]:
        """获取菜单列表的 Select 语句"""
        conditions: list = []

        # 模糊查询字段
        for field in ['title', 'permission']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysMenu, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 精确查询字段
        for field in ['type', 'status', 'hidden', 'parent_id']:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysMenu, field)
                conditions.append(field_attr == value)

        # 时间范围查询
        for field in ['created_time']:
            field_attr = getattr(SysMenu, field)
            start_value = getattr(params, f'{field}_start', None)
            if start_value is not None:
                conditions.append(field_attr >= start_value)
            end_value = getattr(params, f'{field}_end', None)
            if end_value is not None:
                conditions.append(field_attr <= end_value)

        # 构建查询语句, 按 sort 升序、id 升序排列
        return select(SysMenu).where(*conditions).order_by(SysMenu.sort.asc(), SysMenu.id.asc())

    async def get_all(self, db: 'AsyncSession') -> list[SysMenu]:
        """获取所有菜单（用于构建树形结构）"""
        stmt = select(SysMenu).order_by(SysMenu.sort.asc(), SysMenu.id.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, db: 'AsyncSession', status: int = 1) -> list[SysMenu]:
        """根据状态获取菜单列表"""
        stmt = select(SysMenu).where(SysMenu.status == status).order_by(SysMenu.sort.asc(), SysMenu.id.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, db: 'AsyncSession', parent_id: int) -> list[SysMenu]:
        """获取指定菜单的子菜单"""
        stmt = select(SysMenu).where(SysMenu.parent_id == parent_id).order_by(SysMenu.sort.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_children_ids(self, db: 'AsyncSession', parent_id: int) -> list[int]:
        """递归获取指定菜单的所有子孙菜单 ID（包括自己）"""
        menu_ids = [parent_id]

        async def _collect_children(pid: int):
            children = await self.get_children(db, pid)
            for child in children:
                menu_ids.append(child.id)
                await _collect_children(child.id)

        await _collect_children(parent_id)
        return menu_ids

    async def create(self, db: 'AsyncSession', params: 'SysMenuCreate') -> SysMenu:
        """创建菜单"""
        menu_data = params.model_dump()
        menu = SysMenu(**menu_data, roles=[])
        db.add(menu)
        await db.flush()
        return menu

    async def update(self, db: 'AsyncSession', pk: int, params: 'SysMenuUpdate') -> int:
        """更新菜单信息"""
        update_data = params.model_dump(exclude={'id'}, exclude_unset=True)

        if not update_data:
            return 0

        stmt = update(SysMenu).where(SysMenu.id == pk).values(**update_data)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def update_by_column(self, db: 'AsyncSession', pk: int, column: str, value: Any) -> int:
        """根据指定列名和值更新菜单信息"""
        stmt = update(SysMenu).where(SysMenu.id == pk).values(**{column: value})
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_update_status(self, db: 'AsyncSession', menu_ids: list[int], status: int) -> int:
        """批量更新菜单状态"""
        if not menu_ids:
            return 0

        stmt = update(SysMenu).where(SysMenu.id.in_(menu_ids)).values(status=status)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def delete(self, db: 'AsyncSession', pk: int) -> int:
        """删除菜单（级联删除子菜单）"""
        stmt = delete(SysMenu).where(SysMenu.id == pk)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_delete(self, db: 'AsyncSession', menu_ids: list[int]) -> int:
        """批量删除菜单"""
        if not menu_ids:
            return 0

        stmt = delete(SysMenu).where(SysMenu.id.in_(menu_ids))
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def check_parent_exists(self, db: 'AsyncSession', parent_id: int) -> bool:
        """检查上级菜单是否存在"""
        stmt = select(SysMenu.id).where(SysMenu.id == parent_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def check_has_children(self, db: 'AsyncSession', pk: int) -> bool:
        """检查菜单是否有子菜单"""
        stmt = select(SysMenu.id).where(SysMenu.parent_id == pk).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def check_title_unique(
        self, db: 'AsyncSession', title: str, parent_id: int | None = None, exclude_id: int | None = None
    ) -> bool:
        """检查菜单标题在同级菜单中是否唯一"""
        stmt = select(SysMenu.id).where(SysMenu.title == title, SysMenu.parent_id == parent_id)

        if exclude_id:
            stmt = stmt.where(SysMenu.id != exclude_id)

        result = await db.execute(stmt)
        return result.scalar_one_or_none() is None

    async def check_permission_unique(self, db: 'AsyncSession', permission: str, exclude_id: int | None = None) -> bool:
        """检查权限标识是否唯一"""
        stmt = select(SysMenu.id).where(SysMenu.permission == permission)

        if exclude_id:
            stmt = stmt.where(SysMenu.id != exclude_id)

        result = await db.execute(stmt)
        return result.scalar_one_or_none() is None


sys_menu_crud = CRUDSysMenu()
