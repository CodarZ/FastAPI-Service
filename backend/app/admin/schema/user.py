#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import datetime
from typing import Any, Optional, Self

from pydantic import ConfigDict, EmailStr, Field, model_validator

from backend.app.admin.schema.dept import DeptInfo
from backend.app.admin.schema.role import RoleInfo
from backend.common.schema import SchemaBase


class UserBase(SchemaBase):
    username: str = Field(description='用户名')
    email: Optional[EmailStr] = Field(description='邮箱')
    phone: Optional[str] = Field(description='手机号')
    nickname: str = Field(description='昵称')
    realname: Optional[str] = Field(description='真实姓名')
    avatar: Optional[str] = Field(description='头像')
    gender: Optional[int] = Field(description='性别(0女 1男 3未知)')
    birth_date: Optional[datetime] = Field(description='出生日期')

    dept_id: Optional[int] = Field(description='部门 ID')

    status: Optional[int] = Field(description='用户账号状态(0停用 1正常)')
    is_verified: Optional[bool] = Field(description='是否实名认证')
    is_multi_login: Optional[bool] = Field(description='是否允许多端登录')
    is_admin: Optional[bool] = Field(description='是否超级管理员')
    is_staff: Optional[bool] = Field(description='是否可以登录后台管理')


class UserAuth(SchemaBase):
    """登录账户"""

    username: str = Field(description='用户名, 手机号或邮箱')
    password: Optional[str] = Field(description='密码')
    code: Optional[str] = Field(description='手机号验证码')
    # captcha: str = Field(description='图形验证码')


class UserCreateEmail(SchemaBase):
    email: EmailStr = Field(description='邮箱')
    password: str = Field(description='密码')
    # captcha: str = Field(description='图形验证码')


class UserCreatePhone(SchemaBase):
    phone: str = Field(max_length=11, description='手机号')
    # code: str = Field(description='手机验证码')
    captcha: str = Field(description='图形验证码')


class UserCreate(SchemaBase):
    """添加用户

    常用于后台添加用户
    """

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(max_length=20, description='用户名')
    password: Optional[str] = Field(description='密码（默认 123456）')
    phone: str = Field(max_length=11, description='手机号')
    email: Optional[EmailStr] = Field(description='邮箱')
    nickname: str = Field(description='昵称')
    realname: Optional[str] = Field(description='真实姓名')
    avatar: Optional[str] = Field(description='头像')
    gender: Optional[int] = Field(description='性别(0女 1男 3未知)')
    birth_date: Optional[datetime] = Field(description='出生日期')

    dept_id: Optional[int] = Field(description='部门 ID')
    role_ids: Optional[list[int]] = Field(default=[], description='角色 ID 列表')

    status: Optional[int] = Field(description='用户账号状态(0停用 1正常)')
    is_verified: Optional[bool] = Field(description='是否实名认证')
    is_multi_login: Optional[bool] = Field(description='是否允许多端登录')
    is_admin: Optional[bool] = Field(description='是否超级管理员')
    is_staff: Optional[bool] = Field(description='是否可以登录后台管理')


class UserUpdate(SchemaBase):
    """用户更新"""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(max_length=20, description='用户名')
    password: Optional[str] = Field(description='密码（默认 123456）')
    phone: str = Field(max_length=11, description='手机号')
    email: Optional[EmailStr] = Field(description='邮箱')
    nickname: str = Field(description='昵称')
    realname: Optional[str] = Field(description='真实姓名')
    avatar: Optional[str] = Field(description='头像')
    gender: Optional[int] = Field(description='性别(0女 1男 3未知)')
    birth_date: Optional[datetime] = Field(description='出生日期')

    dept_id: Optional[int] = Field(description='部门 ID')
    role_ids: Optional[list[int]] = Field(default=[], description='角色 ID 列表')

    status: Optional[int] = Field(description='用户账号状态(0停用 1正常)')
    is_verified: Optional[bool] = Field(description='是否实名认证')
    is_multi_login: Optional[bool] = Field(description='是否允许多端登录')
    is_admin: Optional[bool] = Field(description='是否超级管理员')
    is_staff: Optional[bool] = Field(description='是否可以登录后台管理')


class UserInfo(UserBase):
    """用户信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='用户 ID')
    uuid: str = Field(description='用户 UUID')

    join_time: datetime = Field(description='注册时间')
    last_login_time: Optional[datetime] = Field(description='最后登录时间')
    updated_username_time: datetime = Field(description='上次更新用户名的时间')


class UserInfoWithRelations(UserInfo):
    """用户信息详情（包含部门、角色）"""

    model_config = ConfigDict(from_attributes=True)

    dept: Optional[DeptInfo] = Field(description='部门信息')
    roles: Optional[list[RoleInfo]] = Field(description='角色信息列表')


class UserInfoWithRelationInfo(UserInfoWithRelations):
    """用户信息详情（包含部门、角色）"""

    model_config = ConfigDict(from_attributes=True)

    dept: str | None = Field(description='部门信息')  # type: ignore
    roles: list[str] = Field(description='角色信息列表')  # type: ignore

    @model_validator(mode='before')
    @classmethod
    def handle(cls, data: Any) -> Self:
        """处理部门和角色数据"""
        dept = data['dept']
        if dept:
            data['dept'] = dept['name']
        roles = data['roles']
        if roles:
            data['roles'] = [role['name'] for role in roles]
        return data


class CurrentUserInfoWithRelationInfo(UserInfoWithRelationInfo):
    """当前用户信息详情（包含部门、角色）"""

    model_config = ConfigDict(from_attributes=True)
