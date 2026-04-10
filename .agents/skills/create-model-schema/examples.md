# Model & Schema Standard Examples

This document provides minimal, reusable code templates that perfectly align with the current repository's constraints. Use these paradigms to ensure your Python implementation maintains the required architecture.

## 1. SQLAlchemy Model Example (Zero Physical Constraints)

Demonstrates logical-only associative IDs and missing SQLAlchemy relationship declarations.

```python
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, uuid_key


class SysDept(Base):
    """部门表."""

    id: Mapped[id_key] = mapped_column()
    uuid: Mapped[uuid_key] = mapped_column()

    name: Mapped[str] = mapped_column(String(64), index=True, comment='部门名称')
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment='部门编码')
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0, index=True, comment='父部门 ID（逻辑关联）')
    tree: Mapped[str | None] = mapped_column(String(500), default=None, index=True, comment='树路径')
```

## 2. The 15-Tier Suffix Schema Example

Demonstrates precise `ConfigDict` implementations based strictly on the Tier definitions. Note that the inheritance chain must propagate `SchemaBase`'s `extra='ignore'` into the input classes, while selectively declaring `from_attributes=True` into output payloads.

```python
from pydantic import ConfigDict, Field

from backend.common.enum import StatusEnum
from backend.common.schema import SchemaBase
from backend.common.schema.type import IdsListInt


class SysDeptBase(SchemaBase):
    name: str = Field(..., max_length=64, description='部门名称')
    code: str = Field(..., max_length=64, description='部门编码')
    parent_id: int = Field(default=0, description='父部门 ID')


class SysDeptCreate(SysDeptBase):
    status: StatusEnum = Field(default=StatusEnum.ENABLE, description='状态')


class SysDeptUpdate(SysDeptBase):
    status: StatusEnum = Field(..., description='状态')


class SysDeptPatchStatus(SchemaBase):
    status: StatusEnum = Field(..., description='状态')


class SysDeptBatchDelete(SchemaBase):
    ids: IdsListInt = Field(..., min_length=1, description='部门 ID 列表')


class SysDeptBatchPatchStatus(SchemaBase):
    ids: IdsListInt = Field(..., min_length=1, description='部门 ID 列表')
    status: StatusEnum = Field(..., description='状态')


class SysDeptInfoBase(SysDeptBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='部门 ID')
    tree: str | None = Field(default=None, description='树路径')
    status: StatusEnum = Field(..., description='状态')


class SysDeptInfo(SysDeptInfoBase):
    pass


class SysDeptDetail(SysDeptInfoBase):
    pass


class SysDeptListItem(SysDeptInfoBase):
    pass


class SysDeptTreeNode(SysDeptInfoBase):
    children: list['SysDeptTreeNode'] = Field(default_factory=list, description='子节点')


class SysDeptSimple(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='部门 ID')
    name: str = Field(..., description='部门名称')


class SysDeptOption(SchemaBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    value: int = Field(alias='id', description='选项值')
    label: str = Field(alias='name', description='选项标签')


class SysDeptOptionTree(SysDeptOption):
    children: list['SysDeptOptionTree'] = Field(default_factory=list, description='子选项')


class SysDeptFilter(SchemaBase):
    name: str | None = Field(default=None, max_length=64, description='部门名称')
    code: str | None = Field(default=None, max_length=64, description='部门编码')
    status: StatusEnum | None = Field(default=None, description='状态')
```

## 3. Shared Global Types (`common/schema/type`)

Demonstrate extracting global constraints as `Annotated` types utilizing Pydantic V2 core features.

### 3.1 Defining Internal Function (`func.py`)

```python
# backend/common/schema/type/func.py

def uppercase_code_validator(value: str) -> str:
    """将编码统一为大写并做最小校验."""
    value = value.strip().upper()
    if not value:
        raise ValueError('编码不能为空')
    return value
```

### 3.2 Exposing Annotated Alias (`__init__.py`)

```python
# backend/common/schema/type/__init__.py
from typing import Annotated

from pydantic import AfterValidator, StringConstraints

from . import func

CodeStr = Annotated[
    str,
    StringConstraints(min_length=1, max_length=64),
    AfterValidator(func.uppercase_code_validator),
]
```

### 3.3 Consuming inside Schema definitions

