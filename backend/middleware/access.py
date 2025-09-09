#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.log import log


class AccessMiddleware(BaseHTTPMiddleware):
    """访问日志中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path if not request.url.query else request.url.path + '/' + request.url.query

        if request.method != 'OPTIONS':
            log.debug(f'--> 请求开始[{path}]')

        perf_time = time.perf_counter()

        response = await call_next(request)

        elapsed = (time.perf_counter() - perf_time) * 1000.0

        if request.method != 'OPTIONS':
            log.debug('<-- 请求结束')

            log.info(
                f'{(request.client.host if request.client else "unknown"): <15} | {request.method: <5} | '
                f'{f"{elapsed:.3f} ms": <9} | {response.status_code: <7} | {request.url.path}'
            )
        return response
