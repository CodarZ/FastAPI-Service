#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import Field

from backend.app.admin.schema.user import UserInfo
from backend.common.enum.custom import StatusEnum
from backend.common.schema import SchemaBase


class TokenBase(SchemaBase):
    access_token: str = Field(description='访问令牌')
    expire_time: datetime = Field(description='访问令牌过期时间')
    session_uuid: str = Field(description='会话唯一标识符 uuid')


class SwaggerToken(SchemaBase):
    """Swagger 认证"""

    access_token: str = Field(description='访问令牌')
    token_type: str = Field('Bearer', description='令牌类型')
    user: UserInfo = Field(description='用户信息')


class TokenLogin(TokenBase):
    """登录令牌"""

    user: UserInfo = Field(description='用户信息')


class TokenRefresh(TokenBase):
    """获取新的访问令牌"""


class TokenKickout(SchemaBase):
    """踢出令牌"""

    session_uuid: str = Field(description='会话 UUID')


class TokenInfo(SchemaBase):
    """令牌信息"""

    id: int = Field(description='Token ID')
    access_token: str = Field(description='访问令牌')
    expire_time: datetime = Field(description='访问令牌过期时间')
    session_uuid: str = Field(description='会话唯一标识符 uuid')

    username: str = Field(description='用户名')
    nickname: str = Field(description='昵称')
    ip: str = Field(description='IP 地址')
    os: str = Field(description='操作系统')
    browser: str = Field(description='浏览器')
    device: str = Field(description='设备')
    status: StatusEnum = Field(description='状态')
    last_login_time: str = Field(description='最后登录时间')
