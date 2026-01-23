"""角色 Schema 定义"""

from typing import TYPE_CHECKING

from fastapi import Query
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase
from backend.utils.validator import IdsListInt, LocalDatetime, RoleCodeStr, StatusInt

if TYPE_CHECKING:
    from backend.app.admin.schema.sys_dept import SysDeptSimple
    from backend.app.admin.schema.sys_menu import SysMenuSimple
    from backend.app.admin.schema.sys_user import SysUserSimple


# ==================== 基础 Schema ====================
class SysRoleBase(SchemaBase):
    """角色基础 Schema（核心字段复用）"""

    name: str = Field(min_length=2, max_length=64, description='角色名称')
    code: RoleCodeStr = Field(description='权限字符串')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysRoleCreate(SysRoleBase):
    """角色创建请求"""

    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')
    menu_ids: IdsListInt = Field(default_factory=list, description='菜单ID列表')


class SysRoleUpdate(SchemaBase):
    """角色更新请求（包含菜单权限）"""

    id: int = Field(description='角色ID')
    name: str | None = Field(default=None, min_length=2, max_length=64, description='角色名称')
    code: RoleCodeStr | None = Field(default=None, description='权限字符串')
    remark: str | None = Field(default=None, max_length=500, description='备注')
    status: StatusInt = Field(default=1, description='状态(0停用 1正常)')
    menu_ids: IdsListInt = Field(default_factory=list, description='菜单ID列表')


class SysRolePatchStatus(SchemaBase):
    """角色状态修改"""

    id: int = Field(description='角色ID')
    status: StatusInt = Field(description='状态(0停用 1正常)')


class SysRolePatchDataScope(SchemaBase):
    """角色数据范围修改"""

    id: int = Field(description='角色ID')
    data_scope: int = Field(
        default=4, ge=0, le=4, description='数据范围(0全部, 1本部门及子部门, 2本部门, 3自定义部门, 4仅本人)'
    )
    dept_ids: IdsListInt = Field(default_factory=list, description='自定义数据权限-部门ID列表')

    # TODO 当 data_scope=3 时, dept_ids 不能为空且长度必须大于 0


class SysRoleMenuMap(SchemaBase):
    """角色菜单映射（多对多关系维护）"""

    role_id: int = Field(description='角色ID')
    menu_ids: IdsListInt = Field(default_factory=list, description='菜单ID列表')


class SysRoleDeptMap(SchemaBase):
    """角色部门映射（多对多关系维护, 用于自定义的数据权限）"""

    role_id: int = Field(description='角色ID')
    dept_ids: IdsListInt = Field(description='部门ID列表')


class SysRoleBatchDelete(SchemaBase):
    """批量删除"""

    role_ids: IdsListInt = Field(min_length=1, description='角色ID列表')


class SysRoleBatchUserAuth(SchemaBase):
    """批量（分配/取消授权）用户"""

    role_id: int = Field(description='角色ID')
    user_ids: IdsListInt = Field(min_length=1, description='用户ID列表')


class SysRoleBatchPatchStatus(SchemaBase):
    """批量状态修改"""

    role_ids: IdsListInt = Field(min_length=1, description='角色ID列表')
    status: StatusInt = Field(description='状态(0停用 1正常)')


# ==================== 输出 Schema ====================
class SysRoleListItem(SchemaBase):
    """角色列表项（表格展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    data_scope: int = Field(description='数据范围(0全部, 1本部门及子部门, 2本部门, 3自定义部门, 4仅本人)')
    status: int = Field(description='状态(0停用 1正常)')
    remark: str | None = Field(default=None, description='备注')
    created_time: LocalDatetime = Field(description='创建时间')


class SysRoleInfo(SchemaBase):
    """角色基本信息（卡片预览、关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    data_scope: int = Field(description='数据范围(0全部, 1本部门及子部门, 2本部门, 3自定义部门, 4仅本人)')
    status: int = Field(description='状态(0停用 1正常)')
    remark: str | None = Field(default=None, description='备注')
    menus: list[SysMenuSimple] = Field(default_factory=list, description='菜单列表')
    created_time: LocalDatetime = Field(description='创建时间')


class SysRoleDetail(SchemaBase):
    """角色完整详情"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    data_scope: int = Field(description='数据范围(0全部, 1本部门及子部门, 2本部门, 3自定义部门, 4仅本人)')
    status: int = Field(description='状态(0停用 1正常)')
    remark: str | None = Field(default=None, description='备注')
    menus: list[SysMenuSimple] = Field(default_factory=list, description='菜单列表')
    depts: list[SysDeptSimple] = Field(default_factory=list, description='自定义数据权限-部门列表')
    created_time: LocalDatetime = Field(description='创建时间')
    updated_time: LocalDatetime | None = Field(default=None, description='更新时间')


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
    code: str = Field(description='权限字符串')


class SysRoleWithUsers(SchemaBase):
    """角色及其分配的用户"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='角色ID')
    name: str = Field(description='角色名称')
    code: str = Field(description='权限字符串')
    # status: int = Field(description='状态(0停用 1正常)')
    users: list[SysUserSimple] = Field(default_factory=list, description='用户列表')


# ==================== 查询 Schema ====================
class SysRoleFilter(SchemaBase):
    """角色查询条件"""

    name: str | None = Query(default=None, max_length=64, description='角色名称(模糊)')
    code: str | None = Query(default=None, max_length=100, description='权限字符串(模糊)')
    status: int | None = Query(default=None, ge=0, le=1, description='状态(0停用 1正常)')
    data_scope: int | None = Query(
        default=None, ge=0, le=4, description='数据范围(0全部, 1本部门及子部门, 2本部门, 3自定义部门, 4仅本人)'
    )
    created_time_start: LocalDatetime | None = Query(default=None, description='创建时间起')
    created_time_end: LocalDatetime | None = Query(default=None, description='创建时间止')
