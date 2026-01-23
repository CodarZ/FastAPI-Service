"""角色服务类"""

from typing import TYPE_CHECKING

from backend.app.admin.crud import sys_role_crud
from backend.app.admin.schema.sys_role import (
    SysRoleBatchDelete,
    SysRoleBatchPatchStatus,
    SysRoleBatchUserAuth,
    SysRoleCreate,
    SysRoleDeptMap,
    SysRoleDetail,
    SysRoleFilter,
    SysRoleInfo,
    SysRoleListItem,
    SysRoleMenuMap,
    SysRoleOption,
    SysRolePatchDataScope,
    SysRolePatchStatus,
    SysRoleUpdate,
    SysRoleWithUsers,
)
from backend.common.exception import errors
from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SysRoleService:
    """角色服务类"""

    @staticmethod
    async def _get_role_or_404(db: 'AsyncSession', pk: int):
        """获取角色, 不存在则抛出 NotFoundError"""
        role = await sys_role_crud.get(db, pk)
        if not role:
            raise errors.NotFoundError(msg='角色不存在')
        return role

    @staticmethod
    async def get_role_info(*, db: 'AsyncSession', pk: int) -> SysRoleInfo:
        """获取角色信息"""
        role = await SysRoleService._get_role_or_404(db, pk)
        return SysRoleInfo.model_validate(role)

    @staticmethod
    async def get_role_detail(*, db: 'AsyncSession', pk: int) -> SysRoleDetail:
        """获取角色详情（包含 menus 和 depts）"""
        role = await sys_role_crud.get_with_depts(db, pk)
        if not role:
            raise errors.NotFoundError(msg='角色不存在')
        return SysRoleDetail.model_validate(role)

    @staticmethod
    async def get_role_with_users(*, db: 'AsyncSession', pk: int) -> SysRoleWithUsers:
        """获取角色及其分配的用户"""
        role = await sys_role_crud.get_with_users(db, pk)
        if not role:
            raise errors.NotFoundError(msg='角色不存在')
        return SysRoleWithUsers.model_validate(role)

    @staticmethod
    async def get_list(*, params: SysRoleFilter) -> list[SysRoleListItem]:
        """获取角色列表（基础过滤）"""
        async with async_session.begin() as db:
            stmt = await sys_role_crud.get_list_select(params)
            result = await db.scalars(stmt)
            roles = result.all()
            # 在 session 内完成序列化, 避免 DetachedInstanceError
            return [SysRoleListItem.model_validate(role) for role in roles]

    @staticmethod
    async def get_options() -> list[SysRoleOption]:
        """获取角色选项列表（用于下拉选择器）

        只返回启用状态的角色, 仅包含 id、name、code
        """
        async with async_session.begin() as db:
            from sqlalchemy import select

            from backend.app.admin.model import SysRole

            stmt = select(SysRole.id, SysRole.name, SysRole.code).where(SysRole.status == 1).order_by(SysRole.id.desc())
            result = await db.execute(stmt)
            rows = result.all()

            # 转换为 Schema
            return [SysRoleOption(id=r.id, name=r.name, code=r.code) for r in rows]

    @staticmethod
    async def create(*, db: 'AsyncSession', params: SysRoleCreate):
        """创建新角色"""
        # 校验角色名称是否重复
        if await sys_role_crud.get_by_column(db, 'name', params.name):
            raise errors.ConflictError(msg='角色名称已存在')

        # 校验权限字符串是否重复
        if await sys_role_crud.get_by_column(db, 'code', params.code):
            raise errors.ConflictError(msg='权限字符串已存在')

        # TODO: 校验菜单是否存在

        await sys_role_crud.create(db, params)

    @staticmethod
    async def update(*, db: 'AsyncSession', pk: int, params: SysRoleUpdate) -> int:
        """更新角色信息（包括关联关系 menus）"""
        # 校验角色是否存在
        role = await sys_role_crud.get(db, pk)
        if not role:
            raise errors.NotFoundError(msg='角色不存在')

        # 校验角色名称是否重复（排除当前角色）
        if params.name and params.name != role.name:
            existing_role = await sys_role_crud.get_by_column(db, column='name', value=params.name)
            if existing_role:
                raise errors.ConflictError(msg='角色名称已存在')

        # 校验权限字符串是否重复（排除当前角色）
        if params.code and params.code != role.code:
            existing_role = await sys_role_crud.get_by_column(db, column='code', value=params.code)
            if existing_role:
                raise errors.ConflictError(msg='权限字符串已存在')

        # TODO: 校验菜单是否存在

        return await sys_role_crud.update(db, pk, params)

    @staticmethod
    async def patch_status(*, db: 'AsyncSession', pk: int, params: SysRolePatchStatus) -> int:
        """更新角色状态"""
        await SysRoleService._get_role_or_404(db, pk)
        return await sys_role_crud.update_by_column(db, pk, 'status', params.status)

    @staticmethod
    async def patch_data_scope(*, db: 'AsyncSession', pk: int, params: SysRolePatchDataScope) -> int:
        """更新角色数据范围"""
        await SysRoleService._get_role_or_404(db, pk)

        # 当 data_scope=3（自定义部门）时, dept_ids 不能为空
        if params.data_scope == 3 and not params.dept_ids:
            raise errors.RequestError(msg='自定义数据权限时, 部门列表不能为空')

        # TODO: 校验部门是否存在

        return await sys_role_crud.update_data_scope(db, pk, params.data_scope, params.dept_ids)

    @staticmethod
    async def update_role_menus(*, db: 'AsyncSession', params: SysRoleMenuMap) -> int:
        """更新角色菜单映射（多对多关系维护）"""
        await SysRoleService._get_role_or_404(db, params.role_id)

        # TODO: 校验菜单是否存在

        return await sys_role_crud.update_role_menus(db, params.role_id, params.menu_ids)

    @staticmethod
    async def update_role_depts(*, db: 'AsyncSession', params: SysRoleDeptMap) -> int:
        """更新角色部门映射（多对多关系维护, 用于自定义的数据权限）"""
        await SysRoleService._get_role_or_404(db, params.role_id)

        # TODO: 校验部门是否存在

        return await sys_role_crud.update_role_depts(db, params.role_id, params.dept_ids)

    @staticmethod
    async def batch_assign_users(*, db: 'AsyncSession', params: SysRoleBatchUserAuth) -> dict[str, int | list[int]]:
        """批量分配用户到角色（多对多关系维护）

        处理逻辑：
            1. 校验角色是否存在
            2. 校验用户是否存在, 不存在的自动跳过
            3. 对有效的用户执行批量分配

        Returns:
            包含执行结果的字典：
            - assigned_count: 实际分配的数量
            - skipped_user_not_found: 不存在的用户ID列表
        """
        role_id = params.role_id
        user_ids = params.user_ids

        # 1. 校验角色是否存在
        await SysRoleService._get_role_or_404(db, role_id)

        # 2. 获取实际存在的用户ID
        from backend.app.admin.crud import sys_user_crud

        existing_user_ids = await sys_user_crud.get_existing_ids(db, user_ids)
        not_found_user_ids = list(set(user_ids) - set(existing_user_ids))

        # 3. 执行批量分配
        assigned_count = 0
        if existing_user_ids:
            assigned_count = await sys_role_crud.batch_assign_users(db, role_id, existing_user_ids)

        return {
            'assigned_count': assigned_count,
            'skipped_user_not_found': not_found_user_ids,
        }

    @staticmethod
    async def batch_revoke_users(*, db: 'AsyncSession', params: SysRoleBatchUserAuth) -> dict[str, int | list[int]]:
        """批量取消用户授权（多对多关系维护）

        处理逻辑：
            1. 校验角色是否存在
            2. 校验用户是否存在, 不存在的自动跳过
            3. 对有效的用户执行批量取消授权

        Returns:
            包含执行结果的字典：
            - revoked_count: 实际取消授权的数量
            - skipped_user_not_found: 不存在的用户ID列表
        """
        role_id = params.role_id
        user_ids = params.user_ids

        # 1. 校验角色是否存在
        await SysRoleService._get_role_or_404(db, role_id)

        # 2. 获取实际存在的用户ID
        from backend.app.admin.crud import sys_user_crud

        existing_user_ids = await sys_user_crud.get_existing_ids(db, user_ids)
        not_found_user_ids = list(set(user_ids) - set(existing_user_ids))

        # 3. 执行批量取消授权
        revoked_count = 0
        if existing_user_ids:
            revoked_count = await sys_role_crud.batch_revoke_users(db, role_id, existing_user_ids)

        return {
            'revoked_count': revoked_count,
            'skipped_user_not_found': not_found_user_ids,
        }

    @staticmethod
    async def batch_patch_status(*, db: 'AsyncSession', params: SysRoleBatchPatchStatus) -> dict[str, int | list[int]]:
        """批量更新角色状态

        处理逻辑：
            1. 校验角色是否存在, 不存在的自动跳过
            2. 对存在的角色执行批量更新

        Returns:
            包含执行结果的字典：
            - updated_count: 实际更新的数量
            - skipped_not_found: 不存在的角色ID列表
        """
        role_ids = params.role_ids
        status = params.status

        # 1. 获取实际存在的角色ID
        existing_ids = await sys_role_crud.get_existing_ids(db, role_ids)
        not_found_ids = list(set(role_ids) - set(existing_ids))

        # 2. 执行批量更新
        updated_count = await sys_role_crud.batch_update_status(db, existing_ids, status)

        return {
            'updated_count': updated_count,
            'skipped_not_found': not_found_ids,
        }

    @staticmethod
    async def delete(*, db: 'AsyncSession', pk: int) -> int:
        """删除角色

        注意：由于外键配置了 ondelete='CASCADE', 删除角色会级联清理关联关系
        """
        # 校验角色是否存在
        await SysRoleService._get_role_or_404(db, pk)

        # TODO: 检查该角色是否被用户使用（可选，根据业务需求）

        return await sys_role_crud.delete(db, pk=pk)

    @staticmethod
    async def batch_delete(*, db: 'AsyncSession', params: SysRoleBatchDelete) -> dict[str, int | list[int]]:
        """批量删除角色

        处理逻辑：
            1. 校验角色是否存在, 不存在的自动跳过
            2. 对存在的角色执行批量删除

        Returns:
            包含执行结果的字典：
            - deleted_count: 实际删除的数量
            - skipped_not_found: 不存在的角色ID列表
        """
        role_ids = params.role_ids

        # 1. 获取实际存在的角色ID
        existing_ids = await sys_role_crud.get_existing_ids(db, role_ids)
        not_found_ids = list(set(role_ids) - set(existing_ids))

        # 2. 执行批量删除
        deleted_count = await sys_role_crud.batch_delete(db, existing_ids)

        return {
            'deleted_count': deleted_count,
            'skipped_not_found': not_found_ids,
        }


sys_role_service = SysRoleService()
