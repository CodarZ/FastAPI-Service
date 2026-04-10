from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enum import AccountStatusEnum
from backend.common.model import Base, id_key, uuid_key


class SysAdmin(Base):
    """后台系统 - 管理员用户信息表.

    用户创建流程：
    1. 输入创建
        - 用户名必填，且必须唯一
        - 密码必填
        - 其他字段（昵称、邮箱、手机号等）可选，但如果提供则必须满足唯一性和格式要求
    2. oauth 2.0 授权
        - 自动创建用户名

    `id` 和 `uuid` 字段为全局唯一标识，且在系统中具有特殊意义：
        - `id`：数据库主键，递增整数，主要用于内部关联和性能
        - `uuid`：全局唯一标识符，使用 UUID4 生成，主要用于外部接口暴露和安全考虑

    关联：
        - 用户-角色关联： 通过 `sys_admin_role` 表（`admin_id` 关联本表 `id`）
        - 部门关联：     通过 `dept_id` 字段关联 `sys_dept` 表
    """

    id: Mapped[id_key] = mapped_column()
    uuid: Mapped[uuid_key] = mapped_column()

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment='用户名')
    password: Mapped[str | None] = mapped_column(String(256), comment='密码')

    nickname: Mapped[str] = mapped_column(String(64), comment='昵称')
    realname: Mapped[str | None] = mapped_column(String(50), default=None, comment='真实姓名')
    email: Mapped[str | None] = mapped_column(String(100), default=None, unique=True, index=True, comment='邮箱')
    phone: Mapped[str | None] = mapped_column(String(30), default=None, unique=True, index=True, comment='手机号')
    avatar: Mapped[str | None] = mapped_column(String(500), default=None, comment='头像 URL')
    gender: Mapped[int | None] = mapped_column(SmallInteger, default=None, comment='性别：None=未设置 0=女 1=男 2=未知')
    birth_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, comment='出生日期')
    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment='备注')

    dept_id: Mapped[int | None] = mapped_column(
        BigInteger,
        default=None,
        index=True,
        comment='所属部门 ID（关联 sys_dept.id）',
    )

    is_super: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否超级管理员')
    is_multi_login: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否允许多端同时登录')
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=AccountStatusEnum.ACTIVE,
        index=True,
        comment='账号状态（AccountStatusEnum）',
    )

    last_login_ip: Mapped[str | None] = mapped_column(String(128), default=None, init=False, comment='最后登录 IP')
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        init=False,
        comment='最后登录时间',
    )
