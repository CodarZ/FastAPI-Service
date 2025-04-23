#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enum.custom import StatusEnum
from backend.common.schema import SchemaBase


class LoginLogBase(SchemaBase):
    """登录日志"""

    user_uuid: str = Field(description='用户 UUID')
    username: str = Field(description='用户名')
    status: StatusEnum = Field(description='登录状态(0失败 1成功)')
    msg: str = Field(description='提示消息')

    ip: str = Field(description='登录 IP 地址')
    country: str | None = Field(description='国家')
    region: str | None = Field(description='地区')
    city: str | None = Field(description='城市')

    user_agent: str = Field(description='请求头')
    os: str | None = Field(description='操作系统')
    browser: str | None = Field(description='浏览器')
    device: str | None = Field(description='设备')

    login_time: datetime = Field(description='登录时间')


class LoginLogCreate(LoginLogBase):
    """登录日志创建"""


class LoginLogUpdate(LoginLogBase):
    """登录日志更新"""


class LoginLogInfo(LoginLogBase):
    """登录日志详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='日志 ID')
    created_time: datetime = Field(description='创建时间')
