#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zoneinfo

from datetime import datetime, timezone as datetime_timezone

from backend.core.config import settings


class TimeZone:
    """
    时区工具类，支持本地时区与 UTC 的时间转换、格式化处理。
    """

    def __init__(self) -> None:
        """初始化时区转换器"""
        self.tz_info = zoneinfo.ZoneInfo(settings.DATETIME_TIMEZONE)

    def now(self) -> datetime:
        """获取当前时区时间"""
        return datetime.now(self.tz_info)

    def from_datetime(self, t: datetime) -> datetime:
        """将 datetime 对象转换为当前时区时间"""
        return t.astimezone(self.tz_info)

    def from_str(self, t_str: str, format_str: str = settings.DATETIME_FORMAT) -> datetime:
        """将时间字符串转换为当前时区的 datetime 对象"""
        return datetime.strptime(t_str, format_str).replace(tzinfo=self.tz_info)

    @staticmethod
    def to_str(t: datetime, format_str: str = settings.DATETIME_FORMAT) -> str:
        """将 datetime 对象转换为指定格式的时间字符串"""
        return t.strftime(format_str)

    @staticmethod
    def to_utc(t: datetime | int) -> datetime:
        """将 datetime 对象或时间戳转换为 UTC 时区时间"""
        if isinstance(t, datetime):
            return t.astimezone(datetime_timezone.utc)
        return datetime.fromtimestamp(t, tz=datetime_timezone.utc)


timezone: TimeZone = TimeZone()
