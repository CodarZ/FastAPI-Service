#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any

from pydantic import Field

from backend.common.enum.custom import StatusEnum
from backend.common.schema import SchemaBase


class OperationLogSchemaBase(SchemaBase):
    """基础模型"""

    username: str | None = Field(None, description='操作用户')
    trace_id: str = Field(description='请求跟踪 ID')

    moudle: str = Field(description='操作模块')
    path: str = Field(description='请求路径')
    method: str = Field(description='请求方式')
    code: str = Field(description='操作状态码')
    args: dict[str, Any] | None = Field(None, description='请求参数')
    msg: str | None = Field(None, description='提示消息')
    cost_time: float = Field(description='请求耗时（ms）')

    ip: str = Field(description='IP地址')
    country: str | None = Field(None, description='国家')
    region: str | None = Field(None, description='地区')
    city: str | None = Field(None, description='城市')

    user_agent: str = Field(description='请求头')
    os: str | None = Field(None, description='操作系统')
    browser: str | None = Field(None, description='浏览器')
    device: str | None = Field(None, description='设备')
    status: StatusEnum = Field(description='操作状态（0异常 1正常）')

    operated_time: datetime = Field(description='操作时间')


class OperationLogCreateParams(OperationLogSchemaBase):
    """创建参数"""


class OperationLogUpdateParams(OperationLogSchemaBase):
    """更新参数"""


class OperationLogListQueryParams(SchemaBase):
    """列表搜索参数"""

    username: str | None = Field(default=None, description='操作用户')

    moudle: str | None = Field(default=None, description='操作模块')
    path: str | None = Field(default=None, description='请求路径')
    method: str | None = Field(default=None, description='请求方式')
    code: str | None = Field(default=None, description='操作状态码')

    ip: str | None = Field(default=None, description='IP地址')
    country: str | None = Field(default=None, description='国家')
    region: str | None = Field(default=None, description='地区')
    city: str | None = Field(default=None, description='城市')

    status: StatusEnum | None = Field(default=None, description='操作状态（0异常 1正常）')


class OperationLogDetail(OperationLogSchemaBase):
    """详情"""

    id: int = Field(description='日志 ID')

    created_time: datetime = Field(description='创建时间')


class OperationLogDeleteParams(SchemaBase):
    """删除参数"""

    pks: list[int] = Field(description='操作日志 ID 列表')
