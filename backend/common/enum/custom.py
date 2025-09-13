#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from backend.common.enum.base import IntEnum, StrEnum


class LoginLogStatusEnum(IntEnum):
    """登陆日志状态"""

    FAIL = 0
    SUCCESS = 1


class StatusEnum(IntEnum):
    """状态类型枚举"""

    DISABLE = 0
    ENABLE = 1


class OperationLogCipherEnum(IntEnum):
    """
    操作日志加密类型枚举

    AES:          0 - 使用 AES 对称加密（安全性高，性能损耗较大）
    MD5:          1 - 使用 MD5 摘要加密（不可逆，适合简单脱敏）
    ITS_DANGEROUS: 2 - 使用 ItsDangerous 加密（常用于签名和加密，适合 Web 场景）
    PLAN:         3 - 不加密（明文存储）
    """

    AES = 0
    MD5 = 1
    ITS_DANGEROUS = 2
    PLAN = 3


class MenuEnum(IntEnum):
    """
    菜单类型枚举

    + DIRECTORY:  0 - 目录/文件夹，用于组织和分组菜单项
    + MENU:       1 - 菜单页面，可点击跳转的功能页面
    + BUTTON:     2 - 按钮，页面内的操作按钮（如新增、删除等）
    + EMBEDDED:   3 - 嵌入式组件，内嵌在页面中的功能模块
    + LINK:       4 - 外部链接，跳转到外部网站或资源
    """

    DIRECTORY = 0
    MENU = 1
    BUTTON = 2
    EMBEDDED = 3
    LINK = 4


class RoleDataRuleOperatorEnum(IntEnum):
    """数据权限规则运算符"""

    AND = 0
    OR = 1


class UserPermissionEnum(StrEnum):
    """
    用户权限类型

    + SUPER_USER:    超级管理员 - 拥有系统最高权限，可管理所有功能和用户
    + STAFF:        员工/管理员 - 具有后台管理权限，可执行管理操作
    + USER:         用户 - 用户
    + MULTI_LOGIN:  多设备登录权限 - 允许用户在多个设备上同时登录
    """

    SUPER_USER = 'superuser'
    STAFF = 'staff'
    USER = 'user'
    MULTI_LOGIN = 'multi_login'


class RoleDataRuleExpressionEnum(IntEnum):
    """数据权限规则表达式"""

    EQ = 0  # ==
    NE = 1  # !=
    GT = 2  # >
    GE = 3  # >=
    LT = 4  # <
    LE = 5  # <=
    IN_ = 6  # in
    NOT_IN = 7  # not in


class MethodEnum(StrEnum):
    """请求方法"""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'


class BuildTreeEnum(StrEnum):
    """
    构建树形结构类型枚举
    + TRAVERSAL: 遍历
    + RECURSIVE: 递归
    """

    TRAVERSAL = 'traversal'
    RECURSIVE = 'recursive'


class FileTypeEnum(StrEnum):
    """文件类型"""

    IMAGE = 'image'
    VIDEO = 'video'
