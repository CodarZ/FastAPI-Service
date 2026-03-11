from typing import TYPE_CHECKING, TypedDict, cast

from starlette_context import context

if TYPE_CHECKING:
    from datetime import datetime

    from backend.common.dataclasses import UserAgentInfo


class RequestContextData(TypedDict):
    """自定义请求上下文数据结构."""

    # --------  性能  --------
    perf_time: float  # 请求进入时的高精度时间戳，time.perf_counter()（用于计算耗时）
    start_time: datetime  # 请求进入的真实时间（业务时间），datetime.now()

    # --------  IP / 地理位置  --------
    ip: str  # 客户端真实 IP（已处理反代）
    country: str | None
    region: str | None
    city: str | None

    ua: UserAgentInfo  # 解析后的 User-Agent 信息

    # --------  异常信息  --------
    __request_http_exception__: dict | None  # HTTP 异常
    __request_custom_exception__: dict | None  # 自定义异常（业务）
    __request_assertion_error__: dict | None  # 断言异常
    __request_validation_exception__: dict | None  # 请求/数据验证异常
    __request_unknown_exception__: dict | None  # 未知异常


ctx = cast('RequestContextData', context)
