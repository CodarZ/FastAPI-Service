from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field, computed_field

from backend.common.enum import AccountStatusEnum
from backend.common.schema import SchemaBase
from backend.common.schema.type import CNMobileStr, IdsListInt

from .sys_dept import SysDeptSimple
from .sys_role import SysRoleSimple


# ==================== 基础 Schema ====================
class SysAdminBase(SchemaBase):
    """管理员核心复用字段."""

    username: str = Field(..., max_length=64, description='用户名')
    nickname: str = Field(..., max_length=64, description='昵称')


# ==================== 输入 Schema ====================
class SysAdminCreate(SysAdminBase):
    """管理员创建请求."""

    password: str = Field(..., min_length=6, max_length=128, description='密码')
    realname: str | None = Field(default=None, max_length=50, description='真实姓名')
    email: str | None = Field(default=None, max_length=100, description='邮箱')
    phone: CNMobileStr | None = Field(default=None, description='手机号')
    avatar: str | None = Field(default=None, max_length=500, description='头像 URL')
    gender: int | None = Field(default=None, ge=0, le=2, description='性别：0=女 1=男 2=未知')
    birth_date: datetime | None = Field(default=None, description='出生日期')
    remark: str | None = Field(default=None, max_length=500, description='备注')
    dept_id: int | None = Field(default=None, description='所属部门 ID')
    role_ids: list[int] = Field(default_factory=list, description='关联角色 ID 列表')
    is_multi_login: bool = Field(default=False, description='是否允许多端同时登录')
    status: AccountStatusEnum = Field(default=AccountStatusEnum.ACTIVE, description='账号状态')


class SysAdminUpdate(SysAdminBase):
    """管理员全量更新请求."""

    realname: str | None = Field(default=None, max_length=50, description='真实姓名')
    email: str | None = Field(default=None, max_length=100, description='邮箱')
    phone: CNMobileStr | None = Field(default=None, description='手机号')
    avatar: str | None = Field(default=None, max_length=500, description='头像 URL')
    gender: int | None = Field(default=None, ge=0, le=2, description='性别：0=女 1=男 2=未知')
    birth_date: datetime | None = Field(default=None, description='出生日期')
    remark: str | None = Field(default=None, max_length=500, description='备注')
    dept_id: int | None = Field(default=None, description='所属部门 ID')
    role_ids: list[int] = Field(default_factory=list, description='关联角色 ID 列表')
    is_multi_login: bool = Field(default=False, description='是否允许多端同时登录')
    status: AccountStatusEnum = Field(..., description='账号状态')


class SysAdminPatchStatus(SchemaBase):
    """管理员状态局部更新请求."""

    status: AccountStatusEnum = Field(..., description='账号状态')


class SysAdminPatchPassword(SchemaBase):
    """管理员密码修改请求."""

    old_password: str = Field(..., min_length=6, max_length=128, description='原密码')
    new_password: str = Field(..., min_length=6, max_length=128, description='新密码')
    confirm_password: str = Field(..., min_length=6, max_length=128, description='确认密码')


class SysAdminResetPassword(SchemaBase):
    """管理员密码重置请求（管理端操作）."""

    password: str = Field(..., min_length=6, max_length=128, description='重置后密码')


class SysAdminPatchProfile(SchemaBase):
    """管理员个人资料修改请求."""

    nickname: str | None = Field(default=None, max_length=64, description='昵称')
    realname: str | None = Field(default=None, max_length=50, description='真实姓名')
    email: str | None = Field(default=None, max_length=100, description='邮箱')
    phone: CNMobileStr | None = Field(default=None, description='手机号')
    avatar: str | None = Field(default=None, max_length=500, description='头像 URL')
    gender: int | None = Field(default=None, ge=0, le=2, description='性别：0=女 1=男 2=未知')
    birth_date: datetime | None = Field(default=None, description='出生日期')


class SysAdminRoleMap(SchemaBase):
    """管理员-角色 M:N 映射请求."""

    role_ids: IdsListInt = Field(..., min_length=1, description='角色 ID 列表')


class SysAdminBatchDelete(SchemaBase):
    """管理员批量删除请求."""

    ids: IdsListInt = Field(..., min_length=1, description='管理员 ID 列表')


class SysAdminBatchPatchStatus(SchemaBase):
    """管理员批量状态更新."""

    ids: IdsListInt = Field(..., min_length=1, description='管理员 ID 列表')
    status: AccountStatusEnum = Field(..., description='账号状态')


# ==================== 输出 Schema ====================
class SysAdminInfoBase(SysAdminBase):
    """管理员核心输出基类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='管理员 ID')
    uuid: UUID = Field(..., description='全局唯一标识')
    realname: str | None = Field(default=None, description='真实姓名')
    email: str | None = Field(default=None, description='邮箱')
    phone: CNMobileStr | None = Field(default=None, description='手机号（默认脱敏输出）')
    avatar: str | None = Field(default=None, description='头像 URL')
    gender: int | None = Field(default=None, description='性别')
    dept_id: int | None = Field(default=None, description='所属部门 ID')
    is_super: bool = Field(default=False, description='是否超级管理员')
    is_multi_login: bool = Field(default=False, description='是否允许多端同时登录')
    status: AccountStatusEnum = Field(..., description='账号状态')


class SysAdminInfo(SysAdminInfoBase):
    """管理员通用预览信息."""

    pass


class SysAdminDetail(SysAdminInfoBase):
    """管理员详情（包含角色和部门关联信息）."""

    birth_date: datetime | None = Field(default=None, description='出生日期')
    remark: str | None = Field(default=None, description='备注')
    last_login_ip: str | None = Field(default=None, description='最后登录 IP')
    last_login_time: datetime | None = Field(default=None, description='最后登录时间')

    # 关联信息（由 CRUD 层注入）
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


class SysAdminListItem(SysAdminInfoBase):
    """管理员分页列表结构."""

    last_login_time: datetime | None = Field(default=None, description='最后登录时间')


class SysAdminSimple(SchemaBase):
    """管理员嵌套用压缩微型类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='管理员 ID')
    username: str = Field(..., description='用户名')
    nickname: str = Field(..., description='昵称')


class SysAdminOption(SchemaBase):
    """管理员下拉选项."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    value: int = Field(alias='id', description='选项值')
    label: str = Field(alias='username', description='选项标签')
    nickname: str = Field(description='昵称')


# ==================== 查询 Schema ====================
class SysAdminFilter(SchemaBase):
    """管理员查询过滤条件."""

    username: str | None = Field(default=None, max_length=64, description='按用户名过滤')
    nickname: str | None = Field(default=None, max_length=64, description='按昵称过滤')
    phone: str | None = Field(default=None, max_length=30, description='按手机号过滤')
    email: str | None = Field(default=None, max_length=100, description='按邮箱过滤')
    status: AccountStatusEnum | None = Field(default=None, description='按账号状态过滤')
    dept_id: int | None = Field(default=None, description='按部门 ID 过滤')
