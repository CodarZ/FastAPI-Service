from sqlalchemy import Boolean, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enum import DataScopeEnum, StatusEnum
from backend.common.model import Base, UserMixin, id_key


class SysRole(Base, UserMixin):
    """后台系统 - 角色信息表.

    RBAC 权限模型的核心枢纽，连接用户与权限。
    角色是权限的集合，用户通过角色获得相应的菜单权限和数据权限。

    关联说明（无外键）：
        - 用户-角色关联：通过 sys_admin_role 表（role_id 关联本表 id）
        - 角色-菜单关联：通过 sys_role_menu 表（role_id 关联本表 id）
        - 角色-部门关联：通过 sys_role_dept 表（role_id 关联本表 id）
    """

    id: Mapped[id_key] = mapped_column(init=False)

    name: Mapped[str] = mapped_column(String(50), unique=True, comment='角色名称')
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment='角色编码(唯一)')

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=StatusEnum.ENABLE,
        index=True,
        comment='状态（StatusEnum）',
    )

    is_system: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否系统内置角色（True 时不可删除）')

    data_scope: Mapped[int] = mapped_column(
        SmallInteger,
        default=DataScopeEnum.DEPT,
        comment='数据权限范围（DataScopeEnum）',
    )

    sort: Mapped[int] = mapped_column(Integer, default=0, comment='排序权重（越小越靠前）')
    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment='备注')
