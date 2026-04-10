"""自定义 Pydantic 类型.

Pydantic 存在已有的类型: https://docs.pydantic.dev/latest/concepts/types/.
"""

from typing import Annotated

from pydantic import AfterValidator, Field, PlainSerializer, WithJsonSchema

from . import func

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


IdsListInt = Annotated[list[int], AfterValidator(func.ids_validator), Field(description='ID 列表')]
"""ID 列表（自动去重并过滤无效值）"""
