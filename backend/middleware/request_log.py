import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from backend.common.request import ctx
from backend.core.config import settings


class RequestLogMiddleware(BaseHTTPMiddleware):
    """请求日志中间件."""

    async def dispatch(self, request, call_next):

        path = request.url.path

        if path in settings.REQUEST_LOG_WHITE_PATH or not path.startswith(f'{settings.FASTAPI_ROUTE_PREFIX}'):
            response = await call_next(request)
        else:
            method = request.method

            response = await call_next(request)
            code = response.status_code
            perf_time = ctx.get('perf_time')
            elapsed = round((time.perf_counter() - perf_time) * 1000, 3)

            # 此信息只能在请求后获取
            route = request.scope.get('route')
            summary = route.summary or '' if route else ''

            # 日志记录
            logger.debug(f'接口摘要：{summary}')
            logger.info(f'{method: <7} | {code!s: <6} | {elapsed:.3f}ms | {path}')

            if request.method != 'OPTIONS':
                logger.debug('<-- 请求结束')

        return response
