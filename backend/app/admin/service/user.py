#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.admin.crud.user import user_crud
from backend.app.admin.model.user import User
from backend.app.admin.schema.user import (
    UserDetailWithSocials,
    UserListQueryParams,
    UserRegisterParams,
    UserUpdateParams,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.database.postgresql import async_db_session


class UserService:
    @staticmethod
    async def register(*, params: UserRegisterParams) -> None:
        """注册用户"""

        async with async_db_session.begin() as db:
            if await user_crud.get_by_column(db, 'username', params.username):
                raise errors.ValidationError(msg='该用户已经存在')
            if not params.password:
                raise errors.ValidationError(msg='密码不能为空')
            if not params.username:
                raise errors.ValidationError(msg='用户名不能为空')

            await user_crud.register_by_username(db, params)

    @staticmethod
    async def get_userinfo(*, pk: int):
        """根据 pk 获取用户信息"""
        async with async_db_session.begin() as db:
            user = await user_crud.get(db, pk)
            if not user:
                raise errors.NotFoundError(msg='用户不存在')
            return user

    @staticmethod
    async def get_userinfo_with_socials(*, pk: int) -> UserDetailWithSocials:
        """根据 pk 获取包含社交绑定状态的用户信息"""

        async with async_db_session.begin() as db:
            stmt = select(User).options(selectinload(User.socials)).where(User.id == pk)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise errors.NotFoundError(msg='用户不存在')

            return UserDetailWithSocials.model_validate(user)

    @staticmethod
    async def get_list(*, params: UserListQueryParams):
        """获取用户分页列表"""
        async with async_db_session.begin() as db:
            stmt = await user_crud.get_list_select(params)

            return await paging_data(db, stmt)

    @staticmethod
    async def delete(*, pk: int) -> int:
        """删除用户"""

        if pk == 1:
            raise errors.ForbiddenError(msg='超级管理员禁止删除')

        async with async_db_session.begin() as db:
            user = await user_crud.get(db, pk)
            if not user:
                raise errors.NotFoundError(msg='用户不存在')
            count = await user_crud.delete(db, pk)

            return count

    @staticmethod
    async def update(*, pk: int, params: UserUpdateParams) -> int:
        """更新用户信息"""

        if pk == 1:
            raise errors.ForbiddenError(msg='超级管理员禁止修改')
        async with async_db_session.begin() as db:
            # 检查用户是否存在
            user = await user_crud.get(db, pk)

            if not user:
                raise errors.NotFoundError(msg='用户不存在')

            # 检查用户名是否重复（如果要更新用户名）
            if params.username and params.username != user.username:
                existing_user = await user_crud.get_by_column(db, 'username', params.username)
                if existing_user:
                    raise errors.ValidationError(msg='该用户名已存在')

            # 检查邮箱是否重复（如果要更新邮箱）
            if params.email and params.email != user.email:
                existing_user = await user_crud.get_by_column(db, 'email', params.email)
                if existing_user:
                    raise errors.ValidationError(msg='该邮箱已存在')

            # 检查手机号是否重复（如果要更新手机号）
            if params.phone and params.phone != user.phone:
                existing_user = await user_crud.get_by_column(db, 'phone', params.phone)
                if existing_user:
                    raise errors.ValidationError(msg='该手机号已存在')

            # 验证密码（如果要更新密码）
            if params.password is not None:
                if not params.password:
                    raise errors.ValidationError(msg='密码不能为空')

            # 执行更新
            count = await user_crud.update(db, pk, params)
            return count


user_service = UserService()
