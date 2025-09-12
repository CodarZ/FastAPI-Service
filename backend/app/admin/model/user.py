#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import INTEGER, Boolean, DateTime, LargeBinary, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from backend.common.model import Base, id_key
from backend.database.postgresql import uuid4_str
from backend.utils.timezone import timezone


class User(Base):
    """用户表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_user'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment='用户名')

    password: Mapped[str | None] = mapped_column(String(255), comment='密码')
    salt: Mapped[bytes | None] = mapped_column(LargeBinary(255), comment='加密盐')

    nickname: Mapped[str] = mapped_column(String(20), comment='昵称')
    realname: Mapped[str | None] = mapped_column(String(50), default=None, comment=' 真实姓名')
    email: Mapped[str | None] = mapped_column(String(50), default=None, unique=True, index=True, comment='邮箱')
    phone: Mapped[str | None] = mapped_column(String(11), default=None, unique=True, index=True, comment='手机号')
    avatar: Mapped[str | None] = mapped_column(String(255), default=None, comment='头像')
    gender: Mapped[int | None] = mapped_column(INTEGER, default=None, comment='性别(0女 1男 3未知)')
    birth_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, comment='出生日期')

    status: Mapped[int] = mapped_column(INTEGER, index=True, default=1, comment='用户账号状态(0停用 1正常)')
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否实名认证')
    is_multi_login: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否允许多端登录')
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否是超级管理员')
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否可以登录后台管理')

    join_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, comment='注册时间'
    )
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False, comment='最后登录时间'
    )
