from backend.common.enum.base import IntEnum, StrEnum


class LoginLogStatusEnum(StrEnum):
    """登录状态"""

    FAIL = 'FAIL'
    SUCCESS = 'SUCCESS'


class StatusEnum(IntEnum):
    """状态类型枚举"""

    DISABLE = 0
    ENABLE = 1


class CipherEnum(IntEnum):
    """
    加密类型枚举

    AES:           0 - 使用 AES 对称加密（安全性高，性能损耗较大）
    MD5:           1 - 使用 MD5 摘要加密（不可逆，适合简单脱敏）
    ITS_DANGEROUS: 2 - 使用 ItsDangerous 加密（常用于签名和加密，适合 Web 场景）
    PLAIN:         3 - 不加密（明文存储）
    """

    AES = 0
    MD5 = 1
    ITS_DANGEROUS = 2
    PLAIN = 3


class MenuEnum(IntEnum):
    """
    菜单类型枚举

    + DIRECTORY:  0 - 目录/文件夹，用于组织和分组菜单项
    + MENU:       1 - 菜单页面，可点击跳转的功能页面
    + BUTTON:     2 - 按钮，页面内的操作按钮（如新增、删除等）
    + LINK:       3 - 外部链接，跳转到外部网站或资源
    + EMBEDDED:   4 - 嵌入式组件，内嵌在页面中的功能模块
    """

    DIRECTORY = 0
    MENU = 1
    BUTTON = 2
    LINK = 3
    EMBEDDED = 4


class UserPermissionEnum(StrEnum):
    """
    用户权限类型

    + SUPER_USER:    超级管理员  - 拥有系统最高权限，可管理所有功能和用户
    + ADMIN:         管理员/员工 - 具有后台管理权限，可执行管理操作
    + USER:          用户       - C 端的用户
    + MULTI_LOGIN:   多设备登录  - 允许用户在多个设备上同时登录
    """

    SUPER_USER = 'superuser'
    ADMIN = 'admin'
    USER = 'user'
    MULTI_LOGIN = 'multi_login'


class DataRuleOperatorEnum(IntEnum):
    """数据权限规则运算符"""

    AND = 0
    OR = 1


class DataRuleExpressionEnum(IntEnum):
    """数据权限规则表达式"""

    EQ = 0  # ==
    NE = 1  # !=
    GT = 2  # >
    GE = 3  # >=
    LT = 4  # <
    LE = 5  # <=
    IN_ = 6  # in
    NOT_IN = 7  # not in


class RBACLogical(StrEnum):
    """RBAC 逻辑操作符"""

    AND = 'AND'  # 用户必须拥有所有指定权限
    OR = 'OR'  # 用户拥有任意一个指定权限即可
    NOT = 'NOT'  # 用户不能拥有指定权限（黑名单场景）


class MethodEnum(StrEnum):
    """请求方法"""

    CONNECT = 'CONNECT'
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    TRACE = 'TRACE'


class BuildTreeEnum(StrEnum):
    """
    构建树形结构类型枚举
    + TRAVERSAL: 遍历
    + RECURSIVE: 递归
    """

    TRAVERSAL = 'traversal'
    RECURSIVE = 'recursive'
