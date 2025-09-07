#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column

from backend.utils.timezone import timezone

# 通用 Mapped 类型主键, 需手动添加
# 提供了一个预配置的数据库主键类型, 用于 SQLAlchemy 模型类
#
# 使用方式:
# 1. MappedBase 类继承方式:
#    id: Mapped[id_key]
#
# 2. DataClassBase 或 Base 类继承方式:
#    id: Mapped[id_key] = mapped_column(init=False)
id_key = Annotated[
    int,
    mapped_column(
        BigInteger,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
        sort_order=-999,
        comment='主键 Id',
    ),
]


class UserMixin(MappedAsDataclass):
    """用户 `Mixin` 数据类"""

    created_by: Mapped[int] = mapped_column(sort_order=996, comment='创建者')
    updated_by: Mapped[int | None] = mapped_column(init=False, default=None, sort_order=998, comment='更新者')


class DateTimeMixin(MappedAsDataclass):
    """日期时间 Mixin 数据类"""

    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, sort_order=997, comment='创建时间'
    )
    updated_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False, onupdate=timezone.now, sort_order=999, comment='更新时间'
    )


class MappedBase(AsyncAttrs, DeclarativeBase):
    """声明式基类, 作为所有基类或数据模型类的父类而存在

    特性说明：
    - ✅ 支持异步操作（继承自 `AsyncAttrs`）：
        允许在异步环境中对 ORM 实例进行 `await` 操作, 例如：
        + `await session.refresh(obj)`
        + `await session.delete(obj)`。

        `文档<https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs>`__

    - ✅ 启用 SQLAlchemy 2.0 风格的声明式映射（继承自 `DeclarativeBase`）：
        自动识别类字段并映射为数据库表结构
        推荐用 `Mapped[...]` + `mapped_column()` 定义字段。
        `文档<https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动生成表名"""
        return cls.__name__.lower()

    @declared_attr.directive
    def __table_args__(cls) -> dict:
        """自动设置表配置项"""
        return {'comment': cls.__doc__ or ''}


class DataClassBase(MappedAsDataclass, MappedBase):
    """ORM 数据类模型基类（抽象类）。

    此基类结合了 SQLAlchemy 的 `MappedAsDataclass` 与自定义的 `MappedBase`，既拥有 ORM 映射能力，
    又支持 Python 原生 `@dataclass` 的便利性（如自动生成构造函数、默认值处理等），

    ✅ 特性说明：
    - 自动生成 `__init__()` 构造器；
    - 与 `Mapped[...]`、`mapped_column()` 配合使用；
    - 避免重复编写 ORM 映射模板代码；
    - 继承的子类会映射为数据库表。
    """

    __abstract__ = True


class Base(DataClassBase, DateTimeMixin):
    """项目通用模型抽象基类

    ✅ 继承特性：
    - `DataClassBase`：支持 ORM 声明式映射 + 数据类语法（自动生成构造函数、字段类型检查等）；
    - `DateTimeMixin`：自动添加创建时间 (`created_time`) 和更新时间 (`updated_time`) 字段。

    ✅ 用途说明：
    - 作为项目中业务模型类的统一父类；
    - 提供一致的字段结构、表配置方式；
    - 避免每个模型类重复定义时间字段或通用字段；
    - 继承的子类会映射为数据库表。

    示例:
    >>> class User(Base):
    ...     id: Mapped[id_key] = mapped_column(init=False)
    ...     username: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment='用户名')
    """

    __abstract__ = True
