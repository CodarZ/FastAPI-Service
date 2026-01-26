from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from backend.common.model import DataClassBase, id_key
from backend.utils.timezone import timezone


class SysOperationLog(DataClassBase):
    """操作日志表"""

    @declared_attr.directive
    def __tablename__(cls):
        return 'sys_operation_log'

    id: Mapped[id_key] = mapped_column(init=False)
    username: Mapped[str | None] = mapped_column(String(20), comment='操作用户')

    module: Mapped[str] = mapped_column(String(255), comment='操作模块')
    path: Mapped[str] = mapped_column(Text(), comment='请求路径')
    trace_id: Mapped[str] = mapped_column(String(length=128), comment='请求跟踪 ID')
    method: Mapped[str] = mapped_column(String(10), comment='请求方式')
    code: Mapped[str] = mapped_column(String(10), comment='操作状态码')
    args: Mapped[str | None] = mapped_column(JSON(), comment='请求参数')
    msg: Mapped[str | None] = mapped_column(Text(), comment='提示消息')
    cost_time: Mapped[float] = mapped_column(insert_default=0.0, comment='请求耗时（ms）')

    ip: Mapped[str] = mapped_column(String(50), comment='IP地址')
    country: Mapped[str | None] = mapped_column(String(50), comment='国家')
    region: Mapped[str | None] = mapped_column(String(50), comment='地区')
    city: Mapped[str | None] = mapped_column(String(50), comment='城市')

    user_agent: Mapped[str] = mapped_column(String(255), comment='请求头')
    os: Mapped[str | None] = mapped_column(String(50), comment='操作系统')
    browser: Mapped[str | None] = mapped_column(String(50), comment='浏览器')
    device: Mapped[str | None] = mapped_column(String(50), comment='设备')

    status: Mapped[int] = mapped_column(comment='操作状态（0异常 1正常）')
    operated_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment='操作时间')

    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default_factory=timezone.now, comment='创建时间'
    )
