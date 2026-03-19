"""Pydantic 验证器函数.

提供项目特定的字段验证器, 配合 Pydantic 的 field_validator 使用。

注意：SchemaBase 已配置 str_strip_whitespace=True, Pydantic 会自动去除字符串两端空白, 验证器中无需重复处理。
"""

import re

from typing import TYPE_CHECKING

from backend.common.enum import StatusEnum
from backend.utils import regex as patterns

if TYPE_CHECKING:
    from pydantic import SerializationInfo


def status_validator(value: StatusEnum) -> StatusEnum:
    """验证状态值的逻辑关系."""
    if value not in StatusEnum:
        raise ValueError('无效的状态值')
    return value


def cn_mobile_validator(value: str | None) -> str | None:
    """验证中国大陆手机号."""
    if not value:
        return None

    # 1. 统一清洗逻辑：去掉所有空格和连字符
    value = value.replace(' ', '').replace('-', '')

    # 2. 处理区号：支持 +86, 86, 0086
    if value.startswith('+86'):
        value = value[3:]
    elif value.startswith('86'):
        value = value[2:]
    elif value.startswith('0086'):
        value = value[4:]

    # 3. 校验
    if not re.fullmatch(patterns.MOBILE_PATTERN, value):
        raise ValueError('手机号格式不正确')

    return value


def mobile_serialize(v: str | None, info: SerializationInfo) -> str | None:
    """序列化手机号，默认隐藏中间4位脱敏显示.

    通过 info.context 传递 show_full_mobile=True 可以显示完整手机号。
    """
    if not v or (info.context or {}).get('show_full_mobile'):
        return v
    return f'{v[:3]}****{v[-4:]}'
