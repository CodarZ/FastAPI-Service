"""菜单 Schema 定义

包含菜单相关的所有 Schema：Base/Create/Update/Patch*/Detail/Info/ListItem/Simple/Option/Filter/TreeNode
"""

from datetime import datetime

from pydantic import ConfigDict, Field, model_validator

from backend.common.enum.custom import MenuEnum
from backend.common.schema import SchemaBase
from backend.utils.validator import PermissionStr, SortInt, StatusInt


# ==================== 基础 Schema ====================
class SysMenuBase(SchemaBase):
    """菜单基础 Schema（核心字段复用）"""

    title: str = Field(min_length=1, max_length=50, description='菜单标题')
    type: MenuEnum = Field(description='菜单类型(0目录 1菜单 2按钮 3外链 4嵌入式组件)')
    icon: str | None = Field(default=None, max_length=50, description='图标')
    sort: SortInt = Field(default=0, description='排序')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysMenuCreate(SysMenuBase):
    """菜单创建请求"""

    parent_id: int | None = Field(default=None, description='父菜单ID')
    path: str | None = Field(default=None, max_length=200, description='访问地址/外链地址')
    component: str | None = Field(default=None, max_length=300, description='组件文件路径')
    permission: PermissionStr | None = Field(default=None, description='权限标识')
    redirect: str | None = Field(default=None, max_length=200, description='重定向地址')
    active_menu: str | None = Field(default=None, max_length=200, description='访问时高亮的菜单')
    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')
    hidden: bool = Field(default=False, description='是否隐藏菜单')
    keep_alive: bool = Field(default=False, description='是否缓存该页面')
    tab: bool = Field(default=True, description='是否在标签页显示')
    breadcrumb: bool = Field(default=True, description='是否在面包屑中显示')

    @model_validator(mode='after')
    def validate_menu_type_fields(self):
        """根据菜单类型验证必填字段"""
        menu_type = self.type

        # 目录(0)或菜单(1)：path 必填
        if menu_type in (MenuEnum.DIRECTORY, MenuEnum.MENU) and not self.path:
            raise ValueError('目录和菜单类型的访问地址不能为空')

        # 菜单(1)：component 必填
        if menu_type == MenuEnum.MENU and not self.component:
            raise ValueError('菜单类型的组件路径不能为空')

        # 按钮(2)：permission 必填
        if menu_type == MenuEnum.BUTTON and not self.permission:
            raise ValueError('按钮类型的权限标识不能为空')

        # 外链(3)：path 必填且需为URL格式
        if menu_type == MenuEnum.LINK and not self.path:
            raise ValueError('外链类型的访问地址不能为空')

        # 嵌入式组件(4)：path 和 component 必填
        if menu_type == MenuEnum.EMBEDDED:
            if not self.path:
                raise ValueError('嵌入式组件的访问地址不能为空')
            if not self.component:
                raise ValueError('嵌入式组件的组件路径不能为空')

        return self


class SysMenuUpdate(SysMenuBase):
    """菜单更新请求（全量更新）"""

    parent_id: int | None = Field(default=None, description='父菜单ID')
    path: str | None = Field(default=None, max_length=200, description='访问地址/外链地址')
    component: str | None = Field(default=None, max_length=300, description='组件文件路径')
    permission: PermissionStr | None = Field(default=None, description='权限标识')
    redirect: str | None = Field(default=None, max_length=200, description='重定向地址')
    active_menu: str | None = Field(default=None, max_length=200, description='访问时高亮的菜单')
    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')
    hidden: bool = Field(default=False, description='是否隐藏菜单')
    keep_alive: bool = Field(default=False, description='是否缓存该页面')
    tab: bool = Field(default=True, description='是否在标签页显示')
    breadcrumb: bool = Field(default=True, description='是否在面包屑中显示')

    @model_validator(mode='after')
    def validate_menu_type_fields(self):
        """根据菜单类型验证必填字段"""
        menu_type = self.type

        if menu_type in (MenuEnum.DIRECTORY, MenuEnum.MENU) and not self.path:
            raise ValueError('目录和菜单类型的访问地址不能为空')
        if menu_type == MenuEnum.MENU and not self.component:
            raise ValueError('菜单类型的组件路径不能为空')
        if menu_type == MenuEnum.BUTTON and not self.permission:
            raise ValueError('按钮类型的权限标识不能为空')
        if menu_type == MenuEnum.LINK and not self.path:
            raise ValueError('外链类型的访问地址不能为空')
        if menu_type == MenuEnum.EMBEDDED:
            if not self.path:
                raise ValueError('嵌入式组件的访问地址不能为空')
            if not self.component:
                raise ValueError('嵌入式组件的组件路径不能为空')

        return self


class SysMenuPatchStatus(SchemaBase):
    """菜单状态修改"""

    status: StatusInt = Field(description='状态(0停用 1正常)')


class SysMenuPatchHidden(SchemaBase):
    """菜单隐藏状态修改"""

    hidden: bool = Field(description='是否隐藏菜单')


class SysMenuPatchSort(SchemaBase):
    """菜单排序修改"""

    sort: SortInt = Field(description='排序')


class SysMenuPatchParent(SchemaBase):
    """菜单父级修改"""

    parent_id: int | None = Field(default=None, description='父菜单ID')


class SysMenuPatchDisplay(SchemaBase):
    """菜单显示设置修改"""

    icon: str | None = Field(default=None, max_length=50, description='图标')
    sort: SortInt | None = Field(default=None, description='排序')
    hidden: bool | None = Field(default=None, description='是否隐藏')
    keep_alive: bool | None = Field(default=None, description='是否缓存')
    tab: bool | None = Field(default=None, description='是否在标签页显示')
    breadcrumb: bool | None = Field(default=None, description='是否在面包屑中显示')


