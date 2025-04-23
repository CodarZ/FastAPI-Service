#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, validate_email
from pydantic_core import core_schema

from backend.utils.regexp_verify import is_phone


class CustomPhoneStr(str):
    """
    自定义的手机号字段类。
      - 允许空字符串（""）视为 None。
      - 非空字符串时执行手机号格式校验。
      - 适用于 Pydantic 模型字段类型，支持自动转换。

    方法：
      - `_validate(cls, __input_value: str) -> str | None`
      - 输入为空字符串时返回 None。
      - 非空则校验是否合法手机号，合法返回原值，否则抛出异常。

    示例：
      ```python
        phone = CustomPhoneStr._validate('')  # 返回 None
        phone = CustomPhoneStr._validate('13812345678')  # 返回 '13812345678'
        phone = CustomPhoneStr._validate('123456')  # ❌ 抛出校验错误
      ```
    """

    @classmethod
    def _validate(cls, __input_value: str) -> Optional[str]:
        if __input_value == '':
            return None
        if is_phone(__input_value):
            return __input_value
        raise ValueError('手机号格式不正确')

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            json_schema_input_schema=core_schema.str_schema(metadata={'format': 'phone', 'title': '手机号'}),
        )


class CustomEmailStr(EmailStr):
    """
    自定义的电子邮件字段类。
      - 重写了 `_validate` 方法。
      - 允许空字符串 (`""`) 被视为有效值，并将其转换为 `None`。
      - 非空值仍然执行标准的电子邮件格式验证。

    方法
      - `_validate(cls, __input_value: str) -> str`:
      - 验证输入值是否为空字符串。
      - 如果为空字符串，返回 `None`。
      - 否则使用 `pydantic.validate_email` 方法进行电子邮件格式验证。

    示例:
      ```python
        email = CustomEmailStr._validate('')  # 返回 None
        email = CustomEmailStr._validate('example@test.com')  # 返回 'example@test.com'
      ```
    """

    @classmethod
    def _validate(cls, __input_value: str) -> Optional[str]:
        # 如果输入为空字符串，返回 None
        # 否则使用 pydantic 的 validate_email 方法验证
        return None if __input_value == '' else validate_email(__input_value)[1]


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
