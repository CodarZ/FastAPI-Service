from typing import TYPE_CHECKING, Any

from starlette_context import context

if TYPE_CHECKING:
    from datetime import datetime


class TypedContext:
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
    browser: str | None
    device: str | None

    # 权限
    permission: str | None

    def __getattr__(self, name: str) -> Any:
        try:
            return context[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def __setattr__(self, name: str, value: Any) -> None:
        context[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del context[name]
        except KeyError as error:
            raise AttributeError(name) from error


ctx = TypedContext()
