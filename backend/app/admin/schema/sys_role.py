from pydantic import ConfigDict, Field, computed_field

from backend.common.enum import DataScopeEnum, StatusEnum
from backend.common.schema import SchemaBase
from backend.common.schema.type import IdsListInt

from .sys_dept import SysDeptSimple
from .sys_menu import SysMenuSimple


# ==================== 基础 Schema ====================
class SysRoleBase(SchemaBase):
    """角色核心复用字段."""

    name: str = Field(..., max_length=50, description='角色名称')
    code: str = Field(..., max_length=50, description='角色编码')
    sort: int = Field(default=0, ge=0, description='排序权重（越小越靠前）')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysRoleCreate(SysRoleBase):
    """角色创建请求."""

    status: StatusEnum = Field(default=StatusEnum.ENABLE, description='状态')
    data_scope: DataScopeEnum = Field(default=DataScopeEnum.DEPT, description='数据权限范围')
    menu_ids: list[int] = Field(default_factory=list, description='关联菜单 ID 列表')
    dept_ids: list[int] = Field(default_factory=list, description='自定义数据权限部门 ID 列表')


class SysRoleUpdate(SysRoleBase):
    """角色全量更新请求."""

    status: StatusEnum = Field(..., description='状态')
    data_scope: DataScopeEnum = Field(..., description='数据权限范围')
    menu_ids: list[int] = Field(default_factory=list, description='关联菜单 ID 列表')
    dept_ids: list[int] = Field(default_factory=list, description='自定义数据权限部门 ID 列表')


class SysRolePatchStatus(SchemaBase):
    """角色状态局部更新请求."""

    status: StatusEnum = Field(..., description='状态')


class SysRolePatchDataScope(SchemaBase):
    """角色数据权限范围局部更新请求."""

    data_scope: DataScopeEnum = Field(..., description='数据权限范围')
    dept_ids: list[int] = Field(default_factory=list, description='自定义数据权限部门 ID 列表')


class SysRoleMenuMap(SchemaBase):
    """角色-菜单 M:N 映射请求."""

    menu_ids: IdsListInt = Field(..., min_length=1, description='菜单 ID 列表')


class SysRoleBatchDelete(SchemaBase):
    """角色批量删除请求."""

    ids: IdsListInt = Field(..., min_length=1, description='角色 ID 列表')


class SysRoleBatchPatchStatus(SchemaBase):
    """角色批量状态更新."""

    ids: IdsListInt = Field(..., min_length=1, description='角色 ID 列表')
    status: StatusEnum = Field(..., description='状态')


# ==================== 输出 Schema ====================
class SysRoleInfoBase(SysRoleBase):
    """角色核心输出基类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='角色 ID')
    status: StatusEnum = Field(..., description='状态')
    is_system: bool = Field(default=False, description='是否系统内置角色')
    data_scope: DataScopeEnum = Field(..., description='数据权限范围')


class SysRoleInfo(SysRoleInfoBase):
    """角色通用预览信息."""

    pass


class SysRoleDetail(SysRoleInfoBase):
    """角色详情（包含菜单和部门关联信息）."""

    # 关联信息（由 CRUD 层注入）
    _menus: list[SysMenuSimple] = Field(default_factory=list, exclude=True)
    _depts: list[SysDeptSimple] = Field(default_factory=list, exclude=True)

    @computed_field(description='关联菜单 ID 列表')
    @property
    def menu_ids(self) -> list[int]:
        return [m.id for m in self._menus] if self._menus else []

    @computed_field(description='自定义数据权限部门 ID 列表')
    @property
    def dept_ids(self) -> list[int]:
        return [d.id for d in self._depts] if self._depts else []


class SysRoleListItem(SysRoleInfoBase):
    """角色分页列表结构."""

    pass


class SysRoleSimple(SchemaBase):
    """角色嵌套用压缩微型类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='角色 ID')
    name: str = Field(..., description='角色名称')


class SysRoleOption(SchemaBase):
    """角色下拉选项."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    value: int = Field(alias='id', description='选项值')
    label: str = Field(alias='name', description='选项标签')


# ==================== 查询 Schema ====================
class SysRoleFilter(SchemaBase):
    """角色查询过滤条件."""

    name: str | None = Field(default=None, max_length=50, description='按角色名称过滤')
    code: str | None = Field(default=None, max_length=50, description='按角色编码过滤')
    status: StatusEnum | None = Field(default=None, description='按状态过滤')
    data_scope: DataScopeEnum | None = Field(default=None, description='按数据权限范围过滤')
