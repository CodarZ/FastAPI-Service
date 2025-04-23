#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from contextlib import asynccontextmanager

import socketio

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from starlette.middleware.authentication import AuthenticationMiddleware

from backend.app.router import router
from backend.common.logger import set_custom_logfile, setup_logging
from backend.core.config import settings
from backend.core.paths import STATIC_DIR
from backend.database.mysql import create_table
from backend.database.redis import redis_client
from backend.middleware.jwt import JWTAuthMiddleware
from backend.middleware.state import StateMiddleware
from backend.utils.check import ensure_unique_route_names, http_limit_callback
from backend.utils.openapi_patch import simplify_operation_ids
from backend.utils.serializers import MsgSpecJSONResponse


def register_app() -> FastAPI:
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=settings.OPENAPI_URL,
        docs_url=settings.DOCS_URL,
        default_response_class=MsgSpecJSONResponse,
        lifespan=init,
    )
    register_socket(app)
    register_logger()
    register_static_file(app)
    register_middleware(app)
    register_router(app)

    return app


@asynccontextmanager
async def init(app: FastAPI):
    await create_table()

    await redis_client.open()

    await FastAPILimiter.init(
        redis_client,
        settings.REQUEST_LIMITER_REDIS_PREFIX,
        http_limit_callback,
    )
    yield

    await redis_client.close()
    await FastAPILimiter.close()


def register_logger():
    """注册日志"""
    setup_logging()
    set_custom_logfile()


def register_static_file(app: FastAPI):
    """注册静态资源服务"""
    if settings.FASTAPI_STATIC_FILES:
        from fastapi.staticfiles import StaticFiles

        app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')  # 固有静态资源


def register_middleware(app: FastAPI):
    # JWT auth (必须)
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JWTAuthMiddleware(),
        on_error=JWTAuthMiddleware.auth_exception_handler,
    )

    if settings.MIDDLEWARE_ACCESS:
        from backend.middleware.access import AccessMiddleware

        app.add_middleware(AccessMiddleware)

    app.add_middleware(StateMiddleware)
    app.add_middleware(CorrelationIdMiddleware, validator=lambda x: False)

    # CORS（必须放在最下面）
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )


def register_router(app: FastAPI) -> None:
    """
    注册路由

    :param app: FastAPI 应用实例
    :return:
    """

    app.include_router(router, prefix=settings.API_ROUTE_PREFIX)

    # Extra
    ensure_unique_route_names(app)
    simplify_operation_ids(app)


def register_socket(app: FastAPI) -> None:
    """注册 Socket.IO 应用"""
    from backend.common.socketio.server import sio

    socket_app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=app,
        # 切勿删除此配置：https://github.com/pyropy/fastapi-socketio/issues/51
        socketio_path='/ws/socket.io',
    )
    app.mount('/ws', socket_app)
