#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import INTEGER, LONGTEXT, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.app.admin.model import Menu, User
from backend.app.admin.model.m2m import sys_role_menu, sys_user_role
from backend.common.model import Base, id_key


class Role(Base):
    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_role'

    id: Mapped[id_key] = mapped_column(init=False)

    name: Mapped[str] = mapped_column(String(20), unique=True, comment='角色名称')
    code: Mapped[str] = mapped_column(String(20), unique=True, comment='角色编码')
    status: Mapped[int] = mapped_column(INTEGER, default=1, comment='角色状态（0停用 1正常）')

    remark: Mapped[str | None] = mapped_column(LONGTEXT(), default=None, comment='备注')

    # 用户-角色  多对多
    users: Mapped[list[User]] = relationship(init=False, secondary=sys_user_role, back_populates='roles')

    # 角色菜单多对多
    menus: Mapped[list[Menu]] = relationship(init=False, secondary=sys_role_menu, back_populates='roles')
