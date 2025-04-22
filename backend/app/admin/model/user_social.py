#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.app.admin.model import User
from backend.common.model import Base, id_key


class UserSocial(Base):
    """用户auth2.0社交信息表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_user_social'

    id: Mapped[id_key] = mapped_column(init=False)

    source: Mapped[str] = mapped_column(String(20), comment='用户来源')
    open_id: Mapped[str | None] = mapped_column(String(20), default=None, comment='用户 open id')
    uid: Mapped[str | None] = mapped_column(String(20), default=None, comment='用户 UID')
    union_id: Mapped[str | None] = mapped_column(String(20), default=None, comment='用户 union id')
    scope: Mapped[str | None] = mapped_column(String(120), default=None, comment='用户 授予权限')
    code: Mapped[str | None] = mapped_column(String(50), default=None, comment='授权 Code')

    # 用户社交信息一对多
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('sys_user.id', ondelete='SET NULL'), default=None, comment='用户关联ID'
    )
    user: Mapped[User | None] = relationship(init=False, back_populates='socials')
