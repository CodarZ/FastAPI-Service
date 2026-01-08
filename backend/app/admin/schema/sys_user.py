"""用户 Schema 定义

包含用户相关的所有 Schema：Base/Create/Update/Patch*/Detail/Info/ListItem/Simple/Option/Filter
"""

from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import Query
from pydantic import ConfigDict, EmailStr, Field, field_validator, model_serializer

from backend.common.schema import SchemaBase
from backend.utils.validator import IdsListInt, MobileStr, PasswordStr, StatusInt, UsernameStr

if TYPE_CHECKING:
    from backend.app.admin.schema.sys_dept import SysDeptSimple
    from backend.app.admin.schema.sys_role import SysRoleSimple


# ==================== 基础 Schema ====================
class SysUserBase(SchemaBase):
    """用户基础 Schema（核心字段复用）"""

    username: UsernameStr = Field(description='用户名')
    nickname: str = Field(min_length=1, max_length=20, description='昵称')
    realname: str | None = Field(default=None, max_length=50, description='真实姓名')
    email: EmailStr | None = Field(default=None, description='邮箱')
    phone: MobileStr | None = Field(default=None, description='手机号')
    gender: int | None = Field(default=None, ge=0, le=3, description='性别(0女 1男 3其他)')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysUserCreate(SysUserBase):
    """用户创建请求"""

    password: PasswordStr = Field(description='密码')
    dept_id: int | None = Field(default=None, description='所属部门ID')
    role_ids: IdsListInt = Field(default_factory=list, description='角色ID列表')
    avatar: str | None = Field(default=None, max_length=500, description='头像URL')
    birth_date: datetime | None = Field(default=None, description='出生日期')
    user_type: str = Field(default='00', max_length=3, description='用户类型')
    status: StatusInt = Field(default=1, description='账号状态(0停用 1正常)')
    is_multi_login: bool = Field(default=False, description='是否允许多端登录')


class SysUserUpdate(SysUserBase):
    """用户更新请求（全量更新, 管理员操作）"""

    id: int = Field(description='用户ID')
    dept_id: int | None = Field(default=None, description='所属部门ID')
    role_ids: IdsListInt = Field(default_factory=list, description='角色ID列表')
    avatar: str | None = Field(default=None, max_length=500, description='头像URL')
    birth_date: datetime | None = Field(default=None, description='出生日期')
    user_type: str = Field(default='00', max_length=3, description='用户类型')
    status: StatusInt = Field(default=1, description='账号状态(0停用 1正常)')
    is_multi_login: bool = Field(default=False, description='是否允许多端登录')
    is_verified: bool = Field(default=False, description='是否实名认证')
    # 注意: is_admin, is_superuser 不应通过普通接口修改, 需通过专门的接口修改


class SysUserPatchStatus(SchemaBase):
    """用户状态修改"""

    id: int = Field(description='用户ID')
    status: StatusInt = Field(description='账号状态(0停用 1正常)')


