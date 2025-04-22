#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

from pydantic import ConfigDict, Field

from backend.common.enum.custom import StatusEnum
from backend.common.schema import SchemaBase


class OperationLog(SchemaBase):
    """操作日志"""

    username: str | None = Field(None, description='用户名')

    title: str = Field(description='操作标题')
    status: StatusEnum = Field(description='操作状态（0异常 1正常）')

    path: str = Field(description='请求路径')
    trace_id: str = Field(description='请求跟踪 ID')
    method: str = Field(description='请求类型')
    args: dict[str, Any] | None = Field(None, description='请求参数')
    code: str = Field(description='操作状态码')
    msg: str | None = Field(None, description='提示消息')
    cost_time: float = Field(0.0, description='请求耗时（ms）')

    ip: str = Field(description='IP地址')
    country: str | None = Field(None, description='国家')
    region: str | None = Field(None, description='地区')
    city: str | None = Field(None, description='城市')

    user_agent: str = Field(description='请求头')
    os: str | None = Field(None, description='操作系统')
    browser: str | None = Field(None, description='浏览器')
    device: str | None = Field(None, description='设备')

    operate_time: str = Field(description='操作时间')


class OperationLogCreate(OperationLog):
    """创建操作日志"""


class OperationLogUpdate(OperationLog):
    """更新操作日志"""


class OperationLogInfo(OperationLog):
    """操作日志数据库模型"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='操作日志 ID')
    created_time: str = Field(description='创建时间')
