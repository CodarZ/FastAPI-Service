#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from fastapi.security import HTTPBasicCredentials

from backend.app.admin.schema.user import UserInfo
from backend.common.security.jwt import create_access_token

__all__ = ['auth_service']


class AuthService:
    """认证服务类"""

    async def swagger_login(self, *, obj: HTTPBasicCredentials):
        """Swagger 登录"""

        # TODO 查询 user 数据库
        a_token = await create_access_token(
            1,
            False,
            # extra info
            swagger=True,
        )
        return a_token.access_token, UserInfo(
            id=1,
            username=obj.username,
            nickname='Swagger',
            avatar='https://example.com/avatar.png',
            email=None,
            phone=None,
            uuid='12345678-1234-5678-1234-567812345678',
        )


auth_service = AuthService()
