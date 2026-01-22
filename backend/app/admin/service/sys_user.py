from typing import TYPE_CHECKING

from backend.app.admin.crud import sys_user_crud
from backend.app.admin.schema.sys_user import (
    SysUserBatchDelete,
    SysUserBatchPatchStatus,
    SysUserCreate,
    SysUserDetail,
    SysUserFilter,
    SysUserInfo,
    SysUserAdvancedFilter,
    SysUserPatchPassword,
    SysUserPatchProfile,
    SysUserPatchStatus,
    SysUserResetPassword,
    SysUserUpdate,
)
from backend.common.exception import errors
from backend.common.security.password import verify_password

from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SysUserService:
    """用户服务类"""

    @staticmethod
    async def _get_user_or_404(db: AsyncSession, pk: int):
        """获取用户, 不存在则抛出 NotFoundError"""
        user = await sys_user_crud.get(db, pk)
        if not user:
            raise errors.NotFoundError(msg='用户不存在')
        return user

    @staticmethod
    async def get_user_info(*, db: AsyncSession, pk: int) -> SysUserInfo:
        """获取用户信息"""
        user = await SysUserService._get_user_or_404(db, pk)
        return SysUserInfo.model_validate(user)

    @staticmethod
    async def get_user_info_by_username(*, db: AsyncSession, username: str) -> SysUserInfo:
        """获取用户信息"""
        user = await sys_user_crud.get_by_column(db, column='username', value=username)
        if not user:
            raise errors.NotFoundError(msg='用户不存在')
        return SysUserInfo.model_validate(user)

    @staticmethod
    async def get_user_detail(*, db: AsyncSession, pk: int) -> SysUserDetail:
        """获取用户详情"""
        user = await SysUserService._get_user_or_404(db, pk)
        return SysUserDetail.model_validate(user)

    @staticmethod
    async def get_list(*, params: SysUserFilter):
        """获取用户列表"""
        async with async_session.begin() as db:
            stmt = await sys_user_crud.get_list_select(params)
            result = await db.scalars(stmt)
            return result.all()

    @staticmethod
    async def get_advanced_list(*, params: SysUserAdvancedFilter):
        """获取用户列表"""
        async with async_session.begin() as db:
            stmt = await sys_user_crud.get_list_advanced_select(params)
            result = await db.scalars(stmt)
            return result.all()

    @staticmethod
    async def create(*, db: AsyncSession, params: SysUserCreate):
        """创建新用户"""

        # 校验用户名是否重复
        if await sys_user_crud.get_by_column(db, 'username', params.username):
            raise errors.ConflictError(msg='用户已存在')

        # 校验手机号是否重复
        if params.phone and await sys_user_crud.get_by_column(db, 'phone', params.phone):
            raise errors.ConflictError(msg='手机号已存在')

        # TODO: 校验部门是否存在
        # TODO: 校验角色是否存在

        await sys_user_crud.create(db, params)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, params: SysUserUpdate) -> int:
        """全量更新用户信息, 包括关联关系 roles"""
        # 校验用户是否存在
        user = await sys_user_crud.get(db, pk)
        if not user:
            raise errors.NotFoundError(msg='用户不存在')

        # 校验用户名是否重复（排除当前用户）
        if params.username != user.username:
            existing_user = await sys_user_crud.get_by_column(db, column='username', value=params.username)
            if existing_user:
                raise errors.ConflictError(msg='用户已存在')

        # TODO: 校验部门是否存在
        # TODO: 校验角色是否存在

        return await sys_user_crud.update(db, pk, params)

    @staticmethod
    async def patch_status(*, db: AsyncSession, pk: int, params: SysUserPatchStatus) -> int:
        """更新用户状态"""
        await SysUserService._get_user_or_404(db, pk)
        return await sys_user_crud.update_by_column(db, pk, 'status', params.status)

    @staticmethod
    async def patch_profile(*, db: AsyncSession, pk: int, params: SysUserPatchProfile) -> int:
        """更新用户资料"""
        await SysUserService._get_user_or_404(db, pk)
        return await sys_user_crud.update_profile(db, pk, params)

    @staticmethod
    async def patch_password(*, db: AsyncSession, pk: int, params: SysUserPatchPassword) -> int:
        """修改用户密码"""
        user = await SysUserService._get_user_or_404(db, pk)

        # 验证旧密码
        if user.password and params.old_password and not verify_password(params.old_password, user.password):
            raise errors.AuthorizationError(msg='旧密码错误')

        return await sys_user_crud.update_password(db, pk, params.new_password)

    @staticmethod
    async def reset_password(*, db: AsyncSession, pk: int, params: SysUserResetPassword) -> int:
        """重置用户密码"""
        await SysUserService._get_user_or_404(db, pk)
        return await sys_user_crud.update_password(db, pk, params.new_password)

    @staticmethod
    async def batch_patch_status(*, db: AsyncSession, params: SysUserBatchPatchStatus) -> dict[str, int | list[int]]:
        """批量更新用户状态

        处理逻辑：
            1. 校验用户是否存在，不存在的自动跳过
            2. 过滤掉超级管理员（不允许批量修改）
            3. 对剩余有效用户执行批量更新

        Returns:
            包含执行结果的字典：
            - updated_count: 实际更新的数量
            - skipped_not_found: 不存在的用户ID列表
            - skipped_superuser: 被跳过的超级管理员ID列表
        """
        user_ids = params.user_ids
        status = params.status

        # 1. 获取实际存在的用户ID
        existing_ids = await sys_user_crud.get_existing_ids(db, user_ids)
        not_found_ids = list(set(user_ids) - set(existing_ids))

        # 2. 获取超级管理员ID（从存在的用户中筛选）
        superuser_ids = await sys_user_crud.get_superuser_ids(db, existing_ids) if existing_ids else []

        # 3. 计算可更新的用户ID（存在且非超管）
        updatable_ids = list(set(existing_ids) - set(superuser_ids))

        # 4. 执行批量更新
        updated_count = await sys_user_crud.batch_update_status(db, updatable_ids, status)

        return {
            'updated_count': updated_count,
            'skipped_not_found': not_found_ids,
            'skipped_superuser': superuser_ids,
        }

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """删除用户"""
        # 校验用户是否存在
        user = await SysUserService._get_user_or_404(db, pk)

        # 不允许删除超级管理员
        if user.is_superuser:
            raise errors.ForbiddenError(msg='不允许删除超级管理员')

        return await sys_user_crud.delete(db, pk=pk)

    @staticmethod
    async def batch_delete(*, db: AsyncSession, params: SysUserBatchDelete) -> dict[str, int | list[int]]:
        """批量删除用户

        处理逻辑：
            1. 校验用户是否存在，不存在的自动跳过
            2. 过滤掉超级管理员（不允许批量删除）
            3. 对剩余有效用户执行批量删除

        Returns:
            包含执行结果的字典：
            - deleted_count: 实际删除的数量
            - skipped_not_found: 不存在的用户ID列表
            - skipped_superuser: 被跳过的超级管理员ID列表
        """
        user_ids = params.user_ids

        # 1. 获取实际存在的用户ID
        existing_ids = await sys_user_crud.get_existing_ids(db, user_ids)
        not_found_ids = list(set(user_ids) - set(existing_ids))

        # 2. 获取超级管理员ID（从存在的用户中筛选）
        superuser_ids = await sys_user_crud.get_superuser_ids(db, existing_ids) if existing_ids else []

        # 3. 计算可删除的用户ID（存在且非超管）
        deletable_ids = list(set(existing_ids) - set(superuser_ids))

        # 4. 执行批量删除
        deleted_count = await sys_user_crud.batch_delete(db, deletable_ids)

        return {
            'deleted_count': deleted_count,
            'skipped_not_found': not_found_ids,
            'skipped_superuser': superuser_ids,
        }


sys_user_service = SysUserService()
