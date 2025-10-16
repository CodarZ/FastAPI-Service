#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dataclasses
import ipaddress
import json

import httpx

from fastapi import Request
from ip2loc import XdbSearcher
from user_agents import parse

from backend.common.dataclasses import IpInfo, UserAgentInfo
from backend.common.log import log
from backend.core.config import settings
from backend.core.path import IP2REGION_DIR
from backend.database.redis import redis_client


def is_private_ip(ip: str) -> bool:
    """判断 IP 是否是内网 IP"""
    try:
        ip_info = ipaddress.ip_address(ip)

        if ip_info.is_private or ip_info.is_loopback or ip_info.is_link_local or ip_info.is_multicast:
            return True
        return False

    except (ipaddress.AddressValueError, ValueError):
        return False
    except Exception:
        return False


def parse_user_agent_info(request: Request) -> UserAgentInfo:
    user_agent = request.headers.get('User-Agent', '').strip()

    if not user_agent:
        return UserAgentInfo(user_agent='unknown')

    _user_agent = parse(user_agent)

    # 获取操作系统及版本
    os = _user_agent.os.family
    os_version = f'{_user_agent.os.version_string}' if _user_agent.os.version_string else None

    # 获取浏览器及版本
    browser = _user_agent.browser.family
    browser_version = f'{_user_agent.browser.version_string}' if _user_agent.browser.version_string else None

    # 获取设备类型及型号
    device = _user_agent.device.family
    device_model = (
        f'{_user_agent.device.brand} {_user_agent.device.model}'
        if _user_agent.device.brand and _user_agent.device.model
        else None
    )

    return UserAgentInfo(
        user_agent=user_agent,
        os=os,
        os_version=os_version,
        browser=browser,
        browser_version=browser_version,
        device=device,
        device_model=device_model,
    )


async def parse_ip_info(request: Request) -> IpInfo:
    """解析 IP 信息"""
    ip = _get_request_ip(request)

    if is_private_ip(ip):
        return IpInfo(ip=ip, country='内网 IP', full_address='内网IP')

    location = await redis_client.get(f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}')
    if location:
        location_dict = json.loads(location)
        return IpInfo(**location_dict)

    location_info = await _get_location_online(ip, request.headers.get('User-Agent'))
    if location_info.country is None:
        location_info = _get_location_offline(ip)
    await redis_client.set(
        name=f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}',
        value=json.dumps(dataclasses.asdict(location_info)),
        ex=settings.IP_LOCATION_EXPIRE_SECONDS,
    )
    return location_info


def _get_request_ip(request: Request):
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

    return '127.0.0.1'


async def _get_location_online(ip: str, user_agent: str | None) -> IpInfo:
    """在线获取 IP 地址的地理位置"""
    ip_api_url = f'http://ip-api.com/json/{ip}?lang=zh-CN'
    headers = {'User-Agent': user_agent or 'unknown'}

    async with httpx.AsyncClient(timeout=3) as request:
        try:
            response = await request.get(ip_api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    log.info(f'在线获取 IP 地址 {ip} 的地理位置: {data}')
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
                log.info(f'IP 地址 {ip} 查询请求失败: {response.status_code} - {response.text}')
                return IpInfo(ip)
        except Exception as e:
            log.error(f'获取 IP 地址 {ip} 代码程序异常: {e}')
            return IpInfo(ip)


# 离线 IP 搜索器单例（数据将缓存到内存, 缓存大小取决于 IP 数据文件大小）
__xdb_searcher = XdbSearcher(contentBuff=XdbSearcher.loadContentFromFile(dbfile=IP2REGION_DIR / 'ip2region_v4.xdb'))


def _get_location_offline(ip: str) -> IpInfo:
    """离线获取 IP 地址的地理位置"""
    try:
        data = __xdb_searcher.search(ip)
        data = data.split('|')

        log.info(f'离线获取 IP 地址 {ip} 的地理位置: {data}')

        return IpInfo(
            ip=ip,
            country=data[0] if data[0] != '0' else None,
            region=data[1] if data[1] != '0' else None,
            city=data[2] if data[2] != '0' else None,
        )
    except Exception as e:
        log.error(f'离线获取 IP 地址属地失败，错误信息：{e}')
        return IpInfo(ip)
