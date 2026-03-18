from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo

from dateutil import parser

from backend.core.config import settings

_DateTime = int | float | datetime


class TimeZone:
    """项目时区工具类."""

    def __init__(self) -> None:
        self.tz = ZoneInfo(settings.DATETIME_TIMEZONE)

    def _convert(self, dt: _DateTime, tz: tzinfo, *, local: bool = False) -> datetime:
        """转换 datetime 并指定时区.

        Args:
            dt: 待转换的时间值（时间戳 / datetime）
            tz: 目标时区
            local: 为 True 时，naive datetime 视为本地时区（DATETIME_TIMEZONE）而非 UTC
        """
        if isinstance(dt, (int, float)):
            return datetime.fromtimestamp(dt, tz=tz)
        if dt.tzinfo is None:
            # naive datetime 时区推定：按需视为本地时区或 UTC
            assumed_tz = self.tz if local else UTC
            return dt.replace(tzinfo=assumed_tz).astimezone(tz)
        return dt.astimezone(tz)

    def now(self) -> datetime:
        """获取当前时间."""
        return datetime.now(tz=self.tz)

    def to_datetime(self, dt: _DateTime | None) -> datetime | None:
        """转换为本地时区（naive 视为 UTC）."""
        if dt is None:
            return None
        return self._convert(dt, self.tz)

    def f_local_datetime(self, dt: _DateTime | None) -> datetime | None:
        """API 输入层专用：将 datetime 统一转为本地时区的 aware datetime.

        处理策略：
            - naive datetime  → 视为本地时区（DATETIME_TIMEZONE），补齐 tzinfo
            - aware datetime  → 自动从原时区转换到本地时区（兼容任意时区输入）
            - int / float     → 按时间戳转换到本地时区
            - None            → 原样返回 None
        """
        if dt is None:
            return None
        return self._convert(dt, self.tz, local=True)

    def to_utc(self, dt: _DateTime | None) -> datetime | None:
        """转换为 UTC 时区."""
        if dt is None:
            return None
        return self._convert(dt, UTC)

    def to_str(self, dt: _DateTime | None, fmt: str = settings.DATETIME_FORMAT) -> str:
        dt = self.to_datetime(dt)
        return dt.strftime(fmt) if dt else ''

    def to_timestamp(self, dt: _DateTime | None) -> float:
        """转换为时间戳（秒）."""
        dt = self.to_datetime(dt)
        return dt.timestamp() if dt else 0.0

    def format_str(self, dt_str: str, fmt: str = settings.DATETIME_FORMAT) -> datetime:
        """将已知确定的 fmt 格式的字符串转换为 datetime 对象."""
        return datetime.strptime(dt_str, fmt).replace(tzinfo=self.tz)

    def parse_str(self, dt_str: str) -> datetime:
        """解析任意格式的日期字符串为 datetime 对象.

        不建议使用，内置了大量的正则表达式，性能较差
        """
        return parser.parse(dt_str).astimezone(self.tz)


timezone = TimeZone()
