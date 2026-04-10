from pydantic import ConfigDict, Field

from backend.common.enum import MenuEnum, StatusEnum
from backend.common.schema import SchemaBase
from backend.common.schema.type import IdsListInt


# ==================== 基础 Schema ====================
class SysMenuBase(SchemaBase):
    """菜单核心复用字段."""

    name: str = Field(..., max_length=64, description='菜单名称')
    type: MenuEnum = Field(default=MenuEnum.DIRECTORY, description='菜单类型')
    parent_id: int = Field(default=0, description='父菜单 ID（0 表示顶级菜单）')
    path: str = Field(..., max_length=255, description='访问地址路径')
    sort: int = Field(default=0, ge=0, description='排序权重（越小越靠前）')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysMenuCreate(SysMenuBase):
    """菜单创建请求."""

    component: str | None = Field(default=None, max_length=255, description='前端组件路径')
    redirect: str | None = Field(default=None, max_length=255, description='重定向路径')
    permission: str | None = Field(default=None, max_length=128, description='权限标识')
    icon: str | None = Field(default=None, max_length=64, description='菜单图标')
    visible: bool = Field(default=True, description='是否可见')
    is_cache: bool = Field(default=False, description='是否缓存页面')
    is_external: bool = Field(default=False, description='是否外部链接')
    is_frame: bool = Field(default=False, description='是否内嵌 iframe')
    status: StatusEnum = Field(default=StatusEnum.ENABLE, description='状态')


class SysMenuUpdate(SysMenuBase):
    """菜单全量更新请求."""

    component: str | None = Field(default=None, max_length=255, description='前端组件路径')
    redirect: str | None = Field(default=None, max_length=255, description='重定向路径')
    permission: str | None = Field(default=None, max_length=128, description='权限标识')
    icon: str | None = Field(default=None, max_length=64, description='菜单图标')
    visible: bool = Field(default=True, description='是否可见')
    is_cache: bool = Field(default=False, description='是否缓存页面')
    is_external: bool = Field(default=False, description='是否外部链接')
    is_frame: bool = Field(default=False, description='是否内嵌 iframe')
    status: StatusEnum = Field(..., description='状态')


class SysMenuPatchStatus(SchemaBase):
    """菜单状态局部更新请求."""

    status: StatusEnum = Field(..., description='状态')


class SysMenuBatchDelete(SchemaBase):
    """菜单批量删除请求."""

    ids: IdsListInt = Field(..., min_length=1, description='菜单 ID 列表')


class SysMenuBatchPatchStatus(SchemaBase):
    """菜单批量状态更新."""

    ids: IdsListInt = Field(..., min_length=1, description='菜单 ID 列表')
    status: StatusEnum = Field(..., description='状态')


# ==================== 输出 Schema ====================
class SysMenuInfoBase(SysMenuBase):
    """菜单核心输出基类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='菜单 ID')
    tree: str | None = Field(default=None, description='树形路径')
    component: str | None = Field(default=None, description='前端组件路径')
    redirect: str | None = Field(default=None, description='重定向路径')
    permission: str | None = Field(default=None, description='权限标识')
    icon: str | None = Field(default=None, description='菜单图标')
    visible: bool = Field(default=True, description='是否可见')
    is_cache: bool = Field(default=False, description='是否缓存页面')
    is_external: bool = Field(default=False, description='是否外部链接')
    is_frame: bool = Field(default=False, description='是否内嵌 iframe')
    status: StatusEnum = Field(..., description='状态')


class SysMenuInfo(SysMenuInfoBase):
    """菜单通用预览信息."""

    pass


class SysMenuDetail(SysMenuInfoBase):
    """菜单详情."""

    pass


class SysMenuListItem(SysMenuInfoBase):
    """菜单分页列表结构."""

    pass


class SysMenuTreeNode(SysMenuInfoBase):
    """菜单树形节点."""

    children: list['SysMenuTreeNode'] = Field(default_factory=list, description='子菜单节点')


class SysMenuSimple(SchemaBase):
    """菜单嵌套用压缩微型类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='菜单 ID')
    name: str = Field(..., description='菜单名称')
    permission: str | None = Field(default=None, description='权限标识')


# ==================== 选项 Schema ====================
class SysMenuOption(SchemaBase):
    """菜单下拉选项."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    value: int = Field(alias='id', description='选项值')
    label: str = Field(alias='name', description='选项标签')


class SysMenuOptionTree(SysMenuOption):
    """菜单树形下拉选项."""

    children: list['SysMenuOptionTree'] = Field(default_factory=list, description='子选项')


# ==================== 查询 Schema ====================
class SysMenuFilter(SchemaBase):
    """菜单查询过滤条件."""

    name: str | None = Field(default=None, max_length=64, description='按菜单名称过滤')
    type: MenuEnum | None = Field(default=None, description='按菜单类型过滤')
    permission: str | None = Field(default=None, max_length=128, description='按权限标识过滤')
    status: StatusEnum | None = Field(default=None, description='按状态过滤')
    parent_id: int | None = Field(default=None, description='按父菜单 ID 过滤')
