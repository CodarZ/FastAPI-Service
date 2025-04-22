#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enum.custom import MenuEnum, StatusEnum
from backend.common.schema import SchemaBase


class MenuBase(SchemaBase):
    """菜单"""

    title: str = Field(..., description='菜单标题')
    name: str = Field(..., description='菜单名称')
    path: str = Field(..., description='路由地址')
    sort: int = Field(default=0, description='排序')
    icon: str | None = Field(default=None, description='菜单图标')
    type: MenuEnum = Field(default=MenuEnum.directory, description='菜单类型（0目录 1菜单 2按钮）')
    component: str | None = Field(default=None, description='组件路径')
    perms: str | None = Field(default=None, description='权限标识')
    status: StatusEnum = Field(default=StatusEnum.YES, description='菜单状态（0停用 1正常）')
    display: int = Field(default=1, description='是否显示（0否 1是）')
    cache: int = Field(default=1, description='是否缓存（0否 1是）')
    link: str | None = Field(default=None, description='外链地址')
    remark: str | None = Field(default=None, description='备注')
    parent_id: int | None = Field(default=None, description='父菜单 ID')


class MenuCreate(MenuBase):
    """菜单创建"""


class MenuUpdate(MenuBase):
    """菜单更新"""


class MenuInfo(MenuBase):
    """菜单信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='菜单 ID')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')
