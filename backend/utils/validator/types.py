"""
自定义 Pydantic 类型

使用 Annotated 类型和验证器创建可复用的验证类型。
这些类型可以直接在 Schema 中使用，无需重复编写验证器。
"""

from typing import Annotated

from pydantic import AfterValidator, Field

import backend.utils.validator.validators as validators

# ==================== 用户相关类型 ====================
MobileStr = Annotated[str, AfterValidator(validators.validate_mobile), Field(min_length=11, max_length=11)]
"""中国大陆手机号（11位）"""

UsernameStr = Annotated[
    str,
    AfterValidator(validators.validate_username),
    Field(min_length=4, max_length=20, description='用户名'),
]
"""用户名（4-20位，字母、数字、下划线、中划线）"""

PasswordStr = Annotated[
    str,
    AfterValidator(validators.validate_password),
    Field(min_length=8, max_length=128, description='密码'),
]
"""密码（至少8位，包含字母和数字）"""

# ==================== 权限相关类型 ====================
PermissionStr = Annotated[
    str,
    AfterValidator(validators.validate_permission),
    Field(max_length=128, description='权限标识'),
]
"""权限标识（module:resource:action 格式）"""

RoleCodeStr = Annotated[
    str,
    AfterValidator(validators.validate_role_code),
    Field(min_length=1, max_length=100, description='角色编码'),
]
"""角色编码（字母开头，可包含字母、数字、下划线、冒号）"""

# ==================== 通用类型 ====================
CodeStr = Annotated[
    str,
    AfterValidator(validators.validate_code),
    Field(min_length=1, max_length=50, description='编码'),
]
"""通用编码（字母开头，可包含字母、数字、下划线）"""

StatusInt = Annotated[int, AfterValidator(validators.validate_status), Field(ge=0, le=1, description='状态')]
"""状态值（0停用 1正常）"""

SortInt = Annotated[int, AfterValidator(validators.validate_sort), Field(ge=0, description='排序')]
"""排序值（非负整数）"""

IdsListInt = Annotated[list[int], AfterValidator(validators.validate_ids_list), Field(description='ID列表')]
"""ID 列表（自动去重并过滤无效值）"""

# ==================== 常用范围 ====================
PositiveInt = Annotated[int, Field(gt=0, description='正整数')]
"""正整数（>0）"""

NonNegativeInt = Annotated[int, Field(ge=0, description='非负整数')]
"""非负整数（>=0）"""

PositiveFloat = Annotated[float, Field(gt=0.0, description='正浮点数')]
"""正浮点数（>0）"""

NonNegativeFloat = Annotated[float, Field(ge=0.0, description='非负浮点数')]
"""非负浮点数（>=0）"""
