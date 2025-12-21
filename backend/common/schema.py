from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.utils.timezone import timezone


class SchemaBase(BaseModel):
    """基础模型配置"""

    model_config = ConfigDict(
        use_enum_values=True,
        extra='forbid',
        str_strip_whitespace=True,
        json_encoders={
            datetime: lambda x: timezone.to_str(timezone.to_timezone(x)),
        },
    )
