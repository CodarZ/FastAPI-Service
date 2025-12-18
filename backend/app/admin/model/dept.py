from typing import List

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.common.model import Base, id_key


class SysDept(Base):
    """菜单信息表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_dept'

    id: Mapped[id_key] = mapped_column(init=False)
    title: Mapped[str] = mapped_column(String(200), comment='部门名称')

    leader: Mapped[str | None] = mapped_column(String(20), comment='负责人')
    phone: Mapped[str | None] = mapped_column(String(11), comment='联系电话')
    email: Mapped[str | None] = mapped_column(String(100), comment='邮箱')
    status: Mapped[int] = mapped_column(Integer, server_default='1', comment='状态（0停用 1正常）')

    sort: Mapped[int] = mapped_column(Integer, comment='显示顺序')

    # 🔑 父级菜单(自引用外键 + ondelete='CASCADE')
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey('sys_dept.id', ondelete='CASCADE'),
        index=True,
        comment='父菜单 ID',
    )

    # 父菜单对象
    parent: Mapped['SysDept | None'] = relationship(
        'SysDept',
        remote_side='SysDept.id',
        back_populates='children',
        lazy='selectin',
        passive_deletes=True,  # 交给数据库级联删除
    )

    # 子菜单集合
    children: Mapped[List['SysDept']] = relationship('SysDept', back_populates='parent', lazy='selectin')
