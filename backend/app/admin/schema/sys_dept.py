from pydantic import ConfigDict, Field

from backend.common.enum import StatusEnum
from backend.common.schema import SchemaBase
from backend.common.schema.type import IdsListInt


# ==================== 基础 Schema ====================
class SysDeptBase(SchemaBase):
    """部门核心复用字段."""

    name: str = Field(..., max_length=64, description='部门名称')
    code: str = Field(..., max_length=64, description='部门编码')
    parent_id: int = Field(default=0, description='父部门 ID（0 表示顶级部门）')
    sort: int = Field(default=0, ge=0, description='排序权重（越小越靠前）')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysDeptCreate(SysDeptBase):
    """部门创建请求."""

    leader: str | None = Field(default=None, max_length=64, description='负责人姓名')
    phone: str | None = Field(default=None, max_length=20, description='联系电话')
    email: str | None = Field(default=None, max_length=100, description='邮箱')
    address: str | None = Field(default=None, max_length=255, description='联系地址')
    status: StatusEnum = Field(default=StatusEnum.ENABLE, description='状态')


class SysDeptUpdate(SysDeptBase):
    """部门全量更新请求."""

    leader: str | None = Field(default=None, max_length=64, description='负责人姓名')
    phone: str | None = Field(default=None, max_length=20, description='联系电话')
    email: str | None = Field(default=None, max_length=100, description='邮箱')
    address: str | None = Field(default=None, max_length=255, description='联系地址')
    status: StatusEnum = Field(..., description='状态')


class SysDeptPatchStatus(SchemaBase):
    """部门状态局部更新请求."""

    status: StatusEnum = Field(..., description='状态')


class SysDeptBatchDelete(SchemaBase):
    """部门批量删除请求."""

    ids: IdsListInt = Field(..., min_length=1, description='部门 ID 列表')


class SysDeptBatchPatchStatus(SchemaBase):
    """部门批量状态更新."""

    ids: IdsListInt = Field(..., min_length=1, description='部门 ID 列表')
    status: StatusEnum = Field(..., description='状态')


# ==================== 输出 Schema ====================
class SysDeptInfoBase(SysDeptBase):
    """部门核心输出基类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='部门 ID')
    tree: str | None = Field(default=None, description='树形路径')
    leader: str | None = Field(default=None, description='负责人姓名')
    phone: str | None = Field(default=None, description='联系电话')
    email: str | None = Field(default=None, description='邮箱')
    address: str | None = Field(default=None, description='联系地址')
    status: StatusEnum = Field(..., description='状态')


class SysDeptInfo(SysDeptInfoBase):
    """部门通用预览信息."""

    pass


class SysDeptDetail(SysDeptInfoBase):
    """部门详情."""

    pass


class SysDeptListItem(SysDeptInfoBase):
    """部门分页列表结构."""

    pass


class SysDeptTreeNode(SysDeptInfoBase):
    """部门树形节点."""

    children: list['SysDeptTreeNode'] = Field(default_factory=list, description='子部门节点')


class SysDeptSimple(SchemaBase):
    """部门嵌套用压缩微型类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='部门 ID')
    name: str = Field(..., description='部门名称')


# ==================== 选项 Schema ====================
class SysDeptOption(SchemaBase):
    """部门下拉选项."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    value: int = Field(alias='id', description='选项值')
    label: str = Field(alias='name', description='选项标签')


class SysDeptOptionTree(SysDeptOption):
    """部门树形下拉选项."""

    children: list['SysDeptOptionTree'] = Field(default_factory=list, description='子选项')


# ==================== 查询 Schema ====================
class SysDeptFilter(SchemaBase):
    """部门查询过滤条件."""

    name: str | None = Field(default=None, max_length=64, description='按部门名称过滤')
    code: str | None = Field(default=None, max_length=64, description='按部门编码过滤')
    status: StatusEnum | None = Field(default=None, description='按状态过滤')
    parent_id: int | None = Field(default=None, description='按父部门 ID 过滤')
