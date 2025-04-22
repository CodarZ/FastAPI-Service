#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, EmailStr, Field, model_validator

from backend.app.admin.schema.dept import DeptInfo
from backend.app.admin.schema.role import RoleWithRelationInfo
from backend.common.enum.custom import StatusEnum
from backend.common.schema import CustomEmailStr, CustomPhoneStr, SchemaBase


class UserBase(SchemaBase):
    username: str = Field(..., description='用户名')
    email: Optional[CustomEmailStr] = Field(description='邮箱')
    phone: Optional[CustomPhoneStr] = Field(description='手机号')
    nickname: str = Field(..., description='昵称')
    dept_id: int | None = Field(default=None, description='部门 ID')


class UserAuth(SchemaBase):
    """登录账户"""

    username: str = Field(description='用户名, 手机号或邮箱')
    password: Optional[str] = Field(description='密码')
    code: Optional[str] = Field(description='手机号验证码')
    # captcha: str = Field(..., description='图形验证码')


class UserCreateEmail(SchemaBase):
    email: EmailStr = Field(..., description='邮箱（注册用）')
    password: str = Field(..., description='密码')
    # captcha: str = Field(..., description='图形验证码')


class UserCreatePhone(SchemaBase):
    phone: str = Field(..., description='手机号（注册用）')
    # code: str = Field(..., description='手机验证码')
    captcha: str = Field(..., description='图形验证码')


class UserUpdate(UserBase):
    """用户更新"""

    model_config = ConfigDict(from_attributes=True)

    avatar: str | None = Field(default=None, description='头像')
    gender: int | None = Field(default=None, description='性别(0女 1男 3未知)')
    birth_date: datetime | None = Field(default=None, description='出生日期')

    status: StatusEnum = Field(default=StatusEnum.YES, description='用户账号状态(0停用 1正常)')
    is_admin: bool | None = Field(default=False, description='是否超级管理员')
    is_staff: bool | None = Field(default=False, description='是否可以登录后台管理')
    is_multi_login: bool | None = Field(default=False, description='是否允许多端登录')
    is_verified: bool | None = Field(default=False, description='是否实名认证')


class UserInfo(UserUpdate):
    """用户信息"""

    model_config = ConfigDict(from_attributes=True)

    # id: int = Field(description='用户 ID')
    uuid: str = Field(description='用户 UUID')

    join_time: datetime | None = Field(default=None, description='加入时间')
    last_login_time: datetime | None = Field(default=None, description='最后登录时间')


class UserInfoWithRelations(UserInfo):
    """用户信息详情（包含部门、角色）"""

    model_config = ConfigDict(from_attributes=True)

    dept: DeptInfo | None = Field(None, description='部门信息')
    roles: list[RoleWithRelationInfo] = Field(default=[], description='角色列表')


class CurrentUserInfoWithRelations(UserInfoWithRelations):
    """当前用户信息详情（包含部门、角色）"""

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def handel(cls, data):
        """处理部门和角色数据"""
        dept = data['dept']
        if dept:
            data['dept'] = dept['name']
        roles = data['roles']
        if roles:
            data['roles'] = [role['name'] for role in roles]
        return data
