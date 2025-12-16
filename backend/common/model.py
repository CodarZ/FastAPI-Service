"""SQLAlchemy ORM 基础模型

为所有业务模型提供统一的声明式映射基础设施。
"""

from typing import TYPE_CHECKING, Annotated, Any

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column

from backend.utils.timezone import timezone

if TYPE_CHECKING:
    from datetime import datetime

# 通用 Mapped 类型主键
id_key = Annotated[
    int,
    mapped_column(
        __name_pos=BigInteger,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
        sort_order=-999,
        comment='主键 ID',
    ),
]
"""通用主键类型别名（BigInteger 自增主键）。

预配置的数据库主键类型，统一项目中的主键定义标准。

使用方式：

1. 传统映射（MappedBase）：
    ```python
    class User(MappedBase):
        __tablename__ = 'user'
        id: Mapped[id_key]  # 直接使用类型别名
        username: Mapped[str]
    ```
2. Dataclass 映射（DataClassBase/Base）：
    ```python
    class User(DataClassBase):
        __tablename__ = 'user'
        id: Mapped[id_key] = mapped_column(init=False)  # ⚠️ 必须标记 init=False
        username: Mapped[str]

    # __init__ 签名: User(username: str)
    # id 不会出现在构造函数中，插入后由数据库生成
    ```

注意事项：
    ⚠️ Dataclass 模式下必须添加 `mapped_column(init=False)`
    ⚠️ 主键值由数据库生成，插入前为 None
    ⚠️ BigInteger 支持更大范围，推荐用于高并发/大数据量场景
    ⚠️ 如需 UUID 主键，请自定义其他类型别名

参考：
    - SQLAlchemy Annotated Types: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
    - PostgreSQL BIGINT: https://www.postgresql.org/docs/current/datatype-numeric.html
"""


class UserMixin(MappedAsDataclass):
    """用户 `Mixin` 数据类。"""

    created_by: Mapped[int] = mapped_column(sort_order=996, comment='创建者')
    updated_by: Mapped[int | None] = mapped_column(init=False, default=None, sort_order=998, comment='更新者')


class DateTimeMixin(MappedAsDataclass):
    """日期时间 `Mixin` 数据类。

    时间处理方式：
        - 使用应用层生成的带时区时间戳（timezone.now()）
        - DateTime(timezone=True) 映射为 PostgreSQL TIMESTAMPTZ
        - 数据库自动转换为 UTC 存储, 读取时根据连接时区返回

    可选方案：
    - 数据库层时间戳
    """

    created_time: Mapped[datetime] = mapped_column(
        __name_pos=DateTime(timezone=True),
        init=False,
        default_factory=timezone.now,
        sort_order=997,
        comment='创建时间',
    )
    updated_time: Mapped[datetime | None] = mapped_column(
        __name_pos=DateTime(timezone=True),
        init=False,
        onupdate=timezone.now,
        sort_order=999,
        comment='更新时间',
    )


class MappedBase(AsyncAttrs, DeclarativeBase):
    """异步 ORM 映射基类。

    - 所有继承此基类的模型将自动获得表名生成和注释功能
    - 使用 `Mapped[Type]` 类型注解可获得完整的类型检查支持
    - 延迟加载的关系属性必须通过 `awaitable_attrs` 访问以保持异步安全
    - 所有映射类中使用 `mapped_column()`

    `AsyncAttrs <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs>`__

    `DeclarativeBase <https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__

    `mapped_column() <https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column>`__
    ```
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动生成数据库表名"""
        return cls.__name__.lower()

    @declared_attr.directive
    def __table_args__(cls) -> dict[str, Any]:
        """自动设置表配置项"""
        return {'comment': cls.__doc__ or ''}


class DataClassBase(MappedAsDataclass, MappedBase):
    """声明式 Dataclass 基类（抽象基类）。

    无 `UserMixin` 和 `DateTimeMixin`

    使用场景：
        ✅ 需要自动生成构造函数的业务模型
        ✅ 需要结构化初始化参数的实体类
        ✅ 需要 dataclass 特性（如 replace()、asdict()）
        ✅ 与 Pydantic 或其他框架集成时

    注意事项：
        ⚠️  自增主键需要标记 init=False, 避免在 __init__ 中出现
        ⚠️  关系字段需要 default=None 或 default_factory=list
        ⚠️  字段顺序影响 __init__ 参数顺序（使用 sort_order 调整）
    """

    __abstract__ = True


class Base(DataClassBase, DateTimeMixin):
    """业务模型基类(带时间戳的 dataclass)。

    在 DataClassBase 基础上自动添加时间戳字段 `DateTimeMixin`

    不适用场景：
        ❌ 不需要时间戳的关联表（如: 多对多中间表）
        ❌ 需要自定义时间字段的模型
        ❌ 只读的视图映射

    字段初始化顺序：
        由于 dataclass 的限制, 字段顺序为：
        1. 必需参数（无默认值）
        2. 可选参数（有默认值）
        3. 时间字段（init=False, 自动生成）

        可通过 sort_order 参数调整字段在 dataclass 中的顺序。

    注意事项：
        ⚠️  时间字段已标记 init=False, 不会出现在 __init__ 中
        ⚠️  如需自定义时间字段, 继承 DataClassBase 而非 Base
    """

    __abstract__ = True
