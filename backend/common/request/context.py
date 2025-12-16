from typing import TYPE_CHECKING, Any

from starlette_context import context
from starlette_context.ctx import _Context

if TYPE_CHECKING:
    from datetime import datetime


class TypedContext(_Context):
    """上下文管理扩展"""

    # 性能
    perf_time: float  # 请求进入时的高精度时间（用于计算耗时）
    start_time: datetime  # 请求进入的真实时间

    # IP / 地理位置
    ip: str
    country: str | None
    region: str | None
    city: str | None

    # UA 相关
    user_agent: str
    os: str | None
    os_version: str | None
    browser: str | None
    browser_version: str | None
    device: str | None
    device_model: str | None

    # 权限
    permission: str | None

    def __getattr__(self, name: str) -> Any:
        return context.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        context[name] = value

    def __delattr__(self, name: str) -> None:
        context.pop(name, None)


ctx = TypedContext()
