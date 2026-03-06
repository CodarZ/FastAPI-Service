from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.request import ctx, parse_ua_info

if TYPE_CHECKING:
    from fastapi import Request, Response


class StateMiddleware(BaseHTTPMiddleware):
    """请求状态信息中间件."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        ua = parse_ua_info(request)
        ctx['ua'] = ua

        return await call_next(request)