class SysUserPatchPassword(SchemaBase):
    """用户密码修改"""

    id: int = Field(description='用户ID')
    old_password: str | None = Field(description='旧密码')
    new_password: PasswordStr = Field(description='新密码')
    confirm_password: PasswordStr = Field(min_length=8, max_length=128, description='确认新密码')

    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v: str, info) -> str:
        """验证两次密码一致"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class SysUserResetPassword(SchemaBase):
    """用户密码重置（管理员操作）"""

    id: int = Field(description='用户ID')
    new_password: PasswordStr = Field(description='新密码')


class SysUserPatchProfile(SchemaBase):
    """用户个人资料修改"""

    id: int = Field(description='用户ID')
    nickname: str | None = Field(default=None, min_length=1, max_length=20, description='昵称')
    realname: str | None = Field(default=None, max_length=50, description='真实姓名')
    email: EmailStr | None = Field(default=None, description='邮箱')
    phone: MobileStr | None = Field(default=None, description='手机号')
    avatar: str | None = Field(default=None, max_length=500, description='头像URL')
    gender: int | None = Field(default=None, ge=0, le=3, description='性别(0女 1男 3其他)')
    birth_date: datetime | None = Field(default=None, description='出生日期')


class SysUserRoleMap(SchemaBase):
    """用户角色映射（多对多关系维护）"""

    role_ids: IdsListInt = Field(description='角色ID列表')


class SysUserPatchSuperuser(SchemaBase):
    """用户超级管理员状态修改（仅限超级管理员操作）"""

    id: int = Field(description='用户ID')
    is_superuser: bool = Field(description='是否超级管理员')


class SysUserPatchAdmin(SchemaBase):
    """用户后台管理员状态修改"""

    id: int = Field(description='用户ID')
    is_admin: bool = Field(description='是否后台管理员')


class SysUserBatchDelete(SchemaBase):
    """用户批量删除"""

    user_ids: IdsListInt = Field(min_length=1, description='用户ID列表')


class SysUserBatchPatchStatus(SchemaBase):
    """用户批量状态修改"""

    user_ids: list[int] = Field(min_length=1, description='用户ID列表')
    status: int = Field(ge=0, le=1, description='账号状态(0停用 1正常)')


# ==================== 输出 Schema ====================
class SysUserListItem(SchemaBase):
    """用户列表项（表格展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='用户ID')
    username: str = Field(description='用户名')
    nickname: str = Field(description='昵称')
    email: str | None = Field(default=None, description='邮箱')
    phone: str | None = Field(default=None, description='手机号')
    gender: int | None = Field(default=None, description='性别')
    avatar: str | None = Field(default=None, description='头像')
    status: int = Field(description='账号状态')
    is_verified: bool = Field(description='是否实名认证')
    is_superuser: bool = Field(description='是否超级管理员')
    is_admin: bool = Field(description='是否后台管理员')
    user_type: str | None = Field(default=None, max_length=3, description='用户类型')
    is_multi_login: bool | None = Field(default=None, description='是否允许多端登录')
    dept: SysDeptSimple | None = Field(default=None, description='所属部门')
    dept_id: int | None = Field(default=None, description='所属部门ID')
    # 冗余字段 - 避免关联查询
    dept_name: str | None = Field(default=None, description='部门名称')
    created_time: datetime = Field(description='创建时间')
    last_login_time: datetime | None = Field(default=None, description='最后登录时间')

    @model_serializer(mode='wrap')
    def _serialize_model(self, serializer):
        data = serializer(self)
        if self.dept and hasattr(self.dept, 'title'):
            data['dept_name'] = self.dept.title
        data.pop('dept', None)
        return data


