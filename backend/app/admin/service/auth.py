#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Any

from fastapi import BackgroundTasks, Request, Response
from fastapi.security import HTTPBasicCredentials

from backend.app.admin.crud.user import user_crud
from backend.app.admin.model.user import User
from backend.common.exception import errors
from backend.common.security.jwt import create_access_token, verify_password
from backend.database.postgresql import AsyncSession, async_db_session


class AuthService:
    @staticmethod
    async def user_verify(db: AsyncSession, username: str, password: str) -> User:
        user = await user_crud.get_by_column(db, 'username', username)

        if not user:
            raise errors.NotFoundError(msg='用户不存在')

        if user.password is None:
            raise errors.AuthorizationError(msg='该用户没有设置密码')
        if not verify_password(password, user.password):
            raise errors.AuthorizationError(msg='用户名或密码有误')

        if not user.status:
            raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')

        return user

    async def swagger_login(self, *, params: HTTPBasicCredentials) -> tuple[str, User]:
        async with async_db_session.begin() as db:
            user = await self.user_verify(db, params.username, params.password)
            await user_crud.update_login_time(db, params.username)
            access_token = await create_access_token(
                user.id,
                multi_login=user.is_multi_login,
                # extra info
                swagger=True,
            )
            return access_token.access_token, user

    async def login(self, *, request: Request, response: Response, params: Any, background_tasks: BackgroundTasks):
        pass

    @staticmethod
    async def logout(*, request: Request, response: Response):
        pass


auth_service: AuthService = AuthService()