class SysMenuBatchDelete(SchemaBase):
    """菜单批量删除"""

    menu_ids: list[int] = Field(min_length=1, description='菜单ID列表')


class SysMenuBatchPatchStatus(SchemaBase):
    """菜单批量状态修改"""

    menu_ids: list[int] = Field(min_length=1, description='菜单ID列表')
    status: int = Field(ge=0, le=1, description='状态(0停用 1正常)')


# ==================== 输出 Schema ====================
class SysMenuListItem(SchemaBase):
    """菜单列表项（扁平表格展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    path: str | None = Field(default=None, description='访问地址')
    component: str | None = Field(default=None, description='组件路径')
    permission: str | None = Field(default=None, description='权限标识')
    icon: str | None = Field(default=None, description='图标')
    status: int = Field(description='状态')
    hidden: bool = Field(description='是否隐藏')
    sort: int = Field(description='排序')
    parent_id: int | None = Field(default=None, description='父菜单ID')
    # 冗余字段
    parent_title: str | None = Field(default=None, description='父菜单标题')
    created_time: datetime = Field(description='创建时间')


class SysMenuInfo(SchemaBase):
    """菜单基本信息（卡片预览）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    path: str | None = Field(default=None, description='访问地址')
    component: str | None = Field(default=None, description='组件路径')
    permission: str | None = Field(default=None, description='权限标识')
    icon: str | None = Field(default=None, description='图标')
    redirect: str | None = Field(default=None, description='重定向地址')
    status: int = Field(description='状态')
    hidden: bool = Field(description='是否隐藏')
    sort: int = Field(description='排序')
    parent: SysMenuSimple | None = Field(default=None, description='父菜单')
    created_time: datetime = Field(description='创建时间')


class SysMenuDetail(SchemaBase):
    """菜单完整详情（详情页展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    path: str | None = Field(default=None, description='访问地址')
    component: str | None = Field(default=None, description='组件路径')
    permission: str | None = Field(default=None, description='权限标识')
    icon: str | None = Field(default=None, description='图标')
    redirect: str | None = Field(default=None, description='重定向地址')
    active_menu: str | None = Field(default=None, description='访问时高亮的菜单')
    status: int = Field(description='状态')
    hidden: bool = Field(description='是否隐藏')
    keep_alive: bool = Field(description='是否缓存')
    tab: bool = Field(description='是否在标签页显示')
    breadcrumb: bool = Field(description='是否在面包屑中显示')
    sort: int = Field(description='排序')
    parent_id: int | None = Field(default=None, description='父菜单ID')
    parent: SysMenuSimple | None = Field(default=None, description='父菜单')
    remark: str | None = Field(default=None, description='备注')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(default=None, description='更新时间')


class SysMenuSimple(SchemaBase):
    """菜单简略信息（用于关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    permission: str | None = Field(default=None, description='权限标识')


class SysMenuOption(SchemaBase):
    """菜单下拉选项"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    parent_id: int | None = Field(default=None, description='父菜单ID')


class SysMenuTreeNode(SchemaBase):
    """菜单树节点（树形结构展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    path: str | None = Field(default=None, description='访问地址')
    component: str | None = Field(default=None, description='组件路径')
    permission: str | None = Field(default=None, description='权限标识')
    icon: str | None = Field(default=None, description='图标')
    redirect: str | None = Field(default=None, description='重定向地址')
    status: int = Field(description='状态')
    hidden: bool = Field(description='是否隐藏')
    keep_alive: bool = Field(description='是否缓存')
    tab: bool = Field(description='是否在标签页显示')
    breadcrumb: bool = Field(description='是否在面包屑中显示')
    sort: int = Field(description='排序')
    parent_id: int | None = Field(default=None, description='父菜单ID')
    children: list[SysMenuTreeNode] = Field(default_factory=list, description='子菜单列表')


class SysMenuOptionTree(SchemaBase):
    """菜单树形选项（下拉树选择器）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    parent_id: int | None = Field(default=None, description='父菜单ID')
    children: list[SysMenuOptionTree] = Field(default_factory=list, description='子菜单列表')


class SysMenuRoute(SchemaBase):
    """菜单路由配置（前端路由生成）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='菜单ID')
    title: str = Field(description='菜单标题')
    type: int = Field(description='菜单类型')
    path: str | None = Field(default=None, description='访问地址')
    component: str | None = Field(default=None, description='组件路径')
    icon: str | None = Field(default=None, description='图标')
    redirect: str | None = Field(default=None, description='重定向地址')
    hidden: bool = Field(description='是否隐藏')
    keep_alive: bool = Field(description='是否缓存')
    tab: bool = Field(description='是否在标签页显示')
    breadcrumb: bool = Field(description='是否在面包屑中显示')
    active_menu: str | None = Field(default=None, description='访问时高亮的菜单')
    children: list[SysMenuRoute] = Field(default_factory=list, description='子路由')


# ==================== 查询 Schema ====================
class SysMenuFilter(SchemaBase):
    """菜单查询条件"""

    title: str | None = Field(default=None, max_length=50, description='菜单标题(模糊)')
    type: int | None = Field(default=None, ge=0, le=4, description='菜单类型')
    status: int | None = Field(default=None, ge=0, le=1, description='状态')
    hidden: bool | None = Field(default=None, description='是否隐藏')
    parent_id: int | None = Field(default=None, description='父菜单ID')
    permission: str | None = Field(default=None, max_length=128, description='权限标识(模糊)')
    created_time_start: datetime | None = Field(default=None, description='创建时间起')
    created_time_end: datetime | None = Field(default=None, description='创建时间止')
    keyword: str | None = Field(default=None, max_length=100, description='关键词(标题/权限标识)')
