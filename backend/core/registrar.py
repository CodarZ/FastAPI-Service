#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

from fastapi import FastAPI as FastAPIBase
from fastapi_limiter import FastAPILimiter, http_default_callback
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from backend.common.exception.handler import register_exception
from backend.common.log import set_custom_logfile, setup_logging
from backend.core.config import settings
from backend.database.postgresql import create_tables
from backend.database.redis import redis_client
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
