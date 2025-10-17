from typing import Literal
from uuid import uuid4

from fast_captcha import img_captcha
from starlette.concurrency import run_in_threadpool

from backend.app.admin.schema.captcha import CaptchaDetail
from backend.core.config import settings
from backend.database.redis import redis_client

CaptchaImgType = Literal['file', 'bytesio', 'base64']


class CaptchaService:
    @staticmethod
    def generate_captcha_sync(img_type: CaptchaImgType = 'base64') -> tuple[str, str]:
        """
        同步生成验证码

        :param img_type: 图片类型
        :return: (图片内容, 验证码)
        """
        img, code = img_captcha(img_byte=img_type)
        return str(img), code

    async def create_captcha(self, img_type: CaptchaImgType = 'base64') -> CaptchaDetail:
        """
        创建验证码并存储到 Redis

        :param img_type: 图片类型
        :return: 验证码详情
        """
        # 在线程池中同步生成验证码,避免阻塞事件循环
        img, code = await run_in_threadpool(self.generate_captcha_sync, img_type)

        # 生成唯一标识并存储到 Redis
        uuid = str(uuid4())
        await redis_client.set(
            f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{uuid}',
            code,
            ex=settings.CAPTCHA_LOGIN_EXPIRE_SECONDS,
        )

        # 根据图片类型处理图片数据
        if img_type == 'base64':
            image_data = f'data:image/png;base64,{img}'
        else:
            # file 或 bytesio 类型直接返回原始数据
            image_data = img

        return CaptchaDetail(uuid=uuid, img_type=img_type, image=image_data)


captcha_service = CaptchaService()
