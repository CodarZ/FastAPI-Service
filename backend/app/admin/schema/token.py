#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import Field

from backend.app.admin.schema.user import UserDetail
from backend.common.schema import SchemaBase


class SwaggerToken(SchemaBase):
    """Swagger 认证令牌"""

    access_token: str = Field(description='访问令牌')
    user: UserDetail = Field(description='用户信息')


class AccessTokenBase(SchemaBase):
    """访问令牌基础模型"""

    access_token: str = Field(description='访问令牌')
    expire_time: datetime = Field(description='令牌过期时间')
    session_uuid: str = Field(description='会话 UUID')


class AuthLoginToken(AccessTokenBase):
    """获取登录令牌"""

    user: UserDetail = Field(description='用户信息')


class AuthLoginParams(SchemaBase):
    """用户登录认证参数"""

    username: str = Field(description='用户名')
    password: str = Field(description='密码')
