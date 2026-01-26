import time

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.log import log
from backend.common.request.context import ctx
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
        ctx.perf_time = request.state.perf_time = perf_time

        start_time = timezone.now()
        ctx.start_time = request.state.start_time = start_time

        return await call_next(request)
