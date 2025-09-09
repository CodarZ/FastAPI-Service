#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Any, Sequence, TypeVar

from fastapi.encoders import decimal_encoder
from msgspec import json
from sqlalchemy import Row, RowMapping
from sqlalchemy.orm import ColumnProperty, SynonymProperty, class_mapper
from starlette.responses import JSONResponse

# RowData 类型别名，表示可能是 SQLAlchemy 的 Row、RowMapping 类型或其他任意类型
RowData = Row | RowMapping | Any

# 泛型 R，用于限定类型必须为 RowData
R = TypeVar('R', bound=RowData)


def select_columns_serialize(row: RowData) -> dict:
    """
    序列化 SQLAlchemy 查询结果的表列数据（不包含关联关系的列）。

    遍历给定 SQLAlchemy Row 对象中的所有表列，将其转换为字典格式，并对 Decimal 类型的数据进行处理。

    :param row: SQLAlchemy Row 对象，包含表列的查询结果
    :return: 序列化后的字典对象，仅包含表列的数据
    """
    result = {}
    for column in row.__table__.columns.keys():
        v = getattr(row, column)
        # 如果值是 Decimal 类型，则使用 fastapi 提供的 decimal_encoder 进行转换
        if isinstance(v, Decimal):
            v = decimal_encoder(v)
        result[column] = v
    return result


def select_list_serialize(row: Sequence[R]) -> list[dict[str, Any]]:
    """
    序列化 SQLAlchemy 查询结果列表。

    对多个 SQLAlchemy Row 对象依次调用 `select_columns_serialize` 方法，将查询结果列表转换为字典列表。

    :param row: 包含多个 SQLAlchemy Row 对象的序列
    :return: 序列化后的字典列表
    """
    result = [select_columns_serialize(_) for _ in row]
    return result


def select_as_dict(row: RowData, use_alias: bool = False) -> dict:
    """
    将 SQLAlchemy 查询结果转换为字典格式（可以包含关联数据）。

    默认直接使用 Row 对象的 `__dict__` 属性。如果设置 `use_alias` 为 True，
    则会返回列的别名作为键（如果列未定义别名，不建议设置为 True）。

    :param row: SQLAlchemy Row 对象
    :param use_alias: 是否使用列的别名作为键（默认 False）
    :return: 转换后的字典
    """
    if not use_alias:
        # 如果不使用别名，直接获取对象的字典属性
        result = row.__dict__
        # 删除 SQLAlchemy 自动生成的内部状态属性
        if '_sa_instance_state' in result:
            del result['_sa_instance_state']
    else:
        # 如果使用别名，遍历对象的所有列属性
        result = {}
        mapper = class_mapper(row.__class__)  # 获取对象的类映射
        for prop in mapper.iterate_properties:
            # 判断属性是否为 列属性 或 同义词属性
            if isinstance(prop, (ColumnProperty, SynonymProperty)):
                key = prop.key  # 获取列的键（可能是别名）
                result[key] = getattr(row, key)

    return result


class MsgSpecJSONResponse(JSONResponse):
    """使用高性能 msgspec 库实现的 JSON 响应类。"""

    def render(self, content: Any) -> bytes:
        return json.encode(content)
