"""部门 Schema 定义

包含部门相关的所有 Schema：Base/Create/Update/Patch*/Detail/Info/ListItem/Simple/Option/Filter/TreeNode
"""

from pydantic import model_serializer

from fastapi import Query
from pydantic import ConfigDict, EmailStr, Field


from backend.common.schema import SchemaBase
from backend.utils.validator import IdsListInt, LocalDatetime, MobileStr, SortInt, StatusInt


# ==================== 基础 Schema ====================
class SysDeptBase(SchemaBase):
    """部门基础 Schema（核心字段复用）"""

    title: str = Field(min_length=1, max_length=200, description='部门名称')
    leader: str | None = Field(default=None, max_length=20, description='负责人')
    phone: MobileStr | None = Field(default=None, description='联系电话')
    email: EmailStr | None = Field(default=None, description='邮箱')
    sort: SortInt = Field(default=0, description='显示顺序')


# ==================== 输入 Schema ====================
class SysDeptCreate(SysDeptBase):
    """部门创建请求"""

    parent_id: int | None = Field(default=None, description='上级部门ID')
    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')


class SysDeptUpdate(SysDeptBase):
    """部门更新请求（全量更新）"""

    id: int = Field(description='部门ID')
    parent_id: int | None = Field(default=None, description='上级部门ID')
    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')


class SysDeptPatchStatus(SchemaBase):
    """部门状态修改"""

    id: int = Field(description='部门ID')
    status: StatusInt = Field(description='状态(0停用 1正常)')


class SysDeptPatchParent(SchemaBase):
    """部门父级修改"""

    id: int = Field(description='部门ID')
    parent_id: int | None = Field(default=None, description='上级部门ID')


class SysDeptPatchSort(SchemaBase):
    """部门排序修改"""

    id: int = Field(description='部门ID')
    sort: SortInt = Field(description='显示顺序')


class SysDeptBatchDelete(SchemaBase):
    """部门批量删除"""

    dept_ids: IdsListInt = Field(min_length=1, description='部门ID列表')


class SysDeptBatchPatchStatus(SchemaBase):
    """部门批量状态修改"""

    dept_ids: IdsListInt = Field(min_length=1, description='部门ID列表')
    status: StatusInt = Field(description='状态(0停用 1正常)')


# ==================== 输出 Schema ====================
class SysDeptListItem(SchemaBase):
    """部门列表项（扁平表格展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='部门ID')
    title: str = Field(description='部门名称')
    leader: str | None = Field(default=None, description='负责人')
    phone: str | None = Field(default=None, description='联系电话')
    email: str | None = Field(default=None, description='邮箱')
    status: int = Field(description='状态')
    sort: int = Field(description='显示顺序')
    parent_id: int | None = Field(default=None, description='上级部门ID')
    # 冗余字段
    parent_name: str | None = Field(default=None, description='上级部门名称')
    parent: SysDeptSimple | None = Field(default=None, description='上级部门')
    created_time: LocalDatetime = Field(description='创建时间')

    @model_serializer(mode='wrap')
    def _serialize_model(self, serializer):
        data = serializer(self)
        if self.parent and hasattr(self.parent, 'title'):
            data['parent_name'] = self.parent.title
        data.pop('parent', None)
        return data


class SysDeptInfo(SchemaBase):
    """部门基本信息（卡片预览、关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='部门ID')
    title: str = Field(description='部门名称')
    leader: str | None = Field(default=None, description='负责人')
    phone: str | None = Field(default=None, description='联系电话')
    email: str | None = Field(default=None, description='邮箱')
    status: int = Field(description='状态')
    sort: int = Field(description='显示顺序')
    parent: SysDeptSimple | None = Field(default=None, description='上级部门')
    created_time: LocalDatetime = Field(description='创建时间')


class SysDeptDetail(SysDeptInfo):
    """部门完整详情（详情页展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    parent_id: int | None = Field(default=None, description='上级部门ID')
    updated_time: LocalDatetime | None = Field(default=None, description='更新时间')


class SysDeptSimple(SchemaBase):
    """部门简略信息（用于关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='部门ID')
    title: str = Field(description='部门名称')


class SysDeptOption(SchemaBase):
    """部门下拉选项"""

    id: int = Field(description='部门ID')
    title: str = Field(description='部门名称')


class SysDeptTreeNode(SchemaBase):
    """部门树节点（树形结构展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='部门ID')
    title: str = Field(description='部门名称')
    status: int = Field(description='状态')
    sort: int = Field(description='显示顺序')
    leader: str | None = Field(default=None, description='负责人')
    phone: str | None = Field(default=None, description='联系电话')
    email: str | None = Field(default=None, description='邮箱')
    parent_id: int | None = Field(default=None, description='上级部门ID')
    children: list[SysDeptTreeNode] | None = Field(default=None, description='子部门列表')


class SysDeptOptionTree(SchemaBase):
    """部门树形选项（下拉树选择器）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='部门ID')
    title: str = Field(description='部门名称')
    parent_id: int | None = Field(default=None, description='上级部门ID')
    children: list[SysDeptOptionTree] | None = Field(default=None, description='子部门列表')


# ==================== 查询 Schema ====================
class SysDeptFilter(SchemaBase):
    """部门查询条件"""

    title: str | None = Query(default=None, max_length=200, description='部门名称(模糊)')
    leader: str | None = Query(default=None, max_length=20, description='负责人(模糊)')
    status: int | None = Query(default=None, ge=0, le=1, description='状态')
    parent_id: int | None = Query(default=None, description='上级部门ID')
    created_time_start: LocalDatetime | None = Query(default=None, description='创建时间起')
    created_time_end: LocalDatetime | None = Query(default=None, description='创建时间止')
