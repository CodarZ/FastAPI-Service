#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pydantic import Field

from backend.common.schema import SchemaBase


class UserRegisterParams(SchemaBase):
    """注册用户"""

    username: str = Field(description='用户名')
    password: str = Field(description='密码')
