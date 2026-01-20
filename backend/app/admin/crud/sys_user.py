"""用户 CRUD"""

from typing import TYPE_CHECKING

import bcrypt

from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import noload, selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model.m2m import sys_user_role
from backend.app.admin.model.sys_dept import SysDept
from backend.app.admin.model.sys_role import SysRole
from backend.app.admin.model.sys_user import SysUser
from backend.common.security.password import get_hashed_password

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.schema.sys_user import (
        SysUserAdvancedFilter,
        SysUserCreate,
        SysUserFilter,
        SysUserPatchProfile,
        SysUserUpdate,
    )


class CRUDSysUser(CRUDPlus[SysUser]):
    """用户 CRUD

    关联：
        - dept: 所属部门 (外键)
        - roles: 角色列表 (多对多)
    """

    async def get(self, db: AsyncSession, pk: int) -> SysUser | None:
        """根据 pk 获取用户信息"""
        result = await self.select_model(db, pk)
        if isinstance(result, SysUser):
            return result
        # 兼容 SQLAlchemy Row 对象, 使用 getattr 避免类型检查器报错
        mapping = getattr(result, '_mapping', None)
        if mapping:
            return mapping.get('SysUser') or next(iter(mapping.values()), None)
        return None

    async def get_by_column(self, db: AsyncSession, column: str, value: str) -> SysUser | None:
        """根据指定 列名和值 获取用户信息"""
        result = await self.select_model_by_column(db, getattr(self.model, column) == value)
        if isinstance(result, SysUser):
            return result
        mapping = getattr(result, '_mapping', None)
        if mapping:
            return mapping.get('SysUser') or next(iter(mapping.values()), None)
        return None

    async def get_existing_ids(self, db: AsyncSession, user_ids: list[int]) -> list[int]:
        """获取指定列表中的实际存在的用户ID列表"""

        stmt = select(SysUser.id).where(SysUser.id.in_(user_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_superuser_ids(self, db: AsyncSession, user_ids: list[int]) -> list[int]:
        """获取指定列表中的超级管理员ID列表"""

        stmt = select(SysUser.id).where(SysUser.id.in_(user_ids), SysUser.is_superuser)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_list_select(self, params: SysUserFilter) -> Select:
        """获取用户列表的 Select 语句"""

        filters = {}

        # 模糊查询字段
        for field in ['username', 'realname', 'nickname', 'email']:
            value = getattr(params, field, None)
            if value:
                filters[f'{field}__like'] = f'%{value}%'

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
                filters[field] = value

        # 时间范围查询
        for column in ['created_time', 'last_login_time']:
            for suffix, op in [('start', 'ge'), ('end', 'le')]:
                param = f'{column}_{suffix}'
                value = getattr(params, param, None)
                if value is not None:
                    filters[f'{column}__{op}'] = value

        # 加载 dept 对象，不加载 roles（避免 N+1 查询）
        stmt = await self.select_order('id', 'desc', **filters)
        return stmt.options(selectinload(SysUser.dept), noload(SysUser.roles))

    async def get_list_advanced_select(self, params: SysUserAdvancedFilter) -> Select:
        """获取用户列表的 Select 高级语句

        在基础过滤条件上，额外支持：
            - role_id: 按角色ID过滤（通过 JOIN 中间表）
            - keyword: 多字段模糊搜索（用户名/昵称/真实姓名/手机号/邮箱）
        """
        # 复用基础 Select（已包含常规过滤、排序、dept 加载）
        stmt = await self.get_list_select(params)

        # 处理 role_id 过滤 - JOIN 中间表
        if params.role_id is not None:
            stmt = stmt.join(sys_user_role, SysUser.id == sys_user_role.c.user_id).where(
                sys_user_role.c.role_id == params.role_id
            )

        # 处理 keyword 全局模糊搜索 - 匹配多个字段
        if params.keyword:
            keyword_pattern = f'%{params.keyword}%'
            stmt = stmt.where(
                or_(
                    SysUser.realname.ilike(keyword_pattern),
                    SysUser.username.ilike(keyword_pattern),
                    SysUser.nickname.ilike(keyword_pattern),
                    SysUser.phone.ilike(keyword_pattern),
                    SysUser.email.ilike(keyword_pattern),
                )
            )

        return stmt

    async def create(self, db: AsyncSession, params: SysUserCreate) -> SysUser:
        """创建新用户"""

        # 1. 加密
        salt = bcrypt.gensalt()
        hashed_password = get_hashed_password(params.password, salt)

        # 2. 提取 role_ids 和 dept_id，准备用户数据
        role_ids = params.role_ids
        dept_id = params.dept_id
        user_data = params.model_dump(exclude={'password', 'role_ids', 'dept_id'})

        # 3. 加载 dept 关联对象（MappedAsDataclass 模式下，必须传入关联对象而非仅外键）
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

    async def update(self, db: AsyncSession, pk: int, params: SysUserUpdate) -> int:
        """全量更新用户信息, 包括关联关系 roles"""
        # 获取用户实例（用于更新多对多关系）
        user = await self.get(db, pk)
        if not user:
            return 0

        # 提取 role_ids 并从更新数据中排除
        role_ids = params.role_ids
        simple_update_data = params.model_dump(exclude={'id', 'role_ids'})

        # 更新普通字段
        await self.update_model(db, pk, simple_update_data)

        # 更新 roles 多对多关系
        if role_ids is not None:
            from sqlalchemy import select

            from backend.app.admin.model.sys_role import SysRole

            stmt = select(SysRole).where(SysRole.id.in_(role_ids))
            result = await db.execute(stmt)
            user.roles = list(result.scalars().all())

        return 1

    async def update_by_column(self, db: AsyncSession, pk: int, column: str, value) -> int:
        """根据指定 列名和值 更新用户信息（支持任意类型）"""
        return await self.update_model(db, pk, {column: value})

    async def batch_update_status(self, db: AsyncSession, user_ids: list[int], status: int) -> int:
        """批量更新用户状态"""
        if not user_ids:
            return 0

        stmt = update(SysUser).where(SysUser.id.in_(user_ids)).values(status=status)
        result = await db.execute(stmt)
        return getattr(result, 'rowcount', 0)

    async def update_profile(self, db: AsyncSession, pk: int, params: SysUserPatchProfile) -> int:
        """更新用户资料（只更新非 None 字段）"""
        update_data = params.model_dump(exclude={'id'}, exclude_unset=True)
        if not update_data:
            return 0
        return await self.update_model(db, pk, update_data)

    async def update_password(self, db: AsyncSession, pk: int, new_password: str) -> int:
        """更新用户密码"""
        salt = bcrypt.gensalt()
        hashed_password = get_hashed_password(new_password, salt)
        return await self.update_model(db, pk, {'password': hashed_password, 'salt': salt})

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """删除用户"""
        return await self.delete_model(db, pk)

    async def batch_delete(self, db: AsyncSession, user_ids: list[int]) -> int:
        """批量删除用户"""
        if not user_ids:
            return 0

        stmt = delete(SysUser).where(SysUser.id.in_(user_ids))
        result = await db.execute(stmt)
        return getattr(result, 'rowcount', 0)


sys_user_crud = CRUDSysUser(SysUser)
