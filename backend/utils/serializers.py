"""SQLAlchemy 查询结果序列化工具模块

本文件模块提供用于将 SQLAlchemy 查询结果统一转换为原生 Python 字典的工具函数。

--------
SQLAlchemy 查询可能返回多种类型的结果对象，包括：

- ORM 模型实例
    例如：`session.query(User).first()`，返回 `User` 实例。

- Row 对象
    例如：`select(User, Dept).first()`，返回包含多个模型字段的行对象。

- RowMapping
    例如：`result.mappings().first()`，行为类似字典。

由于这些返回类型结构各异，本模块提供统一的序列化工具，将不同类型的查询结果转换为标准 Python 字典。

"""

from typing import Any

from msgspec import json
from sqlalchemy import Row, RowMapping
from starlette.responses import JSONResponse

# RowData 表示可能的查询结果类型
RowData = Row[Any] | RowMapping | Any


# ============================================================================
# 高性能 JSON 响应
# ============================================================================


class MsgSpecJSONResponse(JSONResponse):
    """基于 msgspec 的高性能 JSON 响应类"""

    def render(self, content: Any) -> bytes:
        """将内容编码为 JSON 字节串"""
        return json.encode(content)
