#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import User
from backend.app.admin.model.role import Role
from backend.app.admin.schema.user import UserCreate, UserCreateEmail, UserUpdate
from backend.common.security.jwt import get_hash_password
from backend.utils.timezone import timezone
from backend.utils.tool import generate_random_str


class CRUDUser(CRUDPlus[User]):
    async def get(self, db: AsyncSession, user_id: int):
        """根据 user_id 获取用户详情"""
        return await self.select_model(db, user_id)

    async def get_by_column(self, db: AsyncSession, column: str, value: str):
        """根据指定列名和值获取用户详情

        如：username、email、phone 等列
        """
        return await self.select_model_by_column(db, **{column: value})

    async def update_login_time(self, db: AsyncSession, user_id: int, username: str):
        """更新用户登录时间"""
        return await self.update_model(db, user_id, {'last_login_time': timezone.now()}, username=username)

    async def create_by_email(self, db: AsyncSession, obj: UserCreateEmail):
        """根据邮箱注册用户"""
        salt = bcrypt.gensalt()
        nickname = username = generate_random_str('user_')

        obj.password = get_hash_password(obj.password, salt)
        dict_obj = obj.model_dump()

        dict_obj.update({'is_staff': True, 'salt': salt, 'username': username, 'nickname': nickname})

        user = self.model(**dict_obj)
        db.add(user)

    async def add(self, db: AsyncSession, obj: UserCreate) -> None:
        salt = bcrypt.gensalt()
        obj.password = get_hash_password(obj.password if obj.password else '123456', salt)
        dict_obj = obj.model_dump(exclude={'roles'})
        dict_obj.update({'salt': salt})

        user = self.model(**dict_obj)

        if obj.role_ids:
            role_list = []
            for role_id in obj.role_ids:
                role_list.append(await db.get(Role, role_id))
            user.roles.extend(role_list)

        db.add(user)

    async def update(self, db: AsyncSession, user_id: int, obj: UserUpdate):
        """更新用户信息"""


user_crud = CRUDUser(User)
