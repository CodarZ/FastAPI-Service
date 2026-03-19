"""自定义 Pydantic 类型.

Pydantic 存在已有的类型: https://docs.pydantic.dev/latest/concepts/types/.
"""

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, Field, PlainSerializer, WithJsonSchema

from backend.common.enum import StatusEnum
from backend.utils import timezone

from . import func

StatusInt = Annotated[StatusEnum, AfterValidator(func.status_validator), Field(description='状态值：0-停用，1-正常')]

LocalDatetime = Annotated[
    datetime,
    AfterValidator(timezone.f_local_datetime),
    PlainSerializer(lambda dt: timezone.to_str(dt), return_type=str, when_used='json'),
]
"""本地时区时间类型.

- 反序列化/验证：
    - 将输入 datetime 统一转为本地时区的 aware datetime
    - naive datetime → 视为本地时区（DATETIME_TIMEZONE）
    - 其他时区的 aware datetime → 自动转换到本地时区
- JSON 序列化：输出为本地时区的格式化字符串（DATETIME_FORMAT）
"""

CNMobileStr = Annotated[
    str,
    AfterValidator(func.cn_mobile_validator),
    WithJsonSchema({'type': 'string', 'format': 'mobile'}),
    PlainSerializer(func.mobile_serialize, when_used='json-unless-none'),
]
"""
中国大陆手机号:
- 自动清洗区号/空格并校验 11 位格式
- 默认 JSON 输出为 138****5678

若需明文，请使用：`UserModel.model_dump(mode='json', context={'show_full_mobile': True})`

"""
