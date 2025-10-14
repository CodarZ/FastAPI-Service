#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import BackgroundTasks, Request, Response
from fastapi.security import HTTPBasicCredentials

from backend.app.admin.crud.user import user_crud
from backend.app.admin.model.user import User
from backend.app.admin.schema.token import AuthLoginParams, AuthLoginToken
from backend.app.admin.schema.user import UserDetail
from backend.common.exception import errors
from backend.common.log import log
from backend.common.security.jwt import create_access_token, create_refresh_token, verify_password
from backend.core.config import settings
from backend.database.postgresql import AsyncSession, async_db_session
from backend.utils.timezone import timezone


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

    async def login(
        self, *, request: Request, response: Response, params: AuthLoginParams, background_tasks: BackgroundTasks
    ) -> AuthLoginToken:
        async with async_db_session.begin() as db:
            user = None

            try:
                user = await self.user_verify(db, params.username, params.password)

                await user_crud.update_login_time(db, user.username)
                await db.refresh(user)
                access_token = await create_access_token(
                    user.id,
                    multi_login=user.is_multi_login,
                    # extra info
                    username=user.username,
                    nickname=user.nickname,
                    last_login_time=timezone.to_str(user.last_login_time) if user.last_login_time else None,
                    # ip=request.state.ip if request.state.ip else None,
                    os=request.state.os,
                    browser=request.state.browser,
                    device=request.state.device,
                )

                refresh_token = await create_refresh_token(
                    access_token.session_uuid,
                    user.id,
                    multi_login=user.is_multi_login,
                )

                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=timezone.to_utc(refresh_token.expire_time),
                    httponly=True,
                )
            except errors.NotFoundError as e:
                log.error('登陆错误: 用户名不存在')
                raise errors.NotFoundError(msg=e.msg if e.msg else '用户不存在')
            except (errors.RequestError, errors.CustomError) as e:
                if not user:
                    log.error('登陆错误: 用户密码有误')

                raise errors.RequestError(msg=e.msg if e.msg else '用户密码错误')
            except Exception as e:
                log.error(f'登陆未知错误: {e}')
                raise

            else:
                data = AuthLoginToken(
                    access_token=access_token.access_token,
                    expire_time=access_token.expire_time,
                    session_uuid=access_token.session_uuid,
                    user=UserDetail.model_validate(user),
                )
                return data

    @staticmethod
    async def logout(*, request: Request, response: Response):
        pass


auth_service: AuthService = AuthService()
