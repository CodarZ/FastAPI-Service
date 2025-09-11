#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from backend.app.admin.crud.user import user_crud
from backend.app.admin.schema.user import UserRegisterParams
from backend.common.exception import errors
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


user_service = UserService()