class SysUserInfo(SchemaBase):
    """用户基本信息（卡片预览、关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='用户ID')
    username: str = Field(description='用户名')
    nickname: str = Field(description='昵称')
    realname: str | None = Field(default=None, description='真实姓名')
    email: str | None = Field(default=None, description='邮箱')
    phone: str | None = Field(default=None, description='手机号')
    gender: int | None = Field(default=None, description='性别')
    avatar: str | None = Field(default=None, description='头像')
    status: int = Field(description='账号状态')
    is_superuser: bool = Field(description='是否超级管理员')
    is_admin: bool = Field(description='是否后台管理员')
    dept: SysDeptSimple | None = Field(default=None, description='所属部门')
    dept_id: int | None = Field(default=None, description='所属部门ID')
    dept_name: str | None = Field(default=None, description='所属部门名称')
    created_time: datetime = Field(description='创建时间')

    @model_serializer(mode='wrap')
    def _serialize_model(self, serializer):
        data = serializer(self)
        if self.dept and hasattr(self.dept, 'title'):
            data['dept_name'] = self.dept.title
        data.pop('dept', None)
        return data


class SysUserDetail(SchemaBase):
    """用户完整详情（详情页展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='用户ID')
    username: str = Field(description='用户名')
    nickname: str = Field(description='昵称')
    realname: str | None = Field(default=None, description='真实姓名')
    email: str | None = Field(default=None, description='邮箱')
    phone: str | None = Field(default=None, description='手机号')
    gender: int | None = Field(default=None, description='性别')
    avatar: str | None = Field(default=None, description='头像')
    birth_date: datetime | None = Field(default=None, description='出生日期')
    dept: SysDeptSimple | None = Field(default=None, description='所属部门')
    dept_id: int | None = Field(default=None, description='所属部门ID')
    dept_name: str | None = Field(default=None, description='部门名称')
    user_type: str = Field(description='用户类型')
    status: int = Field(description='账号状态')
    is_multi_login: bool = Field(description='是否允许多端登录')
    is_superuser: bool = Field(description='是否超级管理员')
    is_admin: bool = Field(description='是否后台管理员')
    is_verified: bool = Field(description='是否实名认证')
    roles: list[SysRoleSimple] = Field(default_factory=list, description='角色列表')
    role_ids: list[int] = Field(default_factory=list, description='角色ID列表')
    remark: str | None = Field(default=None, description='备注')
    last_login_time: datetime | None = Field(default=None, description='最后登录时间')
    last_login_ip: str | None = Field(default=None, description='最后登录IP')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(default=None, description='更新时间')

    @model_serializer(mode='wrap')
    def _serialize_model(self, serializer):
        """序列化时提取 dept_name 和 role_ids"""
        data = serializer(self)
        # 提取部门名称
        if self.dept and hasattr(self.dept, 'title'):
            data['dept_name'] = self.dept.title
        # 提取角色ID列表
        if self.roles:
            data['role_ids'] = [role.id for role in self.roles]
        # 移除 dept 和 roles 字段
        # data.pop('dept', None)
        # data.pop('roles', None)
        return data


class SysUserSimple(SchemaBase):
    """用户简略信息（用于关联展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='用户ID')
    username: str = Field(description='用户名')
    nickname: str = Field(description='昵称')
    avatar: str | None = Field(default=None, description='头像')


class SysUserOption(SchemaBase):
    """用户下拉选项"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='用户ID')
    username: str = Field(description='用户名')
    nickname: str = Field(description='昵称')


# ==================== 查询 Schema ====================
class SysUserFilter(SchemaBase):
    """用户查询条件"""

    username: str | None = Query(default=None, max_length=20, description='用户名(模糊)')
    realname: str | None = Query(default=None, max_length=50, description='真实姓名(模糊)')
    nickname: str | None = Query(default=None, max_length=20, description='昵称(模糊)')
    phone: str | None = Query(default=None, max_length=11, description='手机号')
    email: str | None = Query(default=None, description='邮箱')
    user_type: str | None = Query(default=None, max_length=3, description='用户类型')
    status: int | None = Query(default=None, ge=0, le=1, description='账号状态')
    dept_id: int | None = Query(default=None, description='所属部门ID')
    is_verified: bool | None = Query(default=None, description='是否实名认证')
    is_superuser: bool | None = Query(default=None, description='是否超级管理员')
    is_admin: bool | None = Query(default=None, description='是否后台管理员')
    is_multi_login: bool | None = Query(default=None, description='是否允许多端登录')
    created_time_start: datetime | None = Query(default=None, description='创建时间起')
    created_time_end: datetime | None = Query(default=None, description='创建时间止')
    last_login_time_start: datetime | None = Query(default=None, description='最后登录时间起')
    last_login_time_end: datetime | None = Query(default=None, description='最后登录时间止')


class SysUserAdvancedFilter(SysUserFilter):
    """用户高级查询条件"""

    role_id: int | None = Query(default=None, description='角色ID')
    keyword: str | None = Query(
        default=None, max_length=50, description='关键词模糊查询(真实姓名/用户名/昵称/手机号/邮箱)'
    )
