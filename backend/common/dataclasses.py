#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dataclasses

from datetime import datetime

from fastapi import Response

from backend.common.enum.custom import StatusEnum


@dataclasses.dataclass
class IpInfo:
    """IP 地理位置信息数据类

    用于存储和处理 IP 地址相关的地理位置信息, 包括国家、地区、城市等详细定位数据。
    """

    ip: str  # IP 地址, 支持 IPv4 和 IPv6 格式
    country: str | None = None  # 国家/地区
    region: str | None = None  # 省份/州/行政区
    city: str | None = None  # 城市
    district: str | None = None  # 区/县级行政区
    postal_code: str | None = None  # 邮政编码
    timezone: str | None = None  # 时区信息
    latitude: float | None = None  # 纬度
    longitude: float | None = None  # 经度
    location_code: str | None = None  # 行政区划代码
    full_address: str | None = None  # 完整地址


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


@dataclasses.dataclass
class AccessToken:
    """访问令牌"""

    access_token: str
    expire_time: datetime
    session_uuid: str


@dataclasses.dataclass
class RefreshToken:
    """刷新令牌"""

    refresh_token: str
    expire_time: datetime


@dataclasses.dataclass
class NewToken:
    """新访问令牌"""

    access_token: str
    access_expire_time: datetime
    refresh_token: str
    refresh_expire_time: datetime
    session_uuid: str


@dataclasses.dataclass
class TokenPayload:
    """令牌载荷数据类"""

    user_id: int
    session_uuid: str
    expire_time: datetime
