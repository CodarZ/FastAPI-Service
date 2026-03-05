from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from backend.common.request.context import ctx
from backend.core.config import settings


def get_request_trace_id() -> str:
    """从请求头中获取 `X-Request-ID`."""
    if context.exists():
        return ctx.get(HeaderKeys.request_id, settings.TRACE_ID_LOG_DEFAULT)
    return settings.TRACE_ID_LOG_DEFAULT
