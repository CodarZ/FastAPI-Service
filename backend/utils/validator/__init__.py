"""
验证器模块

使用方式：

1. 直接使用验证器函数（最灵活）：
    from pydantic import EmailStr
    from backend.utils.validator import validate_mobile

    class UserCreate(SchemaBase):
        mobile: str = Field(..., description='手机号')
        email: EmailStr = Field(..., description='邮箱')  # 使用 Pydantic 内置

        @field_validator('mobile')
        @classmethod
        def check_mobile(cls, v: str) -> str:
            return validate_mobile(v)

2.  简化的方式一：
    from backend.utils.validator import validate_mobile

    class UserCreate(SchemaBase):
        mobile: str = Field(..., description='手机号')

        _check_mobile = field_validator('mobile', mode='after')(validate_mobile)

3. 使用 Annotated 类型（最简洁，推荐）：
    from backend.utils.validator import MobileStr

    class UserCreate(SchemaBase):
        mobile: MobileStr = Field(..., description='手机号')

2. 使用 Mixin 类（批量字段验证）：
    from backend.utils.validator import MobileValidatorMixin

    class UserCreate(SchemaBase, MobileValidatorMixin):
        phone: str = Field(..., description='手机号')
"""

from backend.utils.validator.minixs import *
from backend.utils.validator.regex import *
from backend.utils.validator.types import *
from backend.utils.validator.validators import *
