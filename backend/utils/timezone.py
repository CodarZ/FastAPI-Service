import zoneinfo

from datetime import datetime

from backend.core.config import settings


class TimeZone:
    def to_utc(self, dt):
        """将 datetime 对象转换为 UTC 时区 datetime 对象"""
        from datetime import timezone as dt_timezone

        aware_dt = self.to_timezone(dt)
        return aware_dt.astimezone(dt_timezone.utc)

    """时区工具类，根据配置项做统一转换/格式化。"""

    def __init__(self) -> None:
        self.config_tz = zoneinfo.ZoneInfo(settings.DATETIME_TIMEZONE)

    def now(self) -> datetime:
        return datetime.now(tz=self.config_tz)

    def format_datetime(self, dt: datetime) -> datetime:
        """将 datetime 对象转换为当前时区 datetime 对象"""
        return dt.astimezone(self.config_tz)

    def format_str(self, dt_str: str, fmt: str = settings.DATETIME_FORMAT) -> datetime:
        """将字符串转为 datetime 对象"""
        dt = datetime.strptime(dt_str, fmt)
        return self.to_timezone(dt)

    def to_timezone(self, dt: datetime | int | float) -> datetime:
        """转换为当前时区 datetime 对象"""
        if isinstance(dt, (int, float)):
            return datetime.fromtimestamp(dt, tz=self.config_tz)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.config_tz)
        return dt.astimezone(self.config_tz)

    @staticmethod
    def to_str(dt: datetime, fmt: str = settings.DATETIME_FORMAT) -> str:
        """将 datetime 对象转换为指定格式字符串"""
        return dt.strftime(fmt)


timezone = TimeZone()
