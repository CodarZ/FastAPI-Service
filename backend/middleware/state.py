#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.request.parse import parse_ip_info, parse_user_agent


class StateMiddleware(BaseHTTPMiddleware):
    """请求 state 中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        ip_info = await parse_ip_info(request)

        # 设置附加请求信息
        for key, value in dataclasses.asdict(ip_info).items():
            setattr(request.state, key, value)

        ua_info = parse_user_agent(request)
        for key, value in dataclasses.asdict(ua_info).items():
            setattr(request.state, key, value)

        response = await call_next(request)

        return response
