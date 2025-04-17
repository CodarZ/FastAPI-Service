#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import json

from typing import Optional

import httpx

from fastapi import Request
from user_agents import parse

from backend.common.dataclasses import IpInfo, UserAgentInfo
from backend.common.logger import log
from backend.core.settings import settings
from backend.database.redis import redis_client


def parse_user_agent(request: Request) -> UserAgentInfo:
    """解析请求中的用户代理信息"""
    user_agent = request.headers.get('User-Agent')
    if not user_agent:
        return UserAgentInfo('unknown')

    _user_agent = parse(user_agent)

    os = _user_agent.get_os()
    os_version = _user_agent.os.version_string

    browser = _user_agent.get_browser()
    browser_version = _user_agent.browser.version_string

    divice = _user_agent.get_device()
    device_model = (
        f'{_user_agent.device.brand} {_user_agent.device.model}'
        if _user_agent.device.brand and _user_agent.device.model
        else None
    )

    return UserAgentInfo(
        user_agent,
        os,
        os_version,
        browser,
        browser_version,
        divice,
        device_model,
    )


async def parse_ip_info(request: Request) -> Optional[IpInfo]:
    ip = __get_request_ip(request)
    location = await redis_client.get(f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}')
    if location:
        location_dict = json.loads(location.decode('utf-8'))
        return IpInfo(**location_dict)

    online_location = await __get_location_online(ip, request.headers.get('User-Agent'))
    await redis_client.set(
        name=f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}',
        value=json.dumps(dataclasses.asdict(online_location)),
        ex=settings.IP_LOCATION_EXPIRE_SECONDS,
    )
    return online_location


def __get_request_ip(request: Request):
    """获取请求的 IP 地址

    优先级：
      1. X-Real-IP
      2. X-Forwarded-For
      3. request.client.host
    """
    ip = request.headers.get('X-Real-IP')
    if ip and ip.strip():
        return ip

    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded and forwarded.strip():
        return next((x.strip() for x in forwarded.split(',') if x.strip()))

    if request.client and request.client.host.strip():
        return '127.0.0.1' if request.client.host == 'testclient' else request.client.host

    return '0.0.0.0'


async def __get_location_online(ip: str, user_agent: str | None) -> IpInfo:
    """获取在线 IP 地址的地理位置"""
    ip_api_url = f'http://ip-api.com/json/{ip}?lang=zh-CN'
    headers = {'User-Agent': user_agent or 'unknown'}

    async with httpx.AsyncClient(timeout=3) as request:
        try:
            response = await request.get(ip_api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return IpInfo(
                        ip=data.get('query'),
                        country=data.get('country'),
                        region=data.get('regionName'),
                        city=data.get('city'),
                        district=None,  # ip-api 不返回区县
                        postal_code=data.get('zip'),
                        timezone=data.get('timezone'),
                        latitude=data.get('lat'),
                        longitude=data.get('lon'),
                        location_code=data.get('region'),
                        full_address=f'{data.get("country", "")}{data.get("regionName", "")}{data.get("city", "")}',
                    )
                else:
                    log.info(f'IP 地址 {ip} 查询不到: {data}')
                    return IpInfo(ip)
            else:
                log.info(f'IP 地址 {ip} 查询失败: {response.status_code} - {response.text}')
                return IpInfo(ip)
        except Exception as e:
            log.error(f'获取 IP 地址 {ip} 的地理位置失败: {e}')
            return IpInfo(ip)
