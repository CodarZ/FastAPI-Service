from fastapi import FastAPI
from starlette_context.middleware import ContextMiddleware
from starlette_context.plugins import RequestIdPlugin

from backend.app.router import router
from backend.common.exception.handler import register_exception
from backend.common.response.code import StandardResponseStatus
from backend.core.config import settings
from backend.utils.route import ensure_unique_route_name, simplify_operation_id
from backend.utils.serializers import MsgSpecJSONResponse


def register_app():
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
    )

    register_middleware(app)

    register_router(app)

    register_exception(app)

    return app


def register_router(app: FastAPI) -> None:
    """注册路由"""

    # API
    app.include_router(router)

    # Extra
    ensure_unique_route_name(app)
    simplify_operation_id(app)


def register_middleware(app: FastAPI) -> None:
    """注册中间件（执行顺序从下往上）"""

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
