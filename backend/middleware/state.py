from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.request.context import ctx
from backend.common.request.parse import parse_ip_info, parse_user_agent_info

if TYPE_CHECKING:
    from fastapi import Request, Response


class StateMiddleware(BaseHTTPMiddleware):
    """请求状态中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理请求并设置请求状态信息"""
        ip_info = await parse_ip_info(request)
        ctx.ip = ip_info.ip
        ctx.country = ip_info.country
        ctx.region = ip_info.region
        ctx.city = ip_info.city

        ua_info = parse_user_agent_info(request)
        ctx.user_agent = ua_info.user_agent
        ctx.os = ua_info.os
        ctx.os_version = ua_info.os_version
        ctx.browser = ua_info.browser
        ctx.browser_version = ua_info.browser_version
        ctx.device = ua_info.device
        ctx.device_model = ua_info.device_model

        return await call_next(request)
