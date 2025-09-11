#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, EmailStr, Field

from backend.common.schema import SchemaBase


class UserInfoBase(SchemaBase):
    """基础属性值, 不包含状态"""

    id: int = Field(description='用户 ID')
    username: str = Field(description='用户名')
    nickname: str = Field(description='昵称')
    email: Optional[EmailStr] = Field(description='邮箱')
    phone: Optional[str] = Field(description='手机号')
    realname: Optional[str] = Field(description='真实姓名')
    avatar: Optional[str] = Field(description='头像')
    gender: Optional[int] = Field(description='性别(0女 1男 3未知)')
    birth_date: Optional[datetime] = Field(description='出生日期')


class UserDetail(UserInfoBase):
    """包含所有属性、状态"""

    model_config = ConfigDict(from_attributes=True)

    uuid: str = Field(description='用户 UUID')

    status: int = Field(description='用户账号状态(0停用 1正常)')
    is_verified: bool = Field(description='是否实名认证')
    is_multi_login: bool = Field(description='是否允许多端登录')
    is_superuser: bool = Field(description='是否超级管理员')
    is_staff: bool = Field(description='是否可以登录后台管理')

    join_time: datetime = Field(description='注册时间')
    last_login_time: Optional[datetime] = Field(description='最后登录时间')


class UserRegisterParams(SchemaBase):
    """注册用户"""

    username: str = Field(description='用户名')
    password: str = Field(description='密码')
