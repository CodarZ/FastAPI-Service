from sqlalchemy import BigInteger, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class SysRequestLog(Base):
    """后台系统 - 请求日志表.

    记录用户的所有请求行为，用于安全审计、问题排查和合规检查。

    请求日志通常：
    - 异步写入（不影响主业务性能）
    - 保留 6-12 个月后归档
    - 敏感操作（如删除、权限变更）永久保留

    日志级别设计：
        - 0=普通操作：查询、列表等读操作
        - 1=重要操作：新增、修改等写操作
        - 2=敏感操作：删除、权限变更、密码修改等
    """

    id: Mapped[id_key] = mapped_column(init=False)

    path: Mapped[str] = mapped_column(String(512), index=True, comment='请求地址')
    method: Mapped[str] = mapped_column(String(10), comment='请求方法')

    admin_id: Mapped[int | None] = mapped_column(
        BigInteger,
        index=True,
        default=None,
        comment='请求用户 ID（未登录时为 None，关联 sys_admin.id）',
    )
    username: Mapped[str | None] = mapped_column(String(64), default=None, comment='请求用户名（冗余存储，便于查询）')
    module: Mapped[str | None] = mapped_column(String(64), default=None, index=True, comment='业务模块')
    trace_id: Mapped[str | None] = mapped_column(String(64), default=None, index=True, comment='请求链路追踪 ID')
    ip: Mapped[str | None] = mapped_column(String(128), default=None, comment='客户端 IP 地址')
    user_agent: Mapped[str | None] = mapped_column(String(512), default=None, comment='浏览器 User-Agent')
    description: Mapped[str | None] = mapped_column(String(128), default=None, comment='描述')

    request_params: Mapped[str | None] = mapped_column(Text, default=None, comment='请求参数（敏感字段脱敏）')
    request_body: Mapped[str | None] = mapped_column(Text, default=None, comment='请求体（大文本存储）')
    status_code: Mapped[int | None] = mapped_column(SmallInteger, default=None, comment='HTTP 响应状态码')
    cost_time: Mapped[int | None] = mapped_column(BigInteger, default=None, comment='请求耗时（毫秒）')
    response_body: Mapped[str | None] = mapped_column(
        Text,
        default=None,
        comment='响应内容（仅记录失败响应，成功响应不记录）',
    )
    error_msg: Mapped[str | None] = mapped_column(Text, default=None, comment='错误信息（失败时记录）')

    level: Mapped[int] = mapped_column(SmallInteger, default=0, index=True, comment='日志级别：0=普通 1=重要 2=敏感')
    result_status: Mapped[int] = mapped_column(SmallInteger, default=1, index=True, comment='最终状态：0=失败 1=成功')

    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment='备注')
