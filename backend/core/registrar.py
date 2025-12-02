from fastapi import FastAPI

from backend.app.router import router
from backend.core.config import settings


def register_app():
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        docs_url=settings.FASTAPI_DOCS_URL,
    )

    register_router(app)

    return app


def register_router(app: FastAPI) -> None:
    """注册路由"""

    # API
    app.include_router(router)
