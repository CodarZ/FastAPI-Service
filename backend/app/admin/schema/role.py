#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.admin.schema.menu import MenuInfo
from backend.common.schema import SchemaBase


class RoleBase(SchemaBase):
    """角色"""

    name: str = Field(..., description='角色名称')
    code: str = Field(..., description='角色编码')
    status: int = Field(default=1, description='角色状态（0停用 1正常）')
    remark: str | None = Field(default=None, description='备注')


class RoleCreate(RoleBase):
    """角色创建"""

    menus: list[int] = Field(default=[], description='菜单 ID 列表')


class RoleUpdate(RoleBase):
    """角色更新"""

    menus: list[int] = Field(default=[], description='菜单 ID 列表')


class RoleInfo(RoleBase):
    """角色信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='角色 ID')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(description='更新时间')


class RoleWithRelationInfo(RoleInfo):
    """角色信息（包含菜单）"""

    menus: list[MenuInfo] = Field(default=[], description='菜单 ID 列表')
