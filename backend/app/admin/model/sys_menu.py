from sqlalchemy import BigInteger, Boolean, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enum import MenuEnum, StatusEnum
from backend.common.model import Base, UserMixin, id_key


class SysMenu(Base, UserMixin):
    """后台系统 - 菜单/权限表.

    RBAC 权限控制的核心表，采用树形结构组织菜单和按钮权限。
    支持目录、菜单、按钮、嵌入式组件、外部链接五种类型。

    关联：
        - 角色-菜单关联：通过 sys_role_menu 表（menu_id 关联本表 id）
        - 树形结构：    通过 parent_id 字段关联本表 id
    """

    id: Mapped[id_key] = mapped_column(init=False)

    name: Mapped[str] = mapped_column(String(64), comment='菜单名称')
    path: Mapped[str] = mapped_column(String(255), unique=True, comment='访问地址路径')

    type: Mapped[int] = mapped_column(
        SmallInteger,
        default=MenuEnum.DIRECTORY,
        index=True,
        comment='菜单类型（MenuEnum）',
    )

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        index=True,
        comment='父菜单 ID（0 表示顶级菜单，关联 sys_menu.id）',
    )
    tree: Mapped[str | None] = mapped_column(
        String(255),
        default=None,
        index=True,
        comment='树形路径（从根到当前节点的路径）',
    )
    component: Mapped[str | None] = mapped_column(String(255), default=None, comment='前端组件路径')
    redirect: Mapped[str | None] = mapped_column(String(255), default=None, comment='重定向路径')
    permission: Mapped[str | None] = mapped_column(String(128), default=None, index=True, comment='权限标识')
    icon: Mapped[str | None] = mapped_column(String(64), default=None, comment='菜单图标')

    visible: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否可见（隐藏后不在菜单中显示，但仍可访问）')
    is_cache: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否缓存页面（keep-alive）')
    is_external: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否外部链接')
    is_frame: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否内嵌 iframe（打开外部链接方式）')

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=StatusEnum.ENABLE,
        index=True,
        comment='状态（StatusEnum）',
    )

    sort: Mapped[int] = mapped_column(SmallInteger, default=0, comment='排序权重（越小越靠前）')
    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment='备注')
