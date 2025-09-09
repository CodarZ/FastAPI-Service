#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request
from user_agents import parse

from backend.common.dataclasses import UserAgentInfo


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
