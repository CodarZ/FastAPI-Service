import zoneinfo

from datetime import datetime, timezone as dt_timezone

from backend.core.config import settings


class TimeZone:
    def __init__(self) -> None:
        self.config_tz = zoneinfo.ZoneInfo(settings.DATETIME_TIMEZONE)

    def now(self) -> datetime:
        """获取项目配置时区 datetime 对象"""
        return datetime.now(tz=self.config_tz)

    def to_utc(self, dt) -> datetime:
        """将 datetime 对象转换为 UTC 时区 datetime 对象

        Example:
            输入: 项目配置时区 datetime 对象
            输出: UTC datetime 对象
        """

        aware_dt = self.to_timezone(dt)
        return aware_dt.astimezone(dt_timezone.utc)

    def format_datetime(self, dt: datetime) -> datetime:
        """将 datetime 对象转换为项目配置时区 datetime 对象

        Example:
            输入: UTC datetime 对象
        """
        return dt.astimezone(self.config_tz)

    def format_str(self, dt_str: str, fmt: str = settings.DATETIME_FORMAT) -> datetime:
        """将字符串转为项目配置时区 datetime 对象

        Example:
            输入: dt_str='2024-01-01 12:30:45', fmt='%Y-%m-%d %H:%M:%S'
        """
        dt = datetime.strptime(dt_str, fmt)
        return self.to_timezone(dt)

    def to_timezone(self, dt: datetime | int | float) -> datetime:
        """转换为项目配置时区 datetime 对象

        Example:
            输入: 1704096000  # Unix 时间戳
            输入: datetime(2024, 1, 1, 12, 0, 0)  # 无时区信息
        """
        if isinstance(dt, (int, float)):
            return datetime.fromtimestamp(dt, tz=self.config_tz)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.config_tz)
        return dt.astimezone(self.config_tz)

    @staticmethod
    def to_str(dt: datetime, fmt: str = settings.DATETIME_FORMAT) -> str:
        """将 datetime 对象转换为指定格式字符串

        Example:
            输入: datetime 对象
            输出: '2024-01-01 12:30:45'
        """
        return dt.strftime(fmt)


timezone = TimeZone()
