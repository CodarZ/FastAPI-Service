from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from backend.common.model import DataClassBase, id_key
from backend.utils.timezone import timezone


class SysLoginLog(DataClassBase):
    """登录日志表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_login_log'

    id: Mapped[id_key] = mapped_column(init=False)

    username: Mapped[str | None] = mapped_column(String(20), comment='用户名')
    user_id: Mapped[int | None] = mapped_column(BigInteger, comment='用户 ID')
    status: Mapped[int] = mapped_column(comment='登录状态（0异常 1正常）')

    ip: Mapped[str | None] = mapped_column(String(50), comment='IP地址')
    country: Mapped[str | None] = mapped_column(String(50), comment='国家')
    region: Mapped[str | None] = mapped_column(String(50), comment='地区')
    city: Mapped[str | None] = mapped_column(String(50), comment='城市')

    user_agent: Mapped[str | None] = mapped_column(String(255), comment='请求头')
    os: Mapped[str | None] = mapped_column(String(50), comment='操作系统')
    browser: Mapped[str | None] = mapped_column(String(50), comment='浏览器')
    device: Mapped[str | None] = mapped_column(String(50), comment='设备')

    msg: Mapped[str | None] = mapped_column(Text(), comment='提示消息')
    login_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment='登录时间')

    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, comment='创建时间'
    )
