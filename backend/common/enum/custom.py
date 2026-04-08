from backend.common.enum.base import IntEnum, StrEnum


class StatusEnum(IntEnum):
    """状态类型.

    + `DISABLE`: 0 - 停用/禁用
    + `ENABLE`: 1 - 启用/正常
    """

    DISABLE = 0
    ENABLE = 1


class AccountStatusEnum(IntEnum):
    """账号状态.

    + `DELETED`: 0 - 已删除（软删除标记，数据仍保留但不可用）
    + `ACTIVE`: 1 - 活跃/正常
    + `LOCKED`: 2 - 锁定（如: 多次登录失败后的临时锁定）
    + `DISABLED`: 3 - 禁用（需管理员解禁）
    """

    DELETED = 0
    ACTIVE = 1
    LOCKED = 2
    DISABLED = 3


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


class RBACLogicalEnum(StrEnum):
    """RBAC 逻辑操作符.

    + `AND`: 用户必须拥有所有指定权限
    + `OR`: 用户拥有任意一个指定权限即可
    """

    AND = 'and'
    OR = 'or'


class DataRuleExpressionEnum(StrEnum):
    """数据权限规则表达式.

    + `EQ`: 等于
    + `NE`: 不等于
    + `GT`: 大于
    + `GE`: 大于等于
    + `LT`: 小于
    + `LE`: 小于等于
    + `BETWEEN`: 在范围内
    + `IN_`: 包含于（在列表中）
    + `NOT_IN`: 不包含于（不在列表中）
    + `LIKE`: 模糊扫描
    + `NOT_LIKE`: 反向模糊扫描
    + `IS_NULL`: 为空
    + `IS_NOT_NULL`: 不为空
    """

    EQ = 'eq'
    NE = 'ne'
    GT = 'gt'
    GE = 'ge'
    LT = 'lt'
    LE = 'le'
    BETWEEN = 'between'
    IN_ = 'in'
    NOT_IN = 'not_in'
    LIKE = 'like'
    NOT_LIKE = 'not_like'
    IS_NULL = 'is_null'
    IS_NOT_NULL = 'is_not_null'


class BuildTreeEnum(StrEnum):
    """构建树形结构类型.

    + `TRAVERSAL`: 遍历
    + `RECURSIVE`: 递归.
    """

    TRAVERSAL = 'traversal'
    RECURSIVE = 'recursive'


class DataScopeEnum(IntEnum):
    """数据权限范围.

    + `ALL`: 0 - 全部数据：可查看所有部门的数据（一般是超级管理员）
    + `DEPT_AND_CHILD`: 1 - 本部门及下级数据：可查看本部门 + 所有下级部门的数据
    + `DEPT`: 2 - 本部门数据：只能查看自己所在部门的数据
    + `SELF`: 3 - 仅本人数据：只能查看自己创建/关联的数据
    + `CUSTOM_DEPT`: 4 - 自定义部门：通过 sys_role_dept 表指定可访问的部门
    + `CUSTOM_RULE`: 5 - 自定义规则：通过 sys_role_data_rule 表指定的细粒度数据权限
    """

    ALL = 0
    DEPT_AND_CHILD = 1
    DEPT = 2
    SELF = 3
    CUSTOM_DEPT = 4
    CUSTOM_RULE = 5
