import time

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.log import log
from backend.utils.timezone import timezone

if TYPE_CHECKING:
    from fastapi import Request, Response


class AccessMiddleware(BaseHTTPMiddleware):
    """访问日志中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path if not request.url.query else request.url.path + '/' + request.url.query

        if request.method != 'OPTIONS':
            log.debug(f'--> 请求开始[{path}]')

        perf_time = time.perf_counter()
        request.state.perf_time = perf_time

        start_time = timezone.now()
        request.state.start_time = start_time

        response = await call_next(request)

        elapsed = (time.perf_counter() - perf_time) * 1000.0

        if request.method != 'OPTIONS':
            log.debug('<-- 请求结束')

            log.info(
                f'{(request.client.host if request.client else "-"): <15} | {request.method: <5} | '
                f'{f"{elapsed:.3f} ms": <12} | {response.status_code: <7} | {request.url.path}'
            )
        return response
