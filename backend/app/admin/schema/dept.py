#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enum.custom import StatusEnum
from backend.common.schema import CustomEmailStr, CustomPhoneStr, SchemaBase


class DeptBase(SchemaBase):
    """部门"""

    name: str = Field(..., title='部门名称', max_length=50)
    sort: int = Field(0, title='排序', ge=0)
    leader: str | None = Field(None, title='负责人', max_length=20)
    phone: CustomPhoneStr | None = Field(None, title='联系方式', max_length=11)
    email: CustomEmailStr | None = Field(None, title='邮箱', max_length=50)
    status: StatusEnum = Field(StatusEnum.YES, title='部门状态(0停用 1正常)')


class DeptCreate(DeptBase):
    """创建部门"""


class DeptUpdate(DeptBase):
    """更新部门"""


class DeptInfo(DeptBase):
    """部门详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., title='部门ID')
    is_del: bool = Field(False, title='是否删除')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(description='更新时间')
