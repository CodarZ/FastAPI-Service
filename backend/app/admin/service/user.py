#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.app.admin.crud.user import user_crud
from backend.app.admin.schema.user import UserCreateEmail
from backend.common.exception import errors
from backend.database.mysql import async_db_session


class UserService:
    @staticmethod
    async def register(*, obj: UserCreateEmail) -> None:
        """使用邮箱-密码注册用户"""

        async with async_db_session.begin() as db:
            if not obj.password:
                raise errors.ValidationError(msg='密码不能为空')
            if not obj.email:
                raise errors.ValidationError(msg='邮箱不能为空')

            user = await user_crud.get_by_column(db, 'email', obj.email)
            if user:
                raise errors.ValidationError(msg='邮箱已被注册')

            await user_crud.create_by_email(db, obj)


user_service = UserService()
