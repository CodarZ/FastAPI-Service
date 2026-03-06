from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo

from dateutil import parser

from backend.core.config import settings

_DateTime = int | float | datetime


class TimeZone:
    """项目时区工具类."""

    def __init__(self) -> None:
        self.tz = ZoneInfo(settings.DATETIME_TIMEZONE)

    def _convert(self, dt: _DateTime, tz: tzinfo) -> datetime:
        """转换 datetime 并指定时区."""
        if isinstance(dt, (int, float)):
            return datetime.fromtimestamp(dt, tz=tz)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=tz)
        return dt.astimezone(tz)

    def now(self) -> datetime:
        """获取当前时间."""
        return datetime.now(tz=self.tz)

    def to_datetime(self, dt: _DateTime) -> datetime:
        """转换为 datetime 对象."""
        return self._convert(dt, self.tz)

    def to_utc(self, dt: _DateTime) -> datetime:
        """转换为 UTC 时区."""
        return self._convert(dt, UTC)

    def to_str(self, dt: _DateTime, fmt: str = settings.DATETIME_FORMAT) -> str:
        """转换为字符串（指定格式）."""
        return self.to_datetime(dt).strftime(fmt)

    def to_timestamp(self, dt: _DateTime) -> float:
        """转换为时间戳（秒）."""
        return self.to_datetime(dt).timestamp()

    def format_str(self, dt_str: str, fmt: str = settings.DATETIME_FORMAT) -> datetime:
        """将已知确定的 fmt 格式的字符串转换为 datetime 对象."""
        return datetime.strptime(dt_str, fmt).replace(tzinfo=self.tz)

    def parse_str(self, dt_str: str) -> datetime:
        """解析任意格式的日期字符串为 datetime 对象.

        不建议使用，内置了大量的正则表达式，性能较差
        """
        return parser.parse(dt_str).astimezone(self.tz)


timezone = TimeZone()
