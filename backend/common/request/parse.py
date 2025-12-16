import dataclasses
import ipaddress
import json

from typing import TYPE_CHECKING

import ip2region.searcher as xdb
import ip2region.util as util

from user_agents import parse

from backend.common.dataclasses import IpInfo, UserAgentInfo
from backend.core.config import settings
from backend.core.path import IP2REGION_DIR
from backend.database.redis import redis_client

if TYPE_CHECKING:
    from fastapi import Request


def parse_user_agent_info(request: Request) -> UserAgentInfo:
    """解析请求的用户代理信息"""
    user_agent = request.headers.get('User-Agent', '')

    ua = parse(user_agent)

    # 获取操作系统及版本
    os = ua.os.family or None
    os_version = ua.os.version_string or None

    # 获取浏览器及版本
    browser = ua.browser.family or None
    browser_version = ua.browser.version_string or None

    # 获取设备类型及型号
    device = ua.device.family or None
    device_model = f'{ua.device.brand} {ua.device.model}'.strip() if ua.device.brand or ua.device.model else None

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
    """解析请求的 IP 信息"""
    ip = _get_request_ip(request)

    if _is_private_ip(ip):
        return IpInfo(ip=ip, country='内网 IP', full_address='内网IP')

    location = await redis_client.get(f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}')

    if location:
        location_dict = json.loads(location)
        return IpInfo(**location_dict)

    location_info = _get_location_offline(ip)

    await redis_client.set(
        name=f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}',
        value=json.dumps(dataclasses.asdict(location_info)),
        ex=settings.IP_LOCATION_EXPIRE_SECONDS,
    )

    return location_info


def _get_request_ip(request: Request) -> str:
    """获取请求的 IP 地址

    优先级：
        1. X-Real-IP
        2. X-Forwarded-For
        3. request.client.host
    """
    # 优先从 X-Real-IP 获取
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip

    # 从 X-Forwarded-For 获取
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For 格式: client, proxy1, proxy2
        return forwarded_for.split(',')[0].strip()

    if request.client:
        client_host = request.client.host
        # 忽略 pytest 测试客户端
        if client_host and client_host != 'testclient':
            return client_host

    return '0.0.0.0'


def _is_private_ip(ip: str) -> bool:
    """判断 IP 是否是内网 IP"""
    try:
        ip_info = ipaddress.ip_address(ip)
        return ip_info.is_private or ip_info.is_loopback or ip_info.is_link_local or ip_info.is_multicast
    except ValueError, ipaddress.AddressValueError:
        return False


ip2region_v4 = IP2REGION_DIR / 'ip2region_v4.xdb'
ip2region_v6 = IP2REGION_DIR / 'ip2region_v6.xdb'

# 全局缓存 searcher 对象（完全基于内存，支持并发）
_searcher_v4 = None
_searcher_v6 = None


def _init_ip2region_searchers():
    """初始化 IP2Region 查询器（全局单例，完全基于内存）

    缓存整个 xdb 数据到内存，实现零 IO 查询，支持并发访问
    """
    global _searcher_v4, _searcher_v6

    if _searcher_v4 is None:
        try:
            # 加载 IPv4 xdb 数据到内存
            c_buffer_v4 = util.load_content_from_file(str(ip2region_v4))
            _searcher_v4 = xdb.new_with_buffer(util.IPv4, c_buffer_v4)
        except Exception as e:
            print(f'IPv4 searcher 初始化失败: {e}')

    if _searcher_v6 is None:
        try:
            # 加载 IPv6 xdb 数据到内存
            c_buffer_v6 = util.load_content_from_file(str(ip2region_v6))
            _searcher_v6 = xdb.new_with_buffer(util.IPv6, c_buffer_v6)
        except Exception as e:
            print(f'IPv6 searcher 初始化失败: {e}')


def _get_location_offline(ip: str) -> IpInfo:
    """离线获取 IP 地址的地理位置

    完全基于内存的查询，零 IO 操作，支持并发
    """
    # 懒加载：首次调用时初始化
    if _searcher_v4 is None or _searcher_v6 is None:
        _init_ip2region_searchers()

    try:
        # 判断 IP 类型并选择对应的 searcher
        ip_obj = ipaddress.ip_address(ip)
        searcher = _searcher_v6 if ip_obj.version == 6 else _searcher_v4

        if searcher is None:
            return IpInfo(ip=ip, country='未知', full_address='查询服务未初始化')

        # 查询 IP 地理位置（无 IO 操作）
        region = searcher.search(ip)

        if not region:
            return IpInfo(ip=ip, country='未知', full_address='未知')

        # 解析并返回结果
        return _parse_region(ip, region)

    except ValueError, Exception:
        return IpInfo(ip=ip, country='未知', full_address='查询失败')


def _parse_region(ip: str, region: str) -> IpInfo:
    """解析 ip2region 返回的 region 字符串

    格式: 国家|区域|省份|城市|运营商
    例如: 中国|0|广东省|深圳市|电信
    """
    parts = region.split('|')
    country = parts[0] if len(parts) > 0 and parts[0] != '0' else None
    province = parts[2] if len(parts) > 2 and parts[2] != '0' else None
    city = parts[3] if len(parts) > 3 and parts[3] != '0' else None

    # 拼接完整地址
    address_parts = [p for p in [country, province, city] if p]
    full_address = ' '.join(address_parts)

    return IpInfo(
        ip=ip,
        country=country,
        region=province,
        city=city,
        full_address=full_address,
    )
