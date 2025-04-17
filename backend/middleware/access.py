#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.logger import log
from backend.utils.timezone import timezone


class AccessMiddleware(BaseHTTPMiddleware):
    """请求日志中间件

    记录每个 HTTP 请求的关键信息，包括：
        - 客户端 host
        - HTTP 方法（如 GET、POST）
        - 响应状态码（如 200、404）
        - 请求路径（如 /api/v1/resource）
        - 请求处理时间（毫秒级）
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = timezone.now()

        response = await call_next(request)

        end_time = timezone.now()

        duration = round((end_time - start_time).total_seconds(), 3) * 1000.0

        # 记录请求日志
        log.info(
            f'{(request.client.host if request.client else "unknown"): <15} | {request.method: <5} | '
            f'{f"{duration}ms": <9} | {response.status_code: <3} | '
            f'{request.url.path}'
        )

        return response
