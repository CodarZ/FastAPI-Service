#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import LONGTEXT, DateTime, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from backend.common.enum.custom import StatusEnum
from backend.common.model import DataClassBase, id_key
from backend.utils.timezone import timezone


class LoginLog(DataClassBase):
    """登录日志表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_login_log'

    id: Mapped[id_key] = mapped_column(init=False)
    user_uuid: Mapped[str] = mapped_column(String(50), comment='用户UUID')
    username: Mapped[str] = mapped_column(String(20), comment='用户名')
    status: Mapped[StatusEnum] = mapped_column(insert_default=StatusEnum.YES, comment='登录状态(0失败 1成功)')
    msg: Mapped[str] = mapped_column(LONGTEXT(), comment='提示消息')

    ip: Mapped[str] = mapped_column(String(50), comment='登录IP地址')
    country: Mapped[str | None] = mapped_column(String(50), comment='国家')
    region: Mapped[str | None] = mapped_column(String(50), comment='地区')
    city: Mapped[str | None] = mapped_column(String(50), comment='城市')

    user_agent: Mapped[str] = mapped_column(String(255), comment='请求头')
    os: Mapped[str | None] = mapped_column(String(50), comment='操作系统')
    browser: Mapped[str | None] = mapped_column(String(50), comment='浏览器')
    device: Mapped[str | None] = mapped_column(String(50), comment='设备')

    login_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment='登录时间')
    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, comment='创建时间'
    )
