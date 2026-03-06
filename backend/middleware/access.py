import time

from typing import TYPE_CHECKING

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.request.context import ctx
from backend.utils import timezone

if TYPE_CHECKING:
    from fastapi import Request, Response


class AccessMiddleware(BaseHTTPMiddleware):
    """请求访问信息中间件."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        path = request.url.path
        method = request.method
        query = request.url.query
        url = f'{path}?{query}' if query else path

        if method != 'OPTIONS':
            logger.debug(f'[Debug] --> 请求开始 | {url}')

        ctx['perf_time'] = time.perf_counter()
        ctx['start_time'] = timezone.now()

        return await call_next(request)
