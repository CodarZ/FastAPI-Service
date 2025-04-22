#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import Field

from backend.common.enum.custom import UserSocialEnum
from backend.common.schema import SchemaBase


class UserSocialBase(SchemaBase):
    source: UserSocialEnum = Field(description='用户来源')
    open_id: str | None = Field(default=None, description='用户 open id')
    uid: str | None = Field(default=None, description='用户 UID')
    union_id: str | None = Field(default=None, description='用户 union id')
    scope: str | None = Field(default=None, description='用户 授予权限')
    code: str | None = Field(default=None, description='授权 Code')


class UserSocialCreate(UserSocialBase):
    """创建 用户社交信息"""

    user_id: int = Field(description='用户关联ID')


class UserSocialUpdate(UserSocialBase):
    """更新 用户社交信息"""
