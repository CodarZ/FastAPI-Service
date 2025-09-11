#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.utils.timezone import timezone


class SchemaBase(BaseModel):
    """基础模型配置"""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: lambda x: timezone.to_str(timezone.from_datetime(x))},
    )
