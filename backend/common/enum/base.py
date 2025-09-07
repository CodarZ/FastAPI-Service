#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, IntEnum as SourceIntEnum


class _EnumBase(Enum):
    """枚举辅助基类，用于扩展枚举类的功能

    `cls.__members__` 是枚举类的特殊属性，包含所有成员的键值对。
    """

    @classmethod
    def get_member_keys(cls):
        return list(cls.__members__.keys())

    @classmethod
    def get_member_values(cls):
        return [member.value for member in cls]

    @classmethod
    def has_key(cls, key: str) -> bool:
        return key in cls.__members__

    @classmethod
    def has_value(cls, value) -> bool:
        return value in cls.get_member_values()

    @classmethod
    def value_of(cls, key: str):
        """通过 key 获取枚举成员，找不到则返回 None"""
        return cls.__members__.get(key)


class IntEnum(_EnumBase, SourceIntEnum):
    """自定义整数枚举类"""

    pass


class StrEnum(_EnumBase, str, Enum):
    """自定义字符串枚举类"""

    pass
