from fastapi import FastAPI
from starlette_context.middleware import ContextMiddleware
from starlette_context.plugins import RequestIdPlugin

from backend.common.log import register_logger
from backend.core.config import settings
from backend.middleware import AccessMiddleware, StateMiddleware


def register_app() -> FastAPI:

    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
        swagger_ui_parameters={
            'docExpansion': 'none',
            'persistAuthorization': True,
            'displayRequestDuration': True,
            'defaultModelsExpandDepth': -1,
        },
    )

    # 日志
    register_logger()

    # 中间件
    register_middleware(app)

    return app


def register_middleware(app: FastAPI):
    """注册全局中间件（执行顺序从下往上）."""
    # --- 请求状态信息中间件 ---
    app.add_middleware(StateMiddleware)

    # --- 请求访问信息中间件 ---
    app.add_middleware(AccessMiddleware)

    # --- 请求上下文中间件 ---
    app.add_middleware(
        ContextMiddleware,
        plugins=[RequestIdPlugin(validate=True)],
    )
