#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model.user import User
from backend.app.admin.schema.user import UserRegisterParams
from backend.common.security.jwt import get_hash_password


class UserCRUD(CRUDPlus[User]):
    async def get(self, db: AsyncSession, pk: int) -> User | None:
        """根据 pk 获取用户详情"""
        return await self.select_model(db, pk)

    async def get_by_column(self, db: AsyncSession, column: str, value: str):
        """根据指定列名和值获取 详情"""
        return await self.select_model_by_column(db, **{column: value})  # type: ignore

    async def register_by_username(self, db: AsyncSession, params: UserRegisterParams):
        """根据用户名、密码创建用户"""
        salt = bcrypt.gensalt()
        params.password = get_hash_password(params.password, salt)

        dict_params = params.model_dump()
        dict_params.update({'username': params.username, 'nickname': params.username, 'salt': salt})

        user = self.model(**dict_params)
        db.add(user)


user_crud = UserCRUD(User)
