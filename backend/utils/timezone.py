#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

from backend.core.config import settings


class TimeZone:
    """
    时区工具类，支持本地时区与 UTC 的时间转换、格式化处理。
    """

    def __init__(self, tz: str = settings.DATETIME_TIMEZONE) -> None:
        """
        初始化时区转换器。

        :param tz: 时区名称，默认从 settings.DATETIME_TIMEZONE 获取
        """
        self._tzinfo = ZoneInfo(tz)

    def now(self) -> datetime:
        """
        获取当前时区的当前时间。

        :return: 当前时区下的 datetime 对象
        """
        return datetime.now(self._tzinfo)

    def to_local(self, dt: datetime) -> datetime:
        """
        将 datetime 对象转换为当前时区时间。

        :param dt: 任意 datetime 对象
        :return: 当前时区下的 datetime 对象
        """
        return dt.astimezone(self._tzinfo)

    def from_str(self, date_str: str, format_str: str = settings.DATETIME_FORMAT) -> datetime:
        """
        将时间字符串解析为当前时区的 datetime 对象。

        :param date_str: 时间字符串
        :param format_str: 时间格式，默认使用 settings.DATETIME_FORMAT
        :return: 当前时区的 datetime 对象
        """
        dt = datetime.strptime(date_str, format_str)
        return dt.replace(tzinfo=self._tzinfo)

    @staticmethod
    def to_str(dt: datetime, format_str: str = settings.DATETIME_FORMAT) -> str:
        """
        将 datetime 对象格式化为字符串。

        :param dt: datetime 对象
        :param format_str: 时间格式字符串，默认使用 settings.DATETIME_FORMAT
        :return: 格式化后的时间字符串
        """
        return dt.strftime(format_str)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """
        将 datetime 对象转换为 UTC 时间。

        :param dt: 任意 datetime 对象
        :return: UTC 时区下的 datetime 对象
        """
        return dt.astimezone(dt_timezone.utc)


timezone = TimeZone()
