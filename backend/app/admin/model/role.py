from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.common.model import Base, id_key

if TYPE_CHECKING:
    from backend.app.admin.model.dept import SysDept
    from backend.app.admin.model.menu import SysMenu
    from backend.app.admin.model.user import SysUser


class SysRole(Base):
    """角色表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_role'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, comment='名称')
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment='权限字符串')

    data_scope: Mapped[int] = mapped_column(
        Integer,
        server_default='0',
        comment='数据范围(0全部, 1本部门及子部门, 2本部门, 3仅本人, 4自定义部门)',
    )

    status: Mapped[int] = mapped_column(Integer, server_default='1', comment='状态（0停用 1正常）')
    remark: Mapped[str | None] = mapped_column(String(500), comment='备注')

    # 关联关系
    users: Mapped[list['SysUser']] = relationship(
        'SysUser', secondary='sys_user_role', back_populates='roles', lazy='selectin'
    )
    menus: Mapped[list['SysMenu']] = relationship(
        'SysMenu', secondary='sys_role_menu', back_populates='roles', lazy='selectin'
    )
    depts: Mapped[list['SysDept']] = relationship(
        'SysDept', secondary='sys_role_dept', back_populates='roles', lazy='selectin'
    )
