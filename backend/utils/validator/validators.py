"""
Pydantic 验证器函数

提供项目特定的字段验证器, 配合 Pydantic 的 field_validator 使用。

注意：SchemaBase 已配置 str_strip_whitespace=True, Pydantic 会自动去除字符串两端空白, 验证器中无需重复处理。
"""

import re

import backend.utils.validator.regex as patterns


# ==================== 用户相关验证器 ====================
def validate_mobile(value: str | None) -> str | None:
    """验证中国大陆手机号（11位）"""
    if not value:
        return None

    # 移除可能的国际区号
    if value.startswith('+86'):
        value = value[3:]
    elif value.startswith('86'):
        value = value[2:]

    # 移除可能的空格和横线（手机号特殊处理, 用户可能输入带分隔符的格式）
    value = value.replace(' ', '').replace('-', '')

    # 格式检查
    if not re.match(patterns.MOBILE_PATTERN, value):
        raise ValueError('手机号格式不正确, 应为11位数字且以1开头')

    return value


def validate_username(value: str) -> str:
    """验证用户名格式：4-20位, 字母、数字、下划线、中划线"""
    if not value:
        raise ValueError('用户名不能为空')

    if not re.match(patterns.USERNAME_PATTERN, value):
        raise ValueError('用户名格式不正确, 应为4-20位字母、数字、下划线或中划线')

    return value


def validate_password(value: str) -> str:
    """验证密码强度：至少8位, 包含字母和数字"""
    if not value:
        raise ValueError('密码不能为空')

    if len(value) < 8:
        raise ValueError('密码长度不能少于8位')

    if not any(c.isalpha() for c in value):
        raise ValueError('密码必须包含字母')

    if not any(c.isdigit() for c in value):
        raise ValueError('密码必须包含数字')

    return value


def validate_password_strong(value: str) -> str:
    """验证强密码：至少8位, 包含大小写字母和数字"""
    if not value:
        raise ValueError('密码不能为空')

    if len(value) < 8:
        raise ValueError('密码长度不能少于8位')

    if not any(c.islower() for c in value):
        raise ValueError('密码必须包含小写字母')

    if not any(c.isupper() for c in value):
        raise ValueError('密码必须包含大写字母')

    if not any(c.isdigit() for c in value):
        raise ValueError('密码必须包含数字')

    return value


# ==================== 权限相关验证器 ====================
def validate_permission(value: str | None) -> str | None:
    """验证权限标识格式：module:resource:action"""
    if not value:
        return None

    if not re.match(patterns.PERMISSION_PATTERN, value):
        raise ValueError('权限标识格式不正确, 应为 module:resource:action')

    return value


def validate_role_code(value: str) -> str:
    """验证角色编码格式：字母开头, 可包含字母、数字、下划线、冒号"""
    if not value:
        raise ValueError('角色编码不能为空')

    if not re.match(patterns.ROLE_CODE_PATTERN, value):
        raise ValueError('角色编码格式不正确, 应以字母开头, 可包含字母、数字、下划线、冒号')

    return value


# ==================== 通用验证器 ====================
def validate_code(value: str) -> str:
    """验证编码/标识符格式：字母开头, 可包含字母、数字、下划线"""
    if not value:
        raise ValueError('编码不能为空')

    if not re.match(patterns.CODE_PATTERN, value):
        raise ValueError('编码格式不正确, 应以字母开头, 可包含字母、数字、下划线')

    return value


def validate_sort(value: int) -> int:
    """验证排序值：非负整数"""
    if value < 0:
        raise ValueError('排序值不能为负数')
    return value


def validate_status(value: int) -> int:
    """验证状态值：0 或 1"""
    if value not in (0, 1):
        raise ValueError('状态值只能是 0(停用) 或 1(正常)')
    return value


def validate_ids_list(value: list[int]) -> list[int]:
    """验证 ID 列表：去重并过滤无效值"""
    if not value:
        return []

    # 去重并过滤非正整数
    return list({v for v in value if isinstance(v, int) and v > 0})
