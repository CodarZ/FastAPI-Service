#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from typing import Any, Sequence, TypeVar

from fastapi.encoders import decimal_encoder
from fastapi.responses import JSONResponse
from msgspec import json
from sqlalchemy import Row, RowMapping
from sqlalchemy.orm import ColumnProperty, SynonymProperty, class_mapper

# 通用行数据类型定义, 兼容 ORM 对象、Row、RowMapping 等
RowData = Row | RowMapping | Any
R = TypeVar('R', bound=RowData)


def _serialize_value(value: Any) -> Any:
    """
    对单个字段值进行序列化处理。

    目前支持：
    - Decimal 类型 → 转换为 float, 兼容 JSON 编码

    :param value: 任意字段值
    :return: JSON 可序列化值
    """
    if isinstance(value, Decimal):
        return decimal_encoder(value)
    return value


def select_columns_serialize(row: RowData) -> dict[str, Any]:
    """
    序列化 SQLAlchemy ORM 实例, 仅包含当前表的字段, 不包含关系字段（如外键表、反向引用等）。

    适用于将数据库模型转换为 JSON 可序列化字典（用于 API 响应）。

    :param row: SQLAlchemy ORM 实例, 必须包含 __table__ 属性
    :return: dict[str, Any] - 当前表字段组成的字典
    """

    result = {}
    for column in row.__table__.columns.keys():
        value = getattr(row, column)
        result[column] = _serialize_value(value)
    return result


def select_list_serialize(rows: Sequence[R]) -> list[dict[str, Any]]:
    """
    批量序列化 SQLAlchemy 查询结果序列, 每个元素使用 select_columns_serialize 处理。

    常用于列表分页查询接口的返回。

    :param rows: SQLAlchemy 查询结果组成的序列
    :return: list[dict[str, Any]] - 每条记录为一个字典
    """
    return [select_columns_serialize(item) for item in rows]


def select_as_dict(row: RowData, use_alias: bool = False) -> dict[str, Any]:
    """
    通用对象序列化为字典, 可选择是否使用 SQLAlchemy ORM 的字段别名。

    - 当 use_alias=False：使用对象的 __dict__, 性能更高
    - 当 use_alias=True：通过 class_mapper 获取字段映射, 兼容属性别名和覆盖字段

    :param row: SQLAlchemy ORM 实例对象
    :param use_alias: 是否启用字段别名（使用 ORM 声明的字段名而非实际属性）
    :return: dict[str, Any] - 对象的字段值字典
    """
    if not use_alias:
        result = row.__dict__.copy()
        del result['_sa_instance_state']
    else:
        result = {}
        mapper = class_mapper(row.__class__)
        for prop in mapper.iterate_properties:
            if isinstance(prop, (ColumnProperty, SynonymProperty)):
                key = prop.key
                result[key] = _serialize_value(getattr(row, key))

    return result


class MsgSpecJSONResponse(JSONResponse):
    """
    使用 msgspec 实现高性能 JSON 序列化的 FastAPI 响应类。

    替代默认的 JSONResponse, 可大幅提升大型数据返回的性能。
    """

    def render(self, content: Any) -> bytes:
        return json.encode(content)
