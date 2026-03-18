from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    """所有业务 Schema 的基类.

    统一配置：
    - `use_enum_values`        - 自动将枚举转为其值
    - `extra='forbid'`         - 禁止传入的未定义的额外字段
    - `str_strip_whitespace`   - 自动去除字符串首尾空白
    """

    model_config = ConfigDict(use_enum_values=True, extra='forbid', str_strip_whitespace=True)
