#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.app.admin.model import User
from backend.common.model import Base, id_key
from backend.utils.timezone import timezone


class UserSocial(Base):
    """用户 Auth2 社交信息表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_user_social'

    id: Mapped[id_key] = mapped_column(init=False)

    open_id: Mapped[str] = mapped_column(String(128), comment='用户唯一平台标识 open_id')
    platform: Mapped[str] = mapped_column(comment='社交平台名称')
    union_id: Mapped[str | None] = mapped_column(String(128), default=None, comment='平台标识')

    bound_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, comment='绑定时间'
    )

    # 用户社交信息一对多
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(User.id, ondelete='SET NULL'), default=None, comment='用户关联ID'
    )
    user: Mapped['User'] | None = relationship(init=False, back_populates='socials')
