"""登录日志 Schema 定义

包含登录日志相关的所有 Schema：ListItem/Detail/Filter
日志类通常只需要查询输出，不需要 Create/Update 等输入 Schema
"""

from datetime import datetime
from fastapi import Query
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase
from backend.utils.validator.types import IdsListInt, LocalDatetime, StatusInt


# ==================== 日志创建（中间件等内部使用） =======================
class SysLoginLogCreate(SchemaBase):
    """登录日志创建（内部使用）"""

    username: str | None = Field(default=None, description='用户名')
    user_id: int | None = Field(default=None, description='用户ID')
    status: StatusInt = Field(description='登录状态(0异常 1正常)')
    ip: str | None = Field(default=None, description='IP地址')
    country: str | None = Field(default=None, description='国家')
    region: str | None = Field(default=None, description='地区')
    city: str | None = Field(default=None, description='城市')
    user_agent: str | None = Field(default=None, description='请求头')
    os: str | None = Field(default=None, description='操作系统')
    browser: str | None = Field(default=None, description='浏览器')
    device: str | None = Field(default=None, description='设备')
    msg: str | None = Field(default=None, description='提示消息')
    login_time: datetime = Field(description='登录时间')


# ==================== 输出 Schema ====================
class SysLoginLogListItem(SchemaBase):
    """登录日志列表项（表格展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='日志ID')
    username: str | None = Field(default=None, description='用户名')
    user_id: int | None = Field(default=None, description='用户ID')
    status: StatusInt = Field(description='登录状态(0异常 1正常)')
    ip: str | None = Field(default=None, description='IP地址')
    city: str | None = Field(default=None, description='城市')
    os: str | None = Field(default=None, description='操作系统')
    browser: str | None = Field(default=None, description='浏览器')
    device: str | None = Field(default=None, description='设备')
    msg: str | None = Field(default=None, description='提示消息')
    login_time: LocalDatetime = Field(description='登录时间')


class SysLoginLogDetail(SchemaBase):
    """登录日志完整详情"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='日志ID')
    username: str | None = Field(default=None, description='用户名')
    user_id: int | None = Field(default=None, description='用户ID')
    status: StatusInt = Field(description='登录状态(0异常 1正常)')
    ip: str | None = Field(default=None, description='IP地址')
    country: str | None = Field(default=None, description='国家')
    region: str | None = Field(default=None, description='地区')
    city: str | None = Field(default=None, description='城市')
    user_agent: str | None = Field(default=None, description='请求头')
    os: str | None = Field(default=None, description='操作系统')
    browser: str | None = Field(default=None, description='浏览器')
    device: str | None = Field(default=None, description='设备')
    msg: str | None = Field(default=None, description='提示消息')
    login_time: LocalDatetime = Field(description='登录时间')
    created_time: LocalDatetime = Field(description='创建时间')


# ==================== 查询 Schema ====================
class SysLoginLogFilter(SchemaBase):
    """登录日志查询条件"""

    username: str | None = Query(default=None, max_length=20, description='用户名(模糊)')
    user_id: int | None = Query(default=None, description='用户ID')
    status: StatusInt | None = Query(default=None, description='登录状态')
    ip: str | None = Query(default=None, max_length=50, description='IP地址')
    city: str | None = Query(default=None, max_length=50, description='城市(模糊)')
    os: str | None = Query(default=None, max_length=50, description='操作系统(模糊)')
    browser: str | None = Query(default=None, max_length=50, description='浏览器(模糊)')
    login_time_start: LocalDatetime | None = Query(default=None, description='登录时间起')
    login_time_end: LocalDatetime | None = Query(default=None, description='登录时间止')


class SysLoginLogBatchDelete(SchemaBase):
    """登录日志批量删除"""

    log_ids: IdsListInt = Field(min_length=1, description='日志ID列表')


class SysLoginLogClear(SchemaBase):
    """登录日志清理（按时间范围）"""

    before_time: LocalDatetime | None = Field(default=None, description='清理此时间之前的日志')
    status: StatusInt | None = Field(default=None, description='仅清理指定状态的日志')


# ==================== 操作结果 Schema ====================
class SysLoginLogBatchDeleteResult(SchemaBase):
    """批量删除结果"""

    deleted_count: int = Field(description='实际删除的数量')


class SysLoginLogClearResult(SchemaBase):
    """清理日志结果"""

    cleared_count: int = Field(description='实际清理的数量')


class SysLoginLogStatistics(SchemaBase):
    """登录日志统计"""

    total_count: int = Field(description='总登录次数')
    success_count: int = Field(description='成功登录次数')
    error_count: int = Field(description='异常登录次数')
