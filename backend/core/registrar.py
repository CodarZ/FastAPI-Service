#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from fastapi import FastAPI

from backend.common.log import setup_logging
from backend.core.config import settings


def register_app() -> FastAPI:
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
    )

    register_logger()

    return app


def register_logger() -> None:
    """注册日志"""
    setup_logging()
