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

    Attributes:
        ip (str): IP 地址, 支持 IPv4 和 IPv6 格式
        country (str | None): 国家/地区名称, 例如："中国"、"美国"
        region (str | None): 省份/州/行政区, 例如："北京"、"加利福尼亚州"
        city (str | None): 城市名称, 例如："深圳"、"旧金山"
        district (str | None): 区/县级行政区, 例如："南山区"
        postal_code (str | None): 邮政编码, 例如："518000"
        timezone (str | None): 时区信息, 例如："Asia/Shanghai"
        latitude (float | None): 纬度坐标, 例如：22.5431
        longitude (float | None): 经度坐标, 例如：114.0579
        location_code (str | None): 行政区划代码, 例如："440300"（深圳）
        full_address (str | None): 完整地址描述, 格式：省市区详细地址
    """

    ip: str
    country: str | None = None
    region: str | None = None
    city: str | None = None
    district: str | None = None
    postal_code: str | None = None
    timezone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_code: str | None = None
    full_address: str | None = None


@dataclasses.dataclass
class UserAgentInfo:
    """User-Agent 信息解析数据类

    用于解析和存储 HTTP 请求头中的 User-Agent 字符串, 提供客户端详细信息。

    Attributes:
        user_agent (str): 原始 User-Agent 字符串
        os (str | None): 操作系统名称, 例如：Windows、macOS、iOS、Android
        os_version (str | None): 操作系统版本号, 例如：Windows 10、macOS 12.3
        browser (str | None): 浏览器名称, 例如：Chrome、Safari、Firefox
        browser_version (str | None): 浏览器版本号, 例如：96.0.4664.110
        device (str | None): 设备类型, 可选值：Mobile、Tablet、Desktop
        device_model (str | None): 设备具体型号, 例如：iPhone 13 Pro、Pixel 6
    """

    user_agent: str
    os: str | None = None
    os_version: str | None = None
    browser: str | None = None
    browser_version: str | None = None
    device: str | None = None
    device_model: str | None = None


@dataclasses.dataclass
class RequestCallNext:
    """请求调用链追踪数据类

    用于在中间件中追踪和记录请求处理过程的状态信息。

    Attributes:
        code (str): 状态码，用于标识请求处理的结果
        msg (str): 状态消息，对处理结果的详细描述
        status (StatusEnum): 状态枚举，表示请求处理的最终状态
        err (Exception | None): 异常信息，如果处理过程中出现错误则包含异常对象
        response (Response): FastAPI 响应对象，包含返回给客户端的数据
    """

    code: str
    msg: str
    status: StatusEnum
    err: Exception | None
    response: Response


@dataclasses.dataclass
class NewToken:
    """新令牌信息数据类

    用于存储新生成的访问令牌和刷新令牌及其相关信息。

    Attributes:
        access_token (str): 新的访问令牌字符串
        expire_time (datetime): 访问令牌的过期时间
        session_uuid (str): 会话唯一标识符
    """

    access_token: str
    expire_time: datetime
    session_uuid: str


@dataclasses.dataclass
class AccessToken:
    """访问令牌信息数据类

    用于存储访问令牌及其相关信息。

    Attributes:
        access_token (str): 访问令牌字符串
        expire_time (datetime): 访问令牌的过期时间
        session_uuid (str): 会话唯一标识符
    """

    access_token: str
    expire_time: datetime
    session_uuid: str


@dataclasses.dataclass
class RefreshToken:
    """刷新令牌信息数据类

    用于存储刷新令牌及其相关信息。

    Attributes:
        refresh_token (str): 刷新令牌字符串
        expire_time (datetime): 刷新令牌的过期时间
    """

    refresh_token: str
    expire_time: datetime


@dataclasses.dataclass
class TokenPayload:
    """令牌载荷数据类

    用于存储令牌中包含的核心信息。

    Attributes:
        id (int): 用户标识符
        session_uuid (str): 会话唯一标识符
        expire_time (datetime): 令牌过期时间
    """

    id: int
    session_uuid: str
    expire_time: datetime
