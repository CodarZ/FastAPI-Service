"""角色 Schema 定义

包含角色相关的所有 Schema：Base/Create/Update/Patch*/Detail/Info/ListItem/Simple/Option/Filter/Map
"""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase
from backend.utils.validator import IdsListInt, RoleCodeStr, StatusInt

if TYPE_CHECKING:
    from backend.app.admin.schema.sys_dept import SysDeptSimple
    from backend.app.admin.schema.sys_menu import SysMenuSimple
    from backend.app.admin.schema.sys_user import SysUserSimple


# ==================== 基础 Schema ====================
class SysRoleBase(SchemaBase):
    """角色基础 Schema（核心字段复用）"""

    name: str = Field(min_length=1, max_length=64, description='角色名称')
    code: RoleCodeStr = Field(description='权限字符串')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysRoleCreate(SysRoleBase):
    """角色创建请求"""

    data_scope: int = Field(
        default=0, ge=0, le=4, description='数据范围(0全部 1本部门及子部门 2本部门 3仅本人 4自定义部门)'
    )
    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')
    menu_ids: IdsListInt = Field(default_factory=list, description='菜单ID列表')
    dept_ids: IdsListInt = Field(default_factory=list, description='自定义数据权限-部门ID列表')


class SysRoleUpdate(SysRoleBase):
    """角色更新请求（全量更新）"""

    data_scope: int = Field(
        default=0, ge=0, le=4, description='数据范围(0全部 1本部门及子部门 2本部门 3仅本人 4自定义部门)'
    )
    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')
    menu_ids: IdsListInt = Field(default_factory=list, description='菜单ID列表')
    dept_ids: IdsListInt = Field(default_factory=list, description='自定义数据权限-部门ID列表')


class SysRolePatchStatus(SchemaBase):
    """角色状态修改"""

    status: StatusInt = Field(description='状态(0停用 1正常)')


class SysRolePatchDataScope(SchemaBase):
    """角色数据范围修改"""

    data_scope: int = Field(ge=0, le=4, description='数据范围(0全部 1本部门及子部门 2本部门 3仅本人 4自定义部门)')
    dept_ids: IdsListInt = Field(default_factory=list, description='自定义数据权限-部门ID列表')


class SysRoleMenuMap(SchemaBase):
    """角色菜单映射（多对多关系维护）"""

    menu_ids: IdsListInt = Field(description='菜单ID列表')


class SysRoleDeptMap(SchemaBase):
    """角色部门映射（多对多关系维护，用于自定义数据权限）"""

    dept_ids: IdsListInt = Field(description='部门ID列表')


class SysRoleBatchDelete(SchemaBase):
    """角色批量删除"""

    role_ids: IdsListInt = Field(min_length=1, description='角色ID列表')


class SysRoleBatchPatchStatus(SchemaBase):
    """角色批量状态修改"""

    role_ids: IdsListInt = Field(min_length=1, description='角色ID列表')
    status: StatusInt = Field(description='状态(0停用 1正常)')


# ==================== 输出 Schema ====================
class SysRoleListItem(SchemaBase):
    """角色列表项（表格展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    data_scope: int = Field(description='数据范围')
    status: int = Field(description='状态')
    remark: str | None = Field(default=None, description='备注')
    created_time: datetime = Field(description='创建时间')


class SysRoleInfo(SchemaBase):
    """角色基本信息（卡片预览、关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    data_scope: int = Field(description='数据范围')
    status: int = Field(description='状态')
    remark: str | None = Field(default=None, description='备注')
    menus: list[SysMenuSimple] = Field(default_factory=list, description='菜单列表')
    created_time: datetime = Field(description='创建时间')


class SysRoleDetail(SchemaBase):
    """角色完整详情（详情页展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    data_scope: int = Field(description='数据范围')
    status: int = Field(description='状态')
    remark: str | None = Field(default=None, description='备注')
    menus: list[SysMenuSimple] = Field(default_factory=list, description='菜单列表')
    depts: list[SysDeptSimple] = Field(default_factory=list, description='自定义数据权限-部门列表')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(default=None, description='更新时间')


class SysRoleSimple(SchemaBase):
    """角色简略信息（用于关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')


class SysRoleOption(SchemaBase):
    """角色下拉选项"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')


class SysRoleWithUsers(SchemaBase):
    """角色及其用户（聚合视图）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    users: list[SysUserSimple] = Field(default_factory=list, description='用户列表')


# ==================== 查询 Schema ====================
class SysRoleFilter(SchemaBase):
    """角色查询条件"""

    name: str | None = Field(default=None, max_length=64, description='角色名称(模糊)')
    code: str | None = Field(default=None, max_length=100, description='权限字符串(模糊)')
    status: int | None = Field(default=None, ge=0, le=1, description='状态')
    data_scope: int | None = Field(default=None, ge=0, le=4, description='数据范围')
    created_time_start: datetime | None = Field(default=None, description='创建时间起')
    created_time_end: datetime | None = Field(default=None, description='创建时间止')
    keyword: str | None = Field(default=None, max_length=100, description='关键词(名称/权限字符串)')
