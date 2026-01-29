from typing import TYPE_CHECKING

from backend.app.admin.crud import sys_user_crud
from backend.app.admin.schema.sys_user import (
    SysUserBatchDelete,
    SysUserBatchPatchStatus,
    SysUserCreate,
    SysUserDetail,
    SysUserFilter,
    SysUserInfo,
    SysUserListItem,
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
    async def _get_user_or_404(db: 'AsyncSession', pk: int):
        """获取用户, 不存在则抛出 NotFoundError"""
        user = await sys_user_crud.get(db, pk)
        if not user:
            raise errors.NotFoundError(msg='用户不存在')
        return user

    @staticmethod
    async def get_user_info(*, db: 'AsyncSession', pk: int) -> SysUserInfo:
        """获取用户信息"""
        user = await SysUserService._get_user_or_404(db, pk)
        return SysUserInfo.model_validate(user)

    @staticmethod
    async def get_current_user(*, db: 'AsyncSession', user_id: int) -> SysUserDetail:
        """获取当前用户详细信息

        用于验证当前登录用户的状态, 包括：
        - 用户是否存在
        - 用户是否被禁用
        - 用户所属部门是否被禁用
        - 用户所属角色是否全部被锁定
        """
        user = await SysUserService._get_user_or_404(db, user_id)

        if not user.status:
            raise errors.TokenError(msg='用户已被禁用, 请联系系统管理员')

        if user.dept_id and user.dept and not user.dept.status:
            raise errors.TokenError(msg='用户所属部门已被禁用, 请联系系统管理员')

        if user.roles:
            role_status = [role.status for role in user.roles]
            if all(status == 0 for status in role_status):
                raise errors.AuthorizationError(msg='用户所属角色已被锁定, 请联系系统管理员')

        return SysUserDetail.model_validate(user)

    @staticmethod
    async def get_user_info_by_username(*, db: 'AsyncSession', username: str) -> SysUserInfo:
        """根据用户名获取用户信息"""
        user = await sys_user_crud.get_by_column(db, column='username', value=username)
        if not user:
            raise errors.NotFoundError(msg='用户不存在')
        return SysUserInfo.model_validate(user)

    @staticmethod
    async def get_user_detail(*, db: 'AsyncSession', pk: int) -> SysUserDetail:
        """获取用户详情"""
        user = await SysUserService._get_user_or_404(db, pk)
        return SysUserDetail.model_validate(user)

    @staticmethod
    async def get_list(*, params: SysUserFilter) -> list[SysUserListItem]:
        """获取用户列表（基础过滤）"""
        async with async_session.begin() as db:
            stmt = await sys_user_crud.get_list_select(params)
            result = await db.scalars(stmt)
            users = result.all()
            # 在 session 内完成序列化, 避免 DetachedInstanceError
            return [SysUserListItem.model_validate(user) for user in users]

    @staticmethod
    async def create(*, db: 'AsyncSession', params: SysUserCreate):
        """创建新用户"""
        # 校验用户名是否重复
        if await sys_user_crud.get_by_column(db, 'username', params.username):
            raise errors.ConflictError(msg='用户名已存在')

        # 校验手机号是否重复（如果提供了手机号）
        if params.phone:
            existing_phone = await sys_user_crud.get_by_column(db, 'phone', params.phone)
            if existing_phone:
                raise errors.ConflictError(msg='手机号已存在')

        # 校验邮箱是否重复（如果提供了邮箱）
        if params.email:
            existing_email = await sys_user_crud.get_by_column(db, 'email', params.email)
            if existing_email:
                raise errors.ConflictError(msg='邮箱已存在')

        # TODO: 校验部门是否存在
        # TODO: 校验角色是否存在

        await sys_user_crud.create(db, params)

    @staticmethod
    async def update(*, db: 'AsyncSession', pk: int, params: SysUserUpdate) -> int:
        """全量更新用户信息（包括关联关系 roles）"""
        # 校验用户是否存在
        user = await sys_user_crud.get(db, pk)
        if not user:
            raise errors.NotFoundError(msg='用户不存在')

        # 校验用户名是否重复（排除当前用户）
        if params.username != user.username:
            existing_user = await sys_user_crud.get_by_column(db, column='username', value=params.username)
            if existing_user:
                raise errors.ConflictError(msg='用户名已存在')

        # 校验手机号是否重复（如果提供了手机号且与当前不同）
        if params.phone and params.phone != user.phone:
            existing_phone = await sys_user_crud.get_by_column(db, 'phone', params.phone)
            if existing_phone:
                raise errors.ConflictError(msg='手机号已存在')

        # 校验邮箱是否重复（如果提供了邮箱且与当前不同）
        if params.email and params.email != user.email:
            existing_email = await sys_user_crud.get_by_column(db, 'email', params.email)
            if existing_email:
                raise errors.ConflictError(msg='邮箱已存在')

        # # 校验邮箱是否重复（如果提供了邮箱且与当前不同）
        # if params.email and params.email != user.email:
        #     existing_email = await sys_user_crud.get_by_column(db, 'email', params.email)
        #     if existing_email:
        #         raise errors.ConflictError(msg='邮箱已存在')

        # TODO: 校验部门是否存在
        # TODO: 校验角色是否存在

        return await sys_user_crud.update(db, pk, params)

    @staticmethod
    async def patch_status(*, db: 'AsyncSession', pk: int, params: SysUserPatchStatus) -> int:
        """更新用户状态"""
        user = await SysUserService._get_user_or_404(db, pk)

        # 不允许停用超级管理员
        if user.is_superuser and params.status == 0:
            raise errors.ForbiddenError(msg='不允许停用超级管理员')

        return await sys_user_crud.update_by_column(db, pk, 'status', params.status)

    @staticmethod
    async def patch_profile(*, db: 'AsyncSession', pk: int, params: SysUserPatchProfile) -> int:
        """更新用户个人资料"""
        await SysUserService._get_user_or_404(db, pk)

        # # 校验手机号是否重复（如果提供了手机号）
        # if params.phone:
        #     existing = await sys_user_crud.get_by_column(db, 'phone', params.phone)
        #     if existing and existing.id != pk:
        #         raise errors.ConflictError(msg='手机号已存在')

        # # 校验邮箱是否重复（如果提供了邮箱）
        # if params.email:
        #     existing = await sys_user_crud.get_by_column(db, 'email', params.email)
        #     if existing and existing.id != pk:
        #         raise errors.ConflictError(msg='邮箱已存在')

        return await sys_user_crud.update_profile(db, pk, params)

    @staticmethod
    async def patch_password(*, db: 'AsyncSession', pk: int, params: SysUserPatchPassword) -> int:
        """修改用户密码（需要旧密码验证）"""
        user = await SysUserService._get_user_or_404(db, pk)

        # 验证旧密码
        if params.old_password:
            if not user.password:
                raise errors.RequestError(msg='用户未设置密码')
            if not verify_password(params.old_password, user.password):
                raise errors.AuthorizationError(msg='旧密码错误')

        return await sys_user_crud.update_password(db, pk, params.new_password)

    @staticmethod
    async def reset_password(*, db: 'AsyncSession', pk: int, params: SysUserResetPassword) -> int:
        """重置用户密码（管理员操作, 无需旧密码）"""
        await SysUserService._get_user_or_404(db, pk)
        return await sys_user_crud.update_password(db, pk, params.new_password)

    @staticmethod
    async def batch_patch_status(*, db: 'AsyncSession', params: SysUserBatchPatchStatus) -> dict[str, int | list[int]]:
        """批量更新用户状态

        处理逻辑：
            1. 校验用户是否存在, 不存在的自动跳过
            2. 过滤掉超级管理员（不允许批量修改超级管理员状态）
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
    async def delete(*, db: 'AsyncSession', pk: int) -> int:
        """删除用户

        注意：不允许删除超级管理员
        """
        # 校验用户是否存在
        user = await SysUserService._get_user_or_404(db, pk)

        # 不允许删除超级管理员
        if user.is_superuser:
            raise errors.ForbiddenError(msg='不允许删除超级管理员')

        return await sys_user_crud.delete(db, pk=pk)

    @staticmethod
    async def batch_delete(*, db: 'AsyncSession', params: SysUserBatchDelete) -> dict[str, int | list[int]]:
        """批量删除用户

        处理逻辑：
            1. 校验用户是否存在, 不存在的自动跳过
            2. 过滤掉超级管理员（不允许批量删除超级管理员）
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

    @staticmethod
    async def update_login_time(*, db: 'AsyncSession', user_id: int) -> int:
        """更新用户最后登录时间"""
        return await sys_user_crud.update_login_time(db, user_id)


sys_user_service = SysUserService()
