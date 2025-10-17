from pydantic import Field

from backend.common.schema import SchemaBase


class CaptchaDetail(SchemaBase):
    """验证码详情"""

    uuid: str = Field(description='图片唯一标识')
    img_type: str = Field(description='图片类型')
    image: str = Field(description='图片内容')
