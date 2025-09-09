#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dataclasses

from fastapi import Response

from backend.common.enum.custom import StatusEnum


@dataclasses.dataclass
class UserAgentInfo:
    """User Agent"""

    user_agent: str  # 原始的 User-Agent 字符串
    os: str | None = None  # 操作系统（如 Windows, macOS, iOS, Android）
    os_version: str | None = None  # 操作系统版本（如 10.0.1, Big Sur, etc.）
    browser: str | None = None  # 浏览器类型（如 Chrome, Safari, Firefox）
    browser_version: str | None = None  # 浏览器版本（如 91.0.4472.124）
    device: str | None = None  # 设备类型（如 Mobile, Tablet, Desktop）
    device_model: str | None = None  # 具体的设备型号（如 iPhone 12, Galaxy S21）


@dataclasses.dataclass
class RequestCallNext:
    """中间件、异常处理器或请求处理链中传递请求的处理状态信息"""

    code: str
    msg: str
    status: StatusEnum
    err: Exception | None
    response: Response
