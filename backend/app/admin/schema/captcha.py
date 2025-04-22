#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import Field

from backend.common.schema import SchemaBase


class CaptchaSchema(SchemaBase):
    """验证码"""

    image: str = Field(..., description='验证码图片')
    image_type: str = Field(default='base64', description='图片类型，如 base64')
