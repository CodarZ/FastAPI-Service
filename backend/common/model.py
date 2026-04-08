import uuid

from datetime import UTC, datetime
from functools import partial
from typing import Annotated

from pydantic.alias_generators import to_snake
from sqlalchemy import BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column

# 通用 Mapped 类型主键, 内部主键 ID (用于外键关联，性能更好)
id_key = Annotated[
    int,
    mapped_column(
        BigInteger,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
        init=False,
        sort_order=-999,
        comment='主键 ID',
    ),
]

# 业务主键 UUID (用于对外暴露，安全性更好)
uuid_key = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        unique=True,
        index=True,
        default=uuid.uuid4,
        sort_order=-998,
        comment='业务唯一标识 UUID',
    ),
]


class UserMixin(MappedAsDataclass):
    """用户 `Mixin` 数据类."""

    created_by: Mapped[int] = mapped_column(sort_order=981, comment='创建者')
    updated_by: Mapped[int | None] = mapped_column(init=False, default=None, sort_order=982, comment='更新者')


class DateTimeMixin(MappedAsDataclass):
    """日期时间 `Mixin` 数据类.

    时间处理方式：
        - 使用应用层生成的带时区时间戳（`datetime.now(tz=UTC)`）
        - DateTime(timezone=True) 映射为 PostgreSQL TIMESTAMPTZ
        - 数据库自动转换为 UTC 存储, 读取时根据连接时区返回
    """

    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        init=False,
        default_factory=partial(datetime.now, tz=UTC),
        sort_order=991,
        comment='创建时间',
    )
    updated_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        init=False,
        default=None,
        onupdate=partial(datetime.now, tz=UTC),
        sort_order=992,
        comment='更新时间',
    )


class MappedBase(AsyncAttrs, DeclarativeBase):
    """异步 ORM 映射基类.

    - 所有继承此基类的模型将自动获得表名生成和注释功能
    - 使用 `Mapped[Type]` 类型注解可获得完整的类型检查支持
    - 延迟加载的关系属性必须通过 `awaitable_attrs` 访问以保持异步安全
    - 所有映射类中使用 `mapped_column()`
    """

    # 将 Mapped[datetime] 自动映射到 PostgreSQL 的 TIMESTAMPTZ 类型
    type_annotation_map = {datetime: DateTime(timezone=True)}

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        """自动生成蛇形命名数据库表名（PascalCase → snake_case）."""
        return to_snake(cls.__name__)

    @declared_attr.directive
    def __table_args__(cls) -> dict[str, str]:  # type: ignore[override]
        """自动设置表配置项.

        - 将模型 docstring 设置为数据库表注释
        """
        return {'comment': cls.__doc__ or ''}


class DataClassBase(MappedAsDataclass, MappedBase):
    """声明式 Dataclass 基类（抽象基类）.

    适用场景：
        ✅ 多对多关联表：如 `UserRole` 关联表，通常只需 ID 映射，无需审计时间戳
        ✅ 配置/字典表：如 `Dictionary`、`Region` 等相对静态的配置数据
        ✅ API 序列化：利用 `asdict(obj)` 将模型快速转为字典返回给前端
        ✅ 批量实例化：利用自动生成的 `__init__` 进行 `User(name="Alice", age=18)` 快速创建对象

    使用注意事项：
        ⚠️  自增主键（`id`）需要标记 `init=False`
        ⚠️  关系字段需要 `default=None` 或 `default_factory=list`
        ⚠️  字段顺序影响 `__init__` 参数顺序（使用 `sort_order` 调整）
    """

    __abstract__ = True


class Base(DataClassBase, DateTimeMixin):
    """业务模型基类.

    - 自动添加时间戳字段 `created_time` 和 `updated_time`

    不适用场景：
        ❌ 极简关联表：如 `user_to_role` 这种纯粹的 ID 映射中间表（建议用 `DataClassBase`）
        ❌ 外部导入数据：已有明确外部时间戳、无需系统自动生成的记录
        ❌ 统计视图：映射数据库 View 的模型
    """

    __abstract__ = True
