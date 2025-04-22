#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from sqlalchemy import INTEGER, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.app.admin.model import User
from backend.common.model import Base, id_key


class Dept(Base):
    """部门表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_dept'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(50), comment='部门名称')
    sort: Mapped[int] = mapped_column(INTEGER, default=0, comment='排序')
    leader: Mapped[str | None] = mapped_column(String(20), default=None, comment='负责人')
    phone: Mapped[str | None] = mapped_column(String(11), default=None, comment='手机')
    email: Mapped[str | None] = mapped_column(String(50), default=None, comment='邮箱')
    status: Mapped[int] = mapped_column(INTEGER, default=1, comment='部门状态(0停用 1正常)')

    is_del: Mapped[bool] = mapped_column(Boolean(), default=False, comment='是否删除')

    # 部门一对多
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey('sys_dept.id', ondelete='SET NULL'), default=None, index=True, comment='父部门ID'
    )
    parent: Mapped[Optional['Dept']] = relationship(init=False, back_populates='children', remote_side=[id])
    children: Mapped[Optional[list['Dept']]] = relationship(init=False, back_populates='parent')

    # 部门用户一对多
    users: Mapped[list[User]] = relationship(init=False, back_populates='dept')
