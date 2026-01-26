from asyncio import create_task
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from starlette_context.middleware import ContextMiddleware
from starlette_context.plugins import RequestIdPlugin

from backend.app.router import router
from backend.common.exception.handler import register_exception
from backend.common.log import set_custom_logfile, setup_logging
from backend.common.request.limit import http_callback_limit
from backend.common.response.code import StandardResponseStatus
from backend.common.schema import auto_rebuild_all_schemas
from backend.core.config import settings
from backend.database.postgresql import create_tables
from backend.database.redis import redis_client
from backend.middleware.access import AccessMiddleware
from backend.middleware.operation_log import OperationLogMiddleware
from backend.middleware.state import StateMiddleware
from backend.utils.route import ensure_unique_route_name, simplify_operation_id
from backend.utils.serializers import MsgSpecJSONResponse

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def register_app():

    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
        default_response_class=MsgSpecJSONResponse,
        lifespan=init,
    )
    register_logger()

    auto_rebuild_all_schemas()

    register_middleware(app)

    register_router(app)

    register_exception(app)

    return app


@asynccontextmanager
async def init(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理器"""

    # 创建数据库表
    await create_tables()

    # 连接 Redis
    await redis_client.open()

    # 初始化 Limiter
    await FastAPILimiter.init(
        redis=redis_client,
        prefix=settings.REDIS_REQUEST_LIMITER_PREFIX,
        http_callback=http_callback_limit,
    )

    # 创建操作日志任务
    create_task(OperationLogMiddleware.task())

    yield

    # 关闭 Redis 连接
    await redis_client.aclose()

    await FastAPILimiter.close()


def register_router(app: FastAPI) -> None:
    """注册路由"""

    # API
    app.include_router(router)

    # Extra
    ensure_unique_route_name(app)
    simplify_operation_id(app)


def register_middleware(app: FastAPI) -> None:
    """注册中间件（执行顺序从下往上）"""

    app.add_middleware(OperationLogMiddleware)

    app.add_middleware(StateMiddleware)

    app.add_middleware(AccessMiddleware)

    # ContextVar 上下文管理
    app.add_middleware(
        ContextMiddleware,
        plugins=[RequestIdPlugin(validate=True)],
        default_error_response=MsgSpecJSONResponse(
            content={
                'code': StandardResponseStatus.HTTP_400.code,
                'msg': StandardResponseStatus.HTTP_400.msg,
                'data': None,
            },
            status_code=StandardResponseStatus.HTTP_400.code,
        ),
    )


def register_logger() -> None:
    """注册日志"""
    setup_logging()

    set_custom_logfile()
