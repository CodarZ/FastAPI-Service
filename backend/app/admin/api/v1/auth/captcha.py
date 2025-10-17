from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from backend.app.admin.schema.captcha import CaptchaDetail
from backend.app.admin.service.captcha import captcha_service
from backend.common.response.base import ResponseSchemaModel, response_base

router = APIRouter()


@router.get(
    '/captcha',
    summary='获取登录验证码',
    dependencies=[Depends(RateLimiter(times=5, seconds=10))],
)
async def get_captcha() -> ResponseSchemaModel[CaptchaDetail]:
    """获取登录验证码"""
    data = await captcha_service.create_captcha()
    return response_base.success_with_schema(data=data)
