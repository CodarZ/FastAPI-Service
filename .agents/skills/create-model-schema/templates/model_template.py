from sqlalchemy import BigInteger, Boolean, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enum import StatusEnum
from backend.common.model import Base, id_key, uuid_key


class DomainEntity(Base):
    """DOMAIN ENTITY 模板, 在此详细说明此实体的职责和字段。.

    关联说明 (逻辑关联, 严禁外键物理约束):
    - example_id: 关联 其他实体.id
    """

    id: Mapped[id_key] = mapped_column()
    uuid: Mapped[uuid_key] = mapped_column()

    # 1. 基础字段
    name: Mapped[str] = mapped_column(String(64), index=True, comment='实体名称')
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment='实体编码')

    # 2. 逻辑外键标识 (ZERO PHYSICAL FKs!)
    parent_id: Mapped[int] = mapped_column(
        BigInteger, default=0, index=True, comment='父节点 ID（关联本表 id，0 为顶级）'
    )

    # 3. 相关状态与开关
    status: Mapped[int] = mapped_column(
        SmallInteger, default=StatusEnum.ENABLE, index=True, comment='状态（StatusEnum）'
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否系统内置')

    # 4. 额外文本与描述
    sort: Mapped[int] = mapped_column(SmallInteger, default=0, comment='排序权重')
    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment='备注信息')
