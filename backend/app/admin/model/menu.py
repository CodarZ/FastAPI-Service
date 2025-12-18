from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.common.enum.custom import MenuEnum  # noqa: TCH001
from backend.common.model import Base, id_key

if TYPE_CHECKING:
    from backend.app.admin.model.role import SysRole


class SysMenu(Base):
    """菜单信息表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_menu'

    id: Mapped[id_key] = mapped_column(init=False)

    title: Mapped[str] = mapped_column(String(50), comment='菜单标题')
    type: Mapped[MenuEnum] = mapped_column(Integer, comment='菜单类型')
    path: Mapped[str | None] = mapped_column(String(200), comment='访问地址、外链地址')
    component: Mapped[str | None] = mapped_column(String(300), comment='组件的文件路径')
    permission: Mapped[str | None] = mapped_column(String(128), comment='权限标识')

    icon: Mapped[str | None] = mapped_column(String(50), comment='图标')
    redirect: Mapped[str | None] = mapped_column(String(200), comment='重定向访问地址')
    active_menu: Mapped[str | None] = mapped_column(String(200), comment='访问时，应该高亮的菜单')

    status: Mapped[int] = mapped_column(Integer, index=True, server_default='1', comment='状态(0停用 1正常)')
    hidden: Mapped[bool] = mapped_column(Boolean, server_default='false', comment='是否隐藏菜单')
    keep_alive: Mapped[bool] = mapped_column(Boolean, server_default='false', comment='是否缓存该页面')
    tab: Mapped[bool] = mapped_column(Boolean, server_default='true', comment='是否在标签页显示')
    breadcrumb: Mapped[bool] = mapped_column(Boolean, server_default='true', comment='是否在面包屑中显示')

    sort: Mapped[int] = mapped_column(comment='排序')
    remark: Mapped[str | None] = mapped_column(String(500), comment='备注')

    # 🔑 父级菜单(自引用外键 + ondelete='CASCADE')
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey('sys_menu.id', ondelete='CASCADE'),
        index=True,
        comment='父菜单 ID',
    )

    # 父菜单对象
    parent: Mapped['SysMenu | None'] = relationship(
        'SysMenu',
        remote_side='SysMenu.id',
        back_populates='children',
        lazy='selectin',
        passive_deletes=True,  # 交给数据库级联删除
    )

    # 子菜单集合
    children: Mapped[List['SysMenu']] = relationship('SysMenu', back_populates='parent', lazy='selectin')

    # 关联关系
    roles: Mapped[list['SysRole']] = relationship(
        'SysRole', secondary='sys_role_menu', back_populates='menus', lazy='selectin'
    )
