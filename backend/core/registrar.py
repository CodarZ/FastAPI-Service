#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI

from backend.core.config import settings


def register_app() -> FastAPI:
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=settings.FASTAPI_DOCS_URL,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
    )

    return app
