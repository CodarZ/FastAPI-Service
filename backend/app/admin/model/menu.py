#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from sqlalchemy import INTEGER, LONGTEXT, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.app.admin.model import Role
from backend.app.admin.model.m2m import sys_role_menu
from backend.common.enum.custom import MenuEnum, StatusEnum
from backend.common.model import Base, id_key


class Menu(Base):
    """菜单表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_menu'

    id: Mapped[id_key] = mapped_column(init=False)
    title: Mapped[str] = mapped_column(String(50), comment='菜单标题')
    name: Mapped[str] = mapped_column(String(50), comment='菜单名称')
    path: Mapped[str] = mapped_column(String(200), comment='路由地址')
    sort: Mapped[int] = mapped_column(INTEGER, default=0, comment='排序')
    icon: Mapped[str | None] = mapped_column(String(100), default=None, comment='菜单图标')
    type: Mapped[int] = mapped_column(INTEGER, default=MenuEnum.directory, comment='菜单类型（0目录 1菜单 2按钮）')
    component: Mapped[str | None] = mapped_column(String(255), default=None, comment='组件路径')
    perms: Mapped[str | None] = mapped_column(String(100), default=None, comment='权限标识')
    status: Mapped[StatusEnum] = mapped_column(INTEGER, default=StatusEnum.YES, comment='菜单状态（0停用 1正常）')
    display: Mapped[int] = mapped_column(INTEGER, default=1, comment='是否显示（0否 1是）')
    cache: Mapped[int] = mapped_column(INTEGER, default=1, comment='是否缓存（0否 1是）')
    link: Mapped[str | None] = mapped_column(LONGTEXT(), default=None, comment='外链地址')
    remark: Mapped[str | None] = mapped_column(LONGTEXT(), default=None, comment='备注')

    # 父级菜单一对多
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey('sys_menu.id', ondelete='SET NULL'), default=None, index=True, comment='父菜单 ID'
    )
    parent: Mapped[Optional['Menu']] = relationship(init=False, back_populates='children', remote_side=[id])
    children: Mapped[Optional[list['Menu']]] = relationship(init=False, back_populates='parent')

    # 菜单角色多对多
    roles: Mapped[list[Role]] = relationship(init=False, secondary=sys_role_menu, back_populates='menus')
