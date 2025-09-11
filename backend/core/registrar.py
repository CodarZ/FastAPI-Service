#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI as FastAPIBase
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter, http_default_callback
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from backend.app.router import router
from backend.common.exception.handler import register_exception
from backend.common.log import set_custom_logfile, setup_logging
from backend.common.response.check import ensure_unique_route_names
from backend.core.config import settings
from backend.core.path import STATIC_DIR, UPLOAD_DIR
from backend.database.postgresql import create_tables
from backend.database.redis import redis_client
from backend.middleware.access import AccessMiddleware
from backend.middleware.state import StateMiddleware
from backend.utils.openapi import simplify_operation_ids
from backend.utils.serializers import MsgSpecJSONResponse


def register_app() -> FastAPIBase:
    class FastAPI(FastAPIBase):
        # https://github.com/fastapi/fastapi/discussions/7847
        # https://github.com/fastapi/fastapi/discussions/8027
        def build_middleware_stack(self) -> ASGIApp:
            return CORSMiddleware(
                super().build_middleware_stack(),
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
                allow_origins=settings.CORS_ALLOWED_ORIGINS,
                expose_headers=settings.CORS_EXPOSE_HEADERS,
            )

    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
        lifespan=init,
        default_response_class=MsgSpecJSONResponse,
    )

    register_logger()

    register_static_file(app)

    register_middleware(app)

    register_router(app)

    register_exception(app)

    return app


@asynccontextmanager
async def init(app: FastAPIBase):
    # 创建数据库表
    await create_tables()

    # 初始化 Redis
    await redis_client.open()

    # 初始化 Limiter
    await FastAPILimiter.init(
        redis=redis_client,
        prefix=settings.REDIS_REQUEST_LIMITER_PREFIX,
        http_callback=http_default_callback,
    )

    yield

    await redis_client.shut()
    await FastAPILimiter.close()


def register_logger() -> None:
    """注册日志"""
    setup_logging()

    set_custom_logfile()


def register_static_file(app: FastAPIBase) -> None:
    """注册静态资源服务"""
    # 上传静态资源
    app.mount('/static/upload', StaticFiles(directory=UPLOAD_DIR), name='upload')

    # 固有静态资源
    if settings.FASTAPI_STATIC_FILES:
        app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


def register_middleware(app: FastAPIBase) -> None:
    """注册中间件"""

    app.add_middleware(AccessMiddleware)

    app.add_middleware(StateMiddleware)

    app.add_middleware(CorrelationIdMiddleware, validator=None)


def register_router(app: FastAPIBase) -> None:
    """注册路由"""

    # API
    app.include_router(router)

    # Extra
    ensure_unique_route_names(app)
    simplify_operation_ids(app)
