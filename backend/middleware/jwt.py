#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from fastapi import Response
from fastapi.requests import HTTPConnection
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError, BaseUser

from backend.app.admin.schema.user import UserInfoWithRelations
from backend.common.exception.errors import TokenError
from backend.common.logger import log
from backend.common.response.code import CustomResponseCode
from backend.common.security.jwt import jwt_authentication
from backend.core.config import settings
from backend.utils.serializers import MsgSpecJSONResponse


class _AuthenticationError(AuthenticationError):
    """重写内部认证错误类"""

    def __init__(
        self, *, code: int | None = None, msg: str | None = None, headers: dict[str, Any] | None = None
    ) -> None:
        self.code = code
        self.msg = msg
        self.headers = headers


class _UserInfo(BaseUser, UserInfoWithRelations):
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return str(self.id)


class JWTAuthMiddleware(AuthenticationBackend):
    """JWT 认证中间件"""

    @staticmethod
    def auth_exception_handler(_: HTTPConnection, exc: AuthenticationError | _AuthenticationError) -> Response:
        """覆盖内部认证错误处理"""
        return MsgSpecJSONResponse(
            content={
                'code': getattr(exc, 'code', CustomResponseCode.HTTP_500.code),
                'msg': getattr(exc, 'msg', CustomResponseCode.HTTP_500.msg),
                'data': None,
            },
            status_code=getattr(exc, 'code', CustomResponseCode.HTTP_500.code),
        )

    async def authenticate(self, conn: HTTPConnection):
        """认证请求"""
        token = conn.headers.get('Authorization')
        if token is None:
            return None
        if conn.url.path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
            return None

        scheme, token = get_authorization_scheme_param(token)
        if scheme.lower() != 'bearer':
            return None

        try:
            user = await jwt_authentication(token)
            user = _UserInfo(**user.model_dump())
        except TokenError as exc:
            raise _AuthenticationError(
                code=exc.code, msg=exc.detail, headers=dict(exc.headers) if exc.headers is not None else None
            )
        except Exception as e:
            log.error(f'JWT 授权异常：{e}')
            raise _AuthenticationError(
                code=getattr(e, 'code', CustomResponseCode.HTTP_500.code),
                msg=getattr(e, 'msg', CustomResponseCode.HTTP_500.msg),
            )

        # https://www.starlette.io/authentication/
        return AuthCredentials(['authenticated']), user
