#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    """
    自定义的基础数据模型类。
      - 配置项 `use_enum_values=True`，在序列化时使用枚举字段的值，而不是枚举对象本身。
      - 适用于项目中的所有数据模型，以提供统一的行为和配置。

    配置项
      - `use_enum_values=True`: 序列化时使用枚举值，便于与前端或其他系统的交互。
      - `datetime` 类型的自定义序列化，输出格式为 YYYY-MM-DD HH:MM:SS。

    示例:

      ```python
        from enum import Enum


        class ExampleEnum(Enum):
            OPTION_A = 'Option A'
            OPTION_B = 'Option B'


        class ExampleModel(SchemaBase):
            value: ExampleEnum


        data = ExampleModel(value=ExampleEnum.OPTION_A)
        print(data.dict())  # 输出: {"value": "Option A"}
      ```
    """

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
        },
    )
