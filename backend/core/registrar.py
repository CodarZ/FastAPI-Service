from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_context.middleware import ContextMiddleware
from starlette_context.plugins import RequestIdPlugin

from backend.common.exception import register_exception
from backend.common.log import register_logger
from backend.core.config import settings
from backend.database import redis_client
from backend.middleware import AccessMiddleware, RequestLogMiddleware, StateMiddleware


def register_app() -> FastAPI:

    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
        lifespan=lifespan,
        swagger_ui_parameters={
            'docExpansion': 'none',
            'persistAuthorization': True,
            'displayRequestDuration': True,
            'defaultModelsExpandDepth': -1,
        },
    )

    # 日志
    register_logger()

    # 异常处理器
    register_exception(app)

    # 中间件
    register_middleware(app)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器."""
    # 连接 Redis
    await redis_client.open()

    yield

    # 关闭 Redis 连接
    await redis_client.aclose()


def register_middleware(app: FastAPI):
    """注册全局中间件（执行顺序从下往上）."""
    # --- 请求日志中间件 ---
    app.add_middleware(RequestLogMiddleware)

    # --- 请求状态信息中间件 ---
    app.add_middleware(StateMiddleware)

    # --- 请求访问信息中间件 ---
    app.add_middleware(AccessMiddleware)

    # --- 请求上下文中间件 ---
    app.add_middleware(
        ContextMiddleware,
        plugins=[RequestIdPlugin(validate=True)],
    )

    # --- 请求 CORS 跨域中间件 ---
    if settings.MIDDLEWARE_CORS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )
