from sqlalchemy import BigInteger, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enum import StatusEnum
from backend.common.model import Base, UserMixin, id_key


class SysDept(Base, UserMixin):
    """后台系统 - 部门信息表.

    组织架构的核心表，采用树形结构管理企业部门层级关系。
    与 RBAC 数据权限结合，实现部门维度的数据隔离。

    树形路径设计：
        - `parent_id` 存储直接上级部门 ID，顶级部门为 0
        - `tree` 存储完整路径（如 0,1,5）
        - 查询下级部门时可通过 `LIKE '0,1,5,%'` 高效获取
        - 避免递归查询，提升性能

    关联：
        - 角色-部门关联：通过 `sys_role_dept` 表（`dept_id` 关联本表 `id`）
        - 用户关联：    通过 `sys_admin` 表的 `dept_id` 字段关联本表 `id`
        - 树形结构：    通过 `parent_id` 字段关联本表 `id`
    """

    id: Mapped[id_key] = mapped_column(init=False)

    name: Mapped[str] = mapped_column(String(64), comment='部门名称')
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment='部门编码（唯一）')

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        index=True,
        comment='父部门 ID（0 表示顶级部门，关联 sys_dept.id）',
    )
    tree: Mapped[str | None] = mapped_column(
        String(255),
        default=None,
        index=True,
        comment='树形路径（从根到当前节点的路径）',
    )

    leader: Mapped[str | None] = mapped_column(String(64), default=None, comment='负责人姓名')
    phone: Mapped[str | None] = mapped_column(String(20), default=None, comment='联系电话')
    email: Mapped[str | None] = mapped_column(String(100), default=None, comment='邮箱')
    address: Mapped[str | None] = mapped_column(String(255), default=None, comment='联系地址')

    sort: Mapped[int] = mapped_column(SmallInteger, default=0, comment='排序权重（越小越靠前）')
    status: Mapped[int] = mapped_column(SmallInteger, default=StatusEnum.ENABLE, index=True, comment='状态（StatusEnum')
    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment='备注')
