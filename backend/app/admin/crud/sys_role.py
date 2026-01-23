"""角色 CRUD"""

from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import CursorResult, Select, delete, select, update
from sqlalchemy.orm import selectinload

from backend.app.admin.model import SysDept, SysMenu, SysRole, SysUser

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema.sys_role import SysRoleCreate, SysRoleFilter, SysRoleUpdate


class CRUDSysRole:
    """角色 CRUD

    关联：
        - users: 用户列表 (多对多)
        - menus: 菜单列表 (多对多)
        - depts: 部门列表 (多对多, 用于自定义数据权限)
    """

    def __init__(self) -> None:
        self.model = SysRole

    async def get(self, db: 'AsyncSession', pk: int) -> SysRole | None:
        """根据主键获取角色信息（预加载 menus）"""
        stmt = select(SysRole).where(SysRole.id == pk).options(selectinload(SysRole.menus))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_column(self, db: 'AsyncSession', column: str, value: str) -> SysRole | None:
        """根据指定列名和值获取角色信息"""
        column_attr = getattr(SysRole, column)
        stmt = select(SysRole).where(column_attr == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_existing_ids(self, db: 'AsyncSession', role_ids: list[int]) -> list[int]:
        """获取指定列表中实际存在的角色 ID 列表"""
        stmt = select(SysRole.id).where(SysRole.id.in_(role_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_with_depts(self, db: 'AsyncSession', pk: int) -> SysRole | None:
        """获取角色（预加载 menus 和 depts）"""
        stmt = select(SysRole).where(SysRole.id == pk).options(selectinload(SysRole.menus), selectinload(SysRole.depts))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_users(self, db: 'AsyncSession', pk: int) -> SysRole | None:
        """获取角色（预加载 users）"""
        stmt = select(SysRole).where(SysRole.id == pk).options(selectinload(SysRole.users))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list_select(self, params: 'SysRoleFilter') -> Select[tuple[SysRole]]:
        """获取角色列表的 Select 语句"""
        conditions: list = []

        # 模糊查询字段
        for field in ['name', 'code']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysRole, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 精确查询字段
        for field in ['status', 'data_scope']:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysRole, field)
                conditions.append(field_attr == value)

        # 时间范围查询
        for field in ['created_time']:
            field_attr = getattr(SysRole, field)
            start_value = getattr(params, f'{field}_start', None)
            if start_value is not None:
                conditions.append(field_attr >= start_value)
            end_value = getattr(params, f'{field}_end', None)
            if end_value is not None:
                conditions.append(field_attr <= end_value)

        # 构建查询语句, 按 id 降序排列
        return select(SysRole).where(*conditions).order_by(SysRole.id.desc())

    async def create(self, db: 'AsyncSession', params: 'SysRoleCreate') -> SysRole:
        """创建角色"""

        # 提取 menu_ids, 准备角色数据
        menu_ids = params.menu_ids
        role_data = params.model_dump(exclude={'menu_ids'})

        # 创建角色实例
        role = SysRole(**role_data, menus=[], depts=[], users=[])

        # 处理 menus 多对多关系
        if menu_ids:
            stmt = select(SysMenu).where(SysMenu.id.in_(menu_ids))
            result = await db.execute(stmt)
            role.menus = list(result.scalars().all())

        # 添加到数据库
        db.add(role)
        await db.flush()

        return role

    async def update(self, db: 'AsyncSession', pk: int, params: 'SysRoleUpdate') -> int:
        """更新角色信息, 包括关联关系 menus"""
        # 获取角色实例（用于更新多对多关系）
        role = await self.get(db, pk)
        if not role:
            return 0

        # 提取普通字段更新数据
        update_data = params.model_dump(exclude={'id', 'menu_ids'}, exclude_unset=True)

        if update_data:
            stmt = update(SysRole).where(SysRole.id == pk).values(**update_data)
            result = await db.execute(stmt)
            result = cast('CursorResult[Any]', result)

        # 更新 menus 多对多关系
        menu_ids = params.menu_ids
        if menu_ids is not None:
            if menu_ids:
                # 如果菜单ID列表不为空，查询菜单对象
                stmt = select(SysMenu).where(SysMenu.id.in_(menu_ids))
                result = await db.execute(stmt)
                role.menus = list(result.scalars().all())
            else:
                # 如果菜单ID列表为空，清空角色的菜单
                role.menus = []

        return 1

    async def update_by_column(self, db: 'AsyncSession', pk: int, column: str, value: Any) -> int:
        """根据指定列名和值更新角色信息"""
        stmt = update(SysRole).where(SysRole.id == pk).values(**{column: value})
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_update_status(self, db: 'AsyncSession', role_ids: list[int], status: int) -> int:
        """批量更新角色状态"""
        if not role_ids:
            return 0

        stmt = update(SysRole).where(SysRole.id.in_(role_ids)).values(status=status)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def update_data_scope(self, db: 'AsyncSession', pk: int, data_scope: int, dept_ids: list[int]) -> int:
        """更新角色数据范围

        - 自定义数据权限需要更新关联的部门列表
        """
        # 获取角色实例
        role = await self.get(db, pk)
        if not role:
            return 0

        # 更新 data_scope 字段
        stmt = update(SysRole).where(SysRole.id == pk).values(data_scope=data_scope)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)

        # 更新 depts 多对多关系
        if dept_ids:
            stmt = select(SysDept).where(SysDept.id.in_(dept_ids))
            result = await db.execute(stmt)
            role.depts = list(result.scalars().all())
        else:
            role.depts = []

        return 1

    async def update_role_menus(self, db: 'AsyncSession', role_id: int, menu_ids: list[int]) -> int:
        """更新角色菜单关联"""
        role = await self.get(db, role_id)
        if not role:
            return 0

        # 更新 menus 多对多关系
        if menu_ids:
            stmt = select(SysMenu).where(SysMenu.id.in_(menu_ids))
            result = await db.execute(stmt)
            role.menus = list(result.scalars().all())
        else:
            role.menus = []

        return 1

    async def update_role_depts(self, db: 'AsyncSession', role_id: int, dept_ids: list[int]) -> int:
        """更新角色部门关联（自定义数据权限）"""
        role = await self.get(db, role_id)
        if not role:
            return 0

        # 更新 depts 多对多关系
        if dept_ids:
            stmt = select(SysDept).where(SysDept.id.in_(dept_ids))
            result = await db.execute(stmt)
            role.depts = list(result.scalars().all())
        else:
            role.depts = []

        return 1

    async def batch_assign_users(self, db: 'AsyncSession', role_id: int, user_ids: list[int]) -> int:
        """批量分配用户"""
        if not user_ids:
            return 0

        # 1. 查询当前角色已关联的用户ID（只查询ID，不加载完整对象）
        from backend.app.admin.model.m2m import sys_user_role

        stmt = select(sys_user_role.c.user_id).where(sys_user_role.c.role_id == role_id)
        result = await db.execute(stmt)
        existing_user_ids = set(result.scalars().all())

        # 2. 筛选出需要新增的用户ID
        new_user_ids = [uid for uid in user_ids if uid not in existing_user_ids]

        if not new_user_ids:
            return 0

        # 3. 只查询需要添加的用户对象
        stmt = select(SysUser).where(SysUser.id.in_(new_user_ids))
        result = await db.execute(stmt)
        new_users = list(result.scalars().all())

        if not new_users:
            return 0

        # 4. 获取角色对象（不需要预加载 users）
        role = await db.get(SysRole, role_id)
        if not role:
            return 0

        # 5. 添加新用户到角色
        role.users.extend(new_users)

        return len(new_users)

    async def batch_revoke_users(self, db: 'AsyncSession', role_id: int, user_ids: list[int]) -> int:
        """批量取消用户授权"""
        if not user_ids:
            return 0

        # 1. 查询当前角色已关联的用户ID（只查询ID，不加载完整对象）
        from backend.app.admin.model.m2m import sys_user_role

        stmt = select(sys_user_role.c.user_id).where(sys_user_role.c.role_id == role_id)
        result = await db.execute(stmt)
        existing_user_ids = set(result.scalars().all())

        # 2. 筛选出需要移除的用户ID（确保这些用户确实已关联）
        user_ids_to_remove = [uid for uid in user_ids if uid in existing_user_ids]

        if not user_ids_to_remove:
            return 0

        # 3. 查询需要移除的用户对象
        stmt = select(SysUser).where(SysUser.id.in_(user_ids_to_remove))
        result = await db.execute(stmt)
        users_to_remove = list(result.scalars().all())

        if not users_to_remove:
            return 0

        # 4. 获取角色对象并预加载当前用户列表
        stmt = select(SysRole).where(SysRole.id == role_id).options(selectinload(SysRole.users))
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            return 0

        # 5. 从角色中移除指定用户
        user_ids_to_remove_set = set(user_ids_to_remove)
        role.users = [user for user in role.users if user.id not in user_ids_to_remove_set]

        return len(users_to_remove)

    async def delete(self, db: 'AsyncSession', pk: int) -> int:
        """删除角色"""
        stmt = delete(SysRole).where(SysRole.id == pk)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_delete(self, db: 'AsyncSession', role_ids: list[int]) -> int:
        """批量删除角色"""
        if not role_ids:
            return 0

        stmt = delete(SysRole).where(SysRole.id.in_(role_ids))
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount


sys_role_crud = CRUDSysRole()
