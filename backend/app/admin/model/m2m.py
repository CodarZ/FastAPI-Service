from sqlalchemy import BigInteger, Column, ForeignKey, Table, UniqueConstraint

from backend.common.model import MappedBase

sys_user_role = Table(
    'sys_user_role',
    MappedBase.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True, comment='主键 ID'),
    Column(
        'user_id',
        BigInteger,
        ForeignKey('sys_user.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
        comment='用户 ID',
    ),
    Column(
        'role_id',
        BigInteger,
        ForeignKey('sys_role.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
        comment='角色 ID',
    ),
    # 唯一约束（避免重复绑定 role）
    UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
)


sys_role_menu = Table(
    'sys_role_menu',
    MappedBase.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True, comment='主键 ID'),
    Column(
        'role_id',
        BigInteger,
        ForeignKey('sys_role.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
        comment='角色 ID',
    ),
    Column(
        'menu_id',
        BigInteger,
        ForeignKey('sys_menu.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
        comment='菜单 ID',
    ),
    # 唯一约束（避免重复绑定 menu）
    UniqueConstraint('role_id', 'menu_id', name='uq_role_menu'),
)
