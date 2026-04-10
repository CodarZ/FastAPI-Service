from typing import TYPE_CHECKING

from pydantic import ConfigDict, Field

from backend.common.enum import StatusEnum
from backend.common.schema import SchemaBase

if TYPE_CHECKING:
    from backend.common.schema.type import IdsListInt


# ==================== 基础 Schema ====================
class DomainEntityBase(SchemaBase):
    """实体核心复用字段."""

    name: str = Field(..., max_length=64, description='名称')
    code: str = Field(..., max_length=64, description='编码')
    parent_id: int = Field(default=0, description='逻辑父级 ID')
    sort: int = Field(default=0, description='排序权重')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class DomainEntityCreate(DomainEntityBase):
    """创建请求 (`extra='ignore'`)."""

    status: StatusEnum = Field(default=StatusEnum.ENABLE, description='状态')


class DomainEntityUpdate(DomainEntityBase):
    """全量更新请求 (`extra='ignore'`)."""

    status: StatusEnum = Field(..., description='状态')


class DomainEntityPatchStatus(SchemaBase):
    """单独局部更新请求 (`extra='ignore'`)."""

    status: StatusEnum = Field(..., description='状态')


class DomainEntityBatchDelete(SchemaBase):
    """批量删除请求."""

    ids: IdsListInt = Field(..., min_length=1, description='实体 ID 列表')


class DomainEntityBatchPatchStatus(SchemaBase):
    """批量状态更新."""

    ids: IdsListInt = Field(..., min_length=1, description='实体 ID 列表')
    status: StatusEnum = Field(..., description='状态')


# ==================== 输出 Schema ====================
class DomainEntityInfoBase(DomainEntityBase):
    """核心输出基类."""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description='实体内 ID')
    status: StatusEnum = Field(..., description='状态')


class DomainEntityInfo(DomainEntityInfoBase):
    """通用预览卡片 / 基本信息."""

    pass


class DomainEntityDetail(DomainEntityInfoBase):
    """深度实体详情 (包含计算关联字段)."""

    # 假设此处有关联对象需要下发:
    # _ref_entities: list[EntitySimple] = Field(default_factory=list, exclude=True)
    #
    # @computed_field(description='扁平化提取下属 ID 集合')
    # @property
    # def ref_ids(self) -> list[int]:
    #     return [ref.id for ref in self._ref_entities]
    pass


class DomainEntityListItem(DomainEntityInfoBase):
    """分页清单结构."""

    pass


class DomainEntityTreeNode(DomainEntityInfoBase):
    """树形展开实体节点."""

    children: list[DomainEntityTreeNode] = Field(default_factory=list, description='子节点下发')


class DomainEntitySimple(SchemaBase):
    """嵌套用压缩微型类."""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description='ID')
    name: str = Field(..., description='名称')


# ==================== 选项 Schema ====================
class DomainEntityOption(SchemaBase):
    """下拉菜单结构."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    value: int = Field(alias='id', description='下拉选值')
    label: str = Field(alias='name', description='下拉标签')


class DomainEntityOptionTree(DomainEntityOption):
    """嵌套下拉菜单结构."""

    children: list[DomainEntityOptionTree] = Field(default_factory=list, description='子菜单列表')


# ==================== 查询 Schema ====================
class DomainEntityFilter(SchemaBase):
    """GET 高级过滤条件."""

    name: str | None = Field(default=None, max_length=64, description='按名过滤')
    status: StatusEnum | None = Field(default=None, description='按状态过滤')
    parent_id: int | None = Field(default=None, description='按父类查询')
