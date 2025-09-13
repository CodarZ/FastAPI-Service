#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class UserSocialSchemaBase(SchemaBase):
    """用户社交绑定基础信息"""

    model_config = ConfigDict(from_attributes=True)

    open_id: str = Field(description='用户唯一平台标识 open_id')
    platform: str = Field(description='社交平台名称')
    union_id: str | None = Field(default=None, description='平台标识')


class UserSocialDetail(UserSocialSchemaBase):
    """用户社交绑定详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='绑定记录 ID')
    bound_time: datetime = Field(description='绑定时间')
    user_id: int | None = Field(description='用户关联ID')


class UserSocialBindParams(UserSocialSchemaBase):
    """社交平台绑定参数"""

    pass


class UserSocialUnbindParams(SchemaBase):
    """社交平台解绑参数"""

    platform: str = Field(description='要解绑的社交平台')
