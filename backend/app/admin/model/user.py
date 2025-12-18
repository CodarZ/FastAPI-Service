from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from backend.common.model import Base, id_key

if TYPE_CHECKING:
    from backend.app.admin.model.dept import SysDept
    from backend.app.admin.model.role import SysRole


class SysUser(Base):
    """用户信息表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_user'

    id: Mapped[id_key] = mapped_column(init=False)

    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment='用户名')
    password: Mapped[str | None] = mapped_column(String(255), comment='密码')
    salt: Mapped[bytes | None] = mapped_column(LargeBinary(255), comment='加密盐')

    nickname: Mapped[str] = mapped_column(String(20), comment='昵称')
    realname: Mapped[str | None] = mapped_column(String(50), comment=' 真实姓名')
    email: Mapped[str | None] = mapped_column(String(50), index=True, comment='邮箱')
    phone: Mapped[str | None] = mapped_column(String(11), unique=True, index=True, comment='手机号')
    avatar: Mapped[str | None] = mapped_column(String(500), comment='头像')
    gender: Mapped[int | None] = mapped_column(Integer, comment='性别(0女 1男 3其他)')
    birth_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment='出生日期')

    dept_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey('sys_dept.id', ondelete='SET NULL'), index=True, comment='所属部门 ID'
    )

    user_type: Mapped[str] = mapped_column(String(3), server_default='00', comment='用户类型')
    status: Mapped[int] = mapped_column(Integer, index=True, server_default='1', comment='账号状态(0停用 1正常)')
    is_multi_login: Mapped[bool] = mapped_column(Boolean, server_default='false', comment='是否允许多端登录')
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default='false', comment='是否是超级管理员')
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default='false', comment='是否是后台管理员')
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default='false', init=False, comment='是否实名认证')
    is_del: Mapped[bool] = mapped_column(Boolean, server_default='false', init=False, comment='是否删除')

    remark: Mapped[str | None] = mapped_column(String(500), comment='备注')
    last_login_ip: Mapped[str | None] = mapped_column(String(128), init=False, comment='最后登录IP')
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False, comment='最后登录时间'
    )

    # 关联关系
    dept: Mapped['SysDept | None'] = relationship('SysDept', lazy='selectin', passive_deletes=True)

    roles: Mapped[list['SysRole']] = relationship(
        'SysRole', secondary='sys_user_role', back_populates='users', lazy='selectin'
    )
