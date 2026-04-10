from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enum import StatusEnum
from backend.common.model import Base, UserMixin, id_key


class SysDataRule(Base, UserMixin):
    """后台系统 - 数据权限规则表.

    实现细粒度数据权限控制的核心表，与角色关联后可动态生成查询条件。

    使用示例与字段说明：
        - `operator`（运算符）：决定【当前规则】与【其他规则】层叠时的连接逻辑（如 AND、OR）。
            最终组成：`Rule1 [operator] Rule2`
        - `expression`（表达式）：决定【当前这一个字段】与值之间的比较关系（如 等于、大于、IN）。
            最终组成：`column_name [expression] value`

    关联：
        - 角色-数据规则关联：通过 sys_role_data_rule 表（data_rule_id 关联本表 id）
    """

    id: Mapped[id_key] = mapped_column(init=False)

    name: Mapped[str] = mapped_column(String(64), comment='名称（如 "仅查看本部门订单"）')
    model_name: Mapped[str] = mapped_column(String(64), index=True, comment='模型名称, 对应 SQLAlchemy 模型类名如 User')
    column_name: Mapped[str] = mapped_column(String(64), comment='字段名称（模型中的列名，如 status）')
    operator: Mapped[str] = mapped_column(String(10), comment='运算符（RBACLogicalEnum）')
    expression: Mapped[str] = mapped_column(String(20), comment='表达式（DataRuleExpressionEnum）')
    code: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        default=None,
        index=True,
        comment='规则编码（唯一）',
    )
    value: Mapped[str | None] = mapped_column(
        String(255),
        default=None,
        comment='规则值（支持变量占位符，如 ${dept_ids}）',
    )

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=StatusEnum.ENABLE,
        index=True,
        comment='状态（StatusEnum）',
    )

    remark: Mapped[str | None] = mapped_column(
        String(500),
        default=None,
        comment='备注',
    )
