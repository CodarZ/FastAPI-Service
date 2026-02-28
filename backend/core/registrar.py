from fastapi import FastAPI

from backend.core.config import settings


def register_app() -> FastAPI:

    return FastAPI(
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
