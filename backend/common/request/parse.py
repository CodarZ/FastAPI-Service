from typing import TYPE_CHECKING

from starlette_context.header_keys import HeaderKeys
from user_agents import parse

from backend.common.dataclasses import UserAgentInfo

if TYPE_CHECKING:
    from fastapi import Request


def parse_ua_info(request: Request) -> UserAgentInfo:
    """解析 User-Agent 信息."""
    user_agent = request.headers.get(HeaderKeys.user_agent, '')

    ua = parse(user_agent)

    return UserAgentInfo(user_agent=user_agent, os=ua.os.family, browser=ua.browser.family, device=ua.device.family)
