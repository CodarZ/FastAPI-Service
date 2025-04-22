#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import INTEGER, VARBINARY, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.app.admin.model import Dept, Role, UserSocial
from backend.app.admin.model.m2m import sys_user_role
from backend.common.model import Base, id_key
from backend.database.mysql import uuid4_str
from backend.utils.timezone import timezone


class User(Base):
    """用户表

    使用邮箱注册：
    1. `username`默认为邮箱。
    2. 需要填写`password`。

    使用手机号验证码注册：
    1. `username`默认为手机号。
    2. `password`默认为空。

    授权登录下：
    1. `username`默认为获取到的一些数据。
    2. `password`默认为空。
    3. 是否需要绑定手机号、邮箱等信息？
    """

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_user'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment='用户名')

    password: Mapped[str | None] = mapped_column(String(255), comment='密码')
    salt: Mapped[bytes | None] = mapped_column(VARBINARY(255), comment='加密盐')

    nickname: Mapped[str] = mapped_column(String(20), comment='昵称')
    email: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, default=None, comment='邮箱')
    phone: Mapped[str | None] = mapped_column(String(11), unique=True, index=True, default=None, comment='手机号')
    avatar: Mapped[str | None] = mapped_column(String(255), default=None, comment='头像')
    gender: Mapped[int | None] = mapped_column(INTEGER, default=None, comment='性别(0女 1男 3未知)')
    birth_date: Mapped[datetime | None] = mapped_column(DateTime, default=None, comment='出生日期')

    status: Mapped[int] = mapped_column(INTEGER, index=True, default=1, comment='用户账号状态(0停用 1正常)')
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否实名认证')
    is_multi_login: Mapped[bool] = mapped_column(Boolean(), default=False, comment='是否重复登陆')
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False, comment='是否是超级管理员')
    is_staff: Mapped[bool] = mapped_column(Boolean(), default=False, comment='是否可以登录后台管理')

    join_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, comment='注册时间'
    )
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False, onupdate=timezone.now, comment='上次登录时间'
    )
    updated_username_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        init=False,
        default_factory=timezone.now,
        onupdate=timezone.now,
        comment='上次更新用户名的时间',
    )

    # 用户-社交  一对多
    socials: Mapped[list[UserSocial]] = relationship(init=False, back_populates='user')

    # 用户-部门  一对多
    dept_id: Mapped[int | None] = mapped_column(
        ForeignKey('sys_dept.id', ondelete='SET NULL'), default=None, comment='关联部门 ID'
    )
    dept: Mapped[Dept | None] = relationship(init=False, back_populates='users')

    # 用户-角色  多对多
    roles: Mapped[list[Role]] = relationship(init=False, secondary=sys_user_role, back_populates='users')
