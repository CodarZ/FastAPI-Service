#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import Field

from backend.common.enum.custom import LoginLogStatusEnum
from backend.common.schema import SchemaBase


class LoginLogSchemaBase(SchemaBase):
    """登录日志基础模型"""

    username: str | None = Field(None, description='用户名')
    user_uuid: str | None = Field(None, description='用户 UUID')
    status: LoginLogStatusEnum = Field(description='登录状态（FAIL 异常、 SUCCESS 正常）')

    ip: str | None = Field(None, description='IP地址')
    country: str | None = Field(None, description='国家')
    region: str | None = Field(None, description='地区')
    city: str | None = Field(None, description='城市')

    user_agent: str | None = Field(None, description='请求头')
    os: str | None = Field(None, description='操作系统')
    browser: str | None = Field(None, description='浏览器')
    device: str | None = Field(None, description='设备')

    msg: str | None = Field(None, description='消息')
    login_time: datetime = Field(description='登录时间')


class LoginLogCreateParams(LoginLogSchemaBase):
    """创建参数"""


class LoginLogUpdateParams(LoginLogSchemaBase):
    """更新参数"""


class LoginLogDeleteParams(SchemaBase):
    """删除参数"""

    pks: list[int] = Field(description='操作日志 ID 列表')


class LoginLogDetail(LoginLogSchemaBase):
    """详情"""

    id: int = Field(description='日志 ID')

    created_time: datetime = Field(description='创建时间')


class LoginLogListQueryParams(SchemaBase):
    """列表搜索参数"""

    user_uuid: str | None = Field(None, description='用户 UUID')
    username: str | None = Field(None, description='操作用户')
    status: LoginLogStatusEnum | None = Field(None, description='登录状态（FAIL 异常、 SUCCESS 正常）')

    ip: str | None = Field(None, description='IP地址')
    country: str | None = Field(None, description='国家')
    region: str | None = Field(None, description='地区')
    city: str | None = Field(None, description='城市')

    user_agent: str | None = Field(None, description='请求头')
    # os: str | None = Field(None, description='操作系统')
    # browser: str | None = Field(None, description='浏览器')
    device: str | None = Field(None, description='设备')

    login_time: datetime | None = Field(None, description='登录时间')
