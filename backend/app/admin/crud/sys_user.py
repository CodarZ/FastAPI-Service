"""用户 CRUD"""

from typing import TYPE_CHECKING, Any, List, Tuple, cast

import bcrypt

from sqlalchemy import CursorResult, Select, delete, select, update
from sqlalchemy.orm import selectinload

from backend.app.admin.model import SysDept, SysRole, SysUser
from backend.common.security.password import get_hashed_password
from backend.utils.timezone import timezone

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema.sys_user import (
        SysUserCreate,
        SysUserFilter,
        SysUserPatchProfile,
        SysUserUpdate,
    )


class CRUDSysUser:
    """用户 CRUD

    关联：
        - dept: 所属部门 (外键)
        - roles: 角色列表 (多对多)
    """

    def __init__(self) -> None:
        self.model = SysUser

    async def get(self, db: 'AsyncSession', pk: int) -> SysUser | None:
        """根据主键获取用户信息（预加载 dept 和 roles）"""
        stmt = select(SysUser).where(SysUser.id == pk).options(selectinload(SysUser.dept), selectinload(SysUser.roles))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_column(self, db: 'AsyncSession', column: str, value: str) -> SysUser | None:
        """根据指定列名和值获取用户信息（预加载 dept 和 roles）

        注意：
        - 如果存在多条记录，只返回第一条
        """
        column_attr = getattr(SysUser, column)
        stmt = (
            select(SysUser)
            .where(column_attr == value)
            .options(selectinload(SysUser.dept), selectinload(SysUser.roles))
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_existing_ids(self, db: 'AsyncSession', user_ids: list[int]) -> List[int]:
        """获取指定列表中实际存在的用户 ID 列表"""
        stmt = select(SysUser.id).where(SysUser.id.in_(user_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_superuser_ids(self, db: 'AsyncSession', user_ids: list[int]) -> List[int]:
        """获取指定列表中的超级管理员 ID"""
        stmt = select(SysUser.id).where(SysUser.id.in_(user_ids), SysUser.is_superuser)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_permissions(self, db: 'AsyncSession', user_id: int) -> Select[Tuple[SysUser]]:
        """获取用户权限集合"""

        return (
            select(SysUser)
            .options(selectinload(SysUser.roles).selectinload(SysRole.menus))
            .where(SysUser.id == user_id)
        )

    async def has_users_in_dept(self, db: 'AsyncSession', dept_id: int) -> bool:
        """检查部门下是否有用户"""
        stmt = select(SysUser.id).where(SysUser.dept_id == dept_id).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_list_select(self, params: 'SysUserFilter') -> Select[tuple[SysUser]]:
        """获取用户列表的 Select 语句"""
        conditions: list = []

        # 模糊查询字段
        for field in ['username', 'realname', 'nickname', 'email']:
            value = getattr(params, field, None)
            if value:
                field_attr = getattr(SysUser, field)
                conditions.append(field_attr.ilike(f'%{value}%'))

        # 精确查询字段
        for field in [
            'phone',
            'status',
            'dept_id',
            'is_superuser',
            'is_admin',
            'is_multi_login',
            'is_verified',
        ]:
            value = getattr(params, field, None)
            if value is not None:
                field_attr = getattr(SysUser, field)
                conditions.append(field_attr == value)

        # 时间范围查询
        for field in ['created_time', 'last_login_time']:
            field_attr = getattr(SysUser, field)
            start_value = getattr(params, f'{field}_start', None)
            if start_value is not None:
                conditions.append(field_attr >= start_value)
            end_value = getattr(params, f'{field}_end', None)
            if end_value is not None:
                conditions.append(field_attr <= end_value)

        # 构建查询语句, 按 id 降序排列
        stmt = select(SysUser).where(*conditions).order_by(SysUser.id.desc())
        # 预加载 dept 关系, 避免延迟加载导致 DetachedInstanceError
        return stmt.options(selectinload(SysUser.dept))

    async def create(self, db: 'AsyncSession', params: 'SysUserCreate') -> SysUser:
        """创建新用户"""

        # 1. 加密
        salt = bcrypt.gensalt()
        hashed_password = get_hashed_password(params.password, salt)

        # 2. 提取 role_ids 和 dept_id, 准备用户数据
        role_ids = params.role_ids
        dept_id = params.dept_id
        user_data = params.model_dump(exclude={'password', 'role_ids', 'dept_id'})

        # 3. 加载 dept 关联对象
        # MappedAsDataclass 模式下, 必须传入关联对象而非仅外键
        dept = None
        if dept_id is not None:
            dept = await db.get(SysDept, dept_id)

        # 4. 创建用户实例
        user = SysUser(
            **user_data,
            password=hashed_password,
            salt=salt,
            dept_id=dept_id,
            is_superuser=False,
            is_admin=False,
            dept=dept,
            roles=[],
        )

        # 5. 处理 roles 多对多关系
        if role_ids:
            stmt = select(SysRole).where(SysRole.id.in_(role_ids))
            result = await db.execute(stmt)
            user.roles = list(result.scalars().all())

        # 6. 添加到数据库
        db.add(user)
        await db.flush()

        return user

    async def update(self, db: 'AsyncSession', pk: int, params: 'SysUserUpdate') -> int:
        """全量更新用户信息, 包括关联关系 roles"""
        # 获取用户实例（用于更新多对多关系）
        user = await self.get(db, pk)
        if not user:
            return 0

        # 提取普通字段更新数据
        update_data = params.model_dump(exclude={'id', 'role_ids'}, exclude_unset=True)

        if update_data:
            stmt = update(SysUser).where(SysUser.id == pk).values(**update_data)
            result = await db.execute(stmt)
            result = cast('CursorResult[Any]', result)

        # 更新 roles 多对多关系
        role_ids = params.role_ids
        if role_ids is not None:
            stmt = select(SysRole).where(SysRole.id.in_(role_ids))
            result = await db.execute(stmt)
            user.roles = list(result.scalars().all())

        return 1

    async def update_by_column(self, db: 'AsyncSession', pk: int, column: str, value: Any) -> int:
        """根据指定列名和值更新用户信息（支持任意类型）"""
        stmt = update(SysUser).where(SysUser.id == pk).values(**{column: value})
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_update_status(self, db: 'AsyncSession', user_ids: list[int], status: int) -> int:
        """批量更新用户状态"""
        if not user_ids:
            return 0

        stmt = update(SysUser).where(SysUser.id.in_(user_ids)).values(status=status)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def update_profile(self, db: 'AsyncSession', pk: int, params: 'SysUserPatchProfile') -> int:
        """更新用户资料（只更新非 None 字段）"""
        update_data = params.model_dump(exclude={'id'}, exclude_unset=True)
        if not update_data:
            return 0
        stmt = update(SysUser).where(SysUser.id == pk).values(**update_data)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def update_password(self, db: 'AsyncSession', pk: int, new_password: str) -> int:
        """更新用户密码"""
        salt = bcrypt.gensalt()
        hashed_password = get_hashed_password(new_password, salt)
        stmt = update(SysUser).where(SysUser.id == pk).values(password=hashed_password, salt=salt)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def update_login_time(self, db: 'AsyncSession', pk: int) -> int:
        """更新用户最后登录时间"""

        stmt = update(SysUser).where(SysUser.id == pk).values(last_login_time=timezone.now())
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def delete(self, db: 'AsyncSession', pk: int) -> int:
        """删除用户"""
        stmt = delete(SysUser).where(SysUser.id == pk)
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount

    async def batch_delete(self, db: 'AsyncSession', user_ids: list[int]) -> int:
        """批量删除用户"""
        if not user_ids:
            return 0

        stmt = delete(SysUser).where(SysUser.id.in_(user_ids))
        result = await db.execute(stmt)
        result = cast('CursorResult[Any]', result)
        return result.rowcount


sys_user_crud = CRUDSysUser()
