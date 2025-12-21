"""正则表达式

注意, Pydantic 存在已有的类型, 如: EmailStr, HttpUrl, IPvAnyAddress 等。
"""

# ==================== 用户相关 ====================
# 中国大陆手机号：1开头的11位数字
MOBILE_PATTERN = r'^1[3-9]\d{9}$'

# 用户名：4-20位，字母、数字、下划线、中划线
USERNAME_PATTERN = r'^[a-zA-Z0-9_-]{4,20}$'

# 密码（中）：至少8位，包含字母和数字
PASSWORD_MEDIUM_PATTERN = r'^(?=.*[A-Za-z])(?=.*\d).{8,}$'

# 密码（强）：至少8位，包含大小写字母、数字
PASSWORD_STRONG_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

# ==================== 权限相关 ====================
# 权限标识：module:resource:action 格式
PERMISSION_PATTERN = r'^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9]*$'

# 角色编码：字母开头，可包含字母、数字、下划线、冒号
ROLE_CODE_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_:]*$'

# ==================== 通用格式 ====================
# 编码/标识符：字母开头，可包含字母、数字、下划线
CODE_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_]*$'

# 路径格式：以 / 开头的路径
PATH_PATTERN = r'^/[a-zA-Z0-9/_-]*$'
