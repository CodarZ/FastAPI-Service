#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter, http_default_callback

from backend.common.log import set_custom_logfile, setup_logging
from backend.core.config import settings
from backend.database.postgresql import create_tables
from backend.database.redis import redis_client


def register_app() -> FastAPI:
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
        lifespan=init,
    )

    register_logger()

    return app


@asynccontextmanager
async def init(app: FastAPI):
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
