from fastapi import APIRouter

from backend.common.response.base import ResponseModel, response_base

router = APIRouter()


@router.get('/health', summary='健康检查')
async def health_check() -> ResponseModel:
    return response_base.success()