```python
from pydantic import Field

from backend.common.schema import SchemaBase
from backend.common.schema.type import CodeStr


class SysDeptCreate(SchemaBase):
    code: CodeStr = Field(..., description='部门编码')
```

### 3.4 Pydantic Contextual Handlers (Full Serialize Scenario)

For phone numbers/sensitive data requiring masking conditionally inside the JSON dump loop.

```python
# backend/common/schema/type/func.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import SerializationInfo


def phone_validator(value: str | None) -> str | None:
    if not value:
        return None
    value = value.replace(' ', '').replace('-', '')
    if len(value) != 11 or not value.isdigit():
        raise ValueError('手机号格式不正确')
    return value


def phone_mask_serialize(value: str | None, info: SerializationInfo) -> str | None:
    # Requires plaintext: model_dump(context={'show_full_phone': True})
    if not value or (info.context or {}).get('show_full_phone'):
        return value
    return f'{value[:3]}****{value[-4:]}'
```

```python
# backend/common/schema/type/__init__.py
from typing import Annotated

from pydantic import AfterValidator, PlainSerializer, WithJsonSchema

from . import func

PhoneMaskedStr = Annotated[
    str,
    AfterValidator(func.phone_validator),
    WithJsonSchema({'type': 'string', 'format': 'mobile'}),
    PlainSerializer(func.phone_mask_serialize, when_used='json-unless-none'),
]
```

```python
# backend/app/admin/schema/sys_admin.py
from pydantic import Field

from backend.common.schema import SchemaBase
from backend.common.schema.type import PhoneMaskedStr


class SysAdminInfo(SchemaBase):
    id: int = Field(..., description='用户 ID')
    phone: PhoneMaskedStr | None = Field(default=None, description='手机号（默认脱敏输出）')
```

## 4. `extra='forbid'` (The Strict Fallback Matrix)

By default, the 15-tier hierarchy inherits `extra='ignore'`. You should ONLY declare `extra='forbid'` dynamically inside a schema acting as a highly deterministic gateway structure.

```python
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class PaymentWebhookPayload(SchemaBase):
    """签名回调入参，字段协议固定，必须严格拒绝未知字段."""

    model_config = ConfigDict(extra='forbid')

    event_id: str = Field(..., description='事件 ID')
    signature: str = Field(..., description='签名')
```

## 5. `Detail` + `computed_field` 关联展开（类型安全规范）

当 `Detail` schema 需要通过 CRUD 层注入关联对象并展开扁平属性时，**必须使用对应实体的 `Simple` Schema 作为精确类型**，禁止使用裸 `list`、`object` 等无类型标注。

### 正确用法 ✅

```python
from pydantic import ConfigDict, Field, computed_field

from backend.common.schema import SchemaBase

from .sys_dept import SysDeptSimple
from .sys_role import SysRoleSimple


class SysAdminInfoBase(SchemaBase):
    """管理员核心输出基类."""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description='管理员 ID')
    username: str = Field(..., description='用户名')
    dept_id: int | None = Field(default=None, description='所属部门 ID')


class SysAdminDetail(SysAdminInfoBase):
    """管理员详情（包含角色和部门关联信息）."""

    # 关联信息（由 CRUD 层注入，序列化时排除）
    _roles: list[SysRoleSimple] = Field(default_factory=list, exclude=True)
    _dept: SysDeptSimple | None = Field(default=None, exclude=True)

    @computed_field(description='角色 ID 列表')
    @property
    def role_ids(self) -> list[int]:
        return [r.id for r in self._roles] if self._roles else []

    @computed_field(description='角色名称列表')
    @property
    def role_names(self) -> list[str]:
        return [r.name for r in self._roles] if self._roles else []

    @computed_field(description='部门名称')
    @property
    def dept_name(self) -> str | None:
        return self._dept.name if self._dept else None
```

### 错误用法 ❌

```python
# 禁止：裸 list 和 object 丢失类型信息，IDE 无法补全，运行时无验证
_roles: list = Field(default_factory=list, exclude=True)
_dept: object | None = Field(default=None, exclude=True)
```

### 规则总结

| 关联类型 | 注入字段类型 | 示例 |
|---------|------------|------|
| 一对多 / 多对多 | `list[XxxSimple]` | `_roles: list[SysRoleSimple]` |
| 多对一 | `XxxSimple \| None` | `_dept: SysDeptSimple \| None` |
