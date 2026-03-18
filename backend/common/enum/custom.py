from backend.common.enum.base import IntEnum, StrEnum


class StatusEnum(IntEnum):
    """状态类型.

    + `DISABLE`: 0 - 停用/禁用
    + `ENABLE`: 1 - 启用/正常
    """

    DISABLE = 0
    ENABLE = 1


class CipherEnum(IntEnum):
    """加密类型.

    + `PLAIN`:         0 - 不加密（明文存储）
    + `AES`:           1 - 使用 AES 对称加密（安全性高，性能损耗较大）
    + `MD5`:           2 - 使用 MD5 摘要加密（不可逆，适合简单脱敏）
    + `ITS`:           3 - 使用 ItsDangerous 加密（常用于签名和加密，适合 Web 场景）
    """

    PLAIN = 0
    AES = 1
    MD5 = 2
    ITS = 3


class MenuEnum(IntEnum):
    """菜单类型.

    + `DIRECTORY`:  0 - 目录/文件夹，用于组织和分组菜单项
    + `MENU`:       1 - 菜单页面，可点击跳转的功能页面
    + `BUTTON`:     2 - 按钮，页面内的操作按钮（如新增、删除等）
    + `EMBEDD`:     3 - 嵌入式组件，内嵌在页面中的功能模块
    + `LINK`:       4 - 外部链接，跳转到外部网站或资源
    """

    DIRECTORY = 0
    MENU = 1
    BUTTON = 2
    EMBEDD = 3
    LINK = 4


class RBACLogical(StrEnum):
    """RBAC 逻辑操作符.

    + `AND`: 用户必须拥有所有指定权限
    + `OR`: 用户拥有任意一个指定权限即可
    + `NOT`: 用户不能拥有指定权限（黑名单场景）
    """

    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'


class DataRuleExpressionEnum(IntEnum):
    """数据权限规则表达式.

    + `EQ`: 等于
    + `NE`: 不等于
    + `GT`: 大于
    + `GE`: 大于等于
    + `LT`: 小于
    + `LE`: 小于等于
    + `IN_`: 包含于（在列表中）
    + `NOT_IN`: 不包含于（不在列表中）
    """

    EQ = 0  # ==
    NE = 1  # !=
    GT = 2  # >
    GE = 3  # >=
    LT = 4  # <
    LE = 5  # <=
    IN_ = 6  # in
    NOT_IN = 7  # not in


class BuildTreeEnum(StrEnum):
    """构建树形结构类型.

    + `TRAVERSAL`: 遍历
    + `RECURSIVE`: 递归.
    """

    TRAVERSAL = 'traversal'
    RECURSIVE = 'recursive'
