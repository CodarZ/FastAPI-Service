from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, id_key


class SysAdminRole(DataClassBase):
    """用户-角色关联表.

    关联关系：
        - admin_id -> sys_admin.id
        - role_id -> sys_role.id
    """

    __tablename__ = 'sys_user_role'  # type: ignore[override]
    __table_args__ = (UniqueConstraint('admin_id', 'role_id', name='uq_user_role'),)  # type: ignore[override]

    id: Mapped[id_key] = mapped_column(init=False)
    admin_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='用户 ID（关联 sys_admin.id）')
    role_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='角色 ID（关联 sys_role.id）')


class SysRoleMenu(DataClassBase):
    """角色-菜单关联表.

    关联关系：
        - role_id -> sys_role.id
        - menu_id -> sys_menu.id
    """

    __tablename__ = 'sys_role_menu'  # type: ignore[override]
    __table_args__ = (UniqueConstraint('role_id', 'menu_id', name='uq_role_menu'),)  # type: ignore[override]

    id: Mapped[id_key] = mapped_column(init=False)
    role_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='角色 ID（关联 sys_role.id）')
    menu_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='菜单 ID（关联 sys_menu.id）')


class SysRoleDept(DataClassBase):
    """角色-部门关联表（部门级数据权限）.

    关联关系：
        - role_id -> sys_role.id
        - dept_id -> sys_dept.id

    使用场景：
        当 sys_role.data_scope = DataScopeEnum.CUSTOM_DEPT 时，
        通过此表指定该角色可访问的部门列表。
    """

    __tablename__ = 'sys_role_dept'  # type: ignore[override]
    __table_args__ = (UniqueConstraint('role_id', 'dept_id', name='uq_role_dept'),)  # type: ignore[override]

    id: Mapped[id_key] = mapped_column(init=False)
    role_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='角色 ID（关联 sys_role.id）')
    dept_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='部门 ID（关联 sys_dept.id）')


class SysRoleDataRule(DataClassBase):
    """角色-数据规则关联表（细粒度字段级数据权限）.

    关联关系：
        - role_id -> sys_role.id
        - data_rule_id -> sys_data_rule.id

    使用场景：
        当 sys_role.data_scope = DataScopeEnum.CUSTOM_RULE 时，
        通过此表指定该角色应用的数据规则列表，支持更细粒度的字段级和值级权限控制。
    """

    __tablename__ = 'sys_role_data_rule'  # type: ignore[override]
    __table_args__ = (UniqueConstraint('role_id', 'data_rule_id', name='uq_role_data_rule'),)  # type: ignore[override]

    id: Mapped[id_key] = mapped_column(init=False)
    role_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='角色 ID（关联 sys_role.id）')
    data_rule_id: Mapped[int] = mapped_column(BigInteger, index=True, comment='数据规则 ID（关联 sys_data_rule.id）')
