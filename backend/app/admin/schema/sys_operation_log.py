"""操作日志 Schema 定义

包含操作日志相关的所有 Schema：ListItem/Detail/Filter
日志类通常只需要查询输出，不需要 Create/Update 等输入 Schema
"""

from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase

if TYPE_CHECKING:
    from datetime import datetime


# ==================== 输出 Schema ====================
class SysOperationLogListItem(SchemaBase):
    """操作日志列表项（表格展示）"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='日志ID')
    username: str | None = Field(default=None, description='操作用户')
    moudle: str = Field(description='操作模块')
    path: str = Field(description='请求路径')
    method: str = Field(description='请求方式')
    code: str = Field(description='操作状态码')
    status: int = Field(description='操作状态(0异常 1正常)')
    cost_time: float = Field(description='请求耗时(ms)')
    ip: str = Field(description='IP地址')
    city: str | None = Field(default=None, description='城市')
    os: str | None = Field(default=None, description='操作系统')
    browser: str | None = Field(default=None, description='浏览器')
    operated_time: datetime = Field(description='操作时间')


class SysOperationLogDetail(SchemaBase):
    """操作日志完整详情"""

    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int = Field(description='日志ID')
    username: str | None = Field(default=None, description='操作用户')
    moudle: str = Field(description='操作模块')
    path: str = Field(description='请求路径')
    trace_id: str = Field(description='请求跟踪ID')
    method: str = Field(description='请求方式')
    code: str = Field(description='操作状态码')
    args: dict[str, Any] | None = Field(default=None, description='请求参数')
    msg: str | None = Field(default=None, description='提示消息')
    cost_time: float = Field(description='请求耗时(ms)')
    ip: str = Field(description='IP地址')
    country: str | None = Field(default=None, description='国家')
    region: str | None = Field(default=None, description='地区')
    city: str | None = Field(default=None, description='城市')
    user_agent: str = Field(description='请求头')
    os: str | None = Field(default=None, description='操作系统')
    browser: str | None = Field(default=None, description='浏览器')
    device: str | None = Field(default=None, description='设备')
    status: int = Field(description='操作状态(0异常 1正常)')
    operated_time: datetime = Field(description='操作时间')
    created_time: datetime = Field(description='创建时间')


# ==================== 查询 Schema ====================
class SysOperationLogFilter(SchemaBase):
    """操作日志查询条件"""

    username: str | None = Field(default=None, max_length=20, description='操作用户(模糊)')
    moudle: str | None = Field(default=None, max_length=255, description='操作模块(模糊)')
    path: str | None = Field(default=None, description='请求路径(模糊)')
    trace_id: str | None = Field(default=None, max_length=128, description='请求跟踪ID')
    method: str | None = Field(default=None, max_length=10, description='请求方式')
    code: str | None = Field(default=None, max_length=10, description='操作状态码')
    status: int | None = Field(default=None, ge=0, le=1, description='操作状态')
    ip: str | None = Field(default=None, max_length=50, description='IP地址')
    city: str | None = Field(default=None, max_length=50, description='城市(模糊)')
    cost_time_min: float | None = Field(default=None, ge=0, description='最小耗时(ms)')
    cost_time_max: float | None = Field(default=None, ge=0, description='最大耗时(ms)')
    operated_time_start: datetime | None = Field(default=None, description='操作时间起')
    operated_time_end: datetime | None = Field(default=None, description='操作时间止')
    keyword: str | None = Field(default=None, max_length=100, description='关键词(用户名/模块/路径)')


class SysOperationLogAdvancedFilter(SysOperationLogFilter):
    """操作日志高级查询条件"""

    os: str | None = Field(default=None, max_length=50, description='操作系统(模糊)')
    browser: str | None = Field(default=None, max_length=50, description='浏览器(模糊)')
    device: str | None = Field(default=None, max_length=50, description='设备(模糊)')
    country: str | None = Field(default=None, max_length=50, description='国家(模糊)')
    region: str | None = Field(default=None, max_length=50, description='地区(模糊)')


class SysOperationLogBatchDelete(SchemaBase):
    """操作日志批量删除"""

    log_ids: list[int] = Field(min_length=1, description='日志ID列表')


class SysOperationLogClear(SchemaBase):
    """操作日志清理（按时间范围）"""

    before_time: datetime | None = Field(default=None, description='清理此时间之前的日志')
    status: int | None = Field(default=None, ge=0, le=1, description='仅清理指定状态的日志')
    moudle: str | None = Field(default=None, max_length=255, description='仅清理指定模块的日志')


# ==================== 统计 Schema ====================
class SysOperationLogStatistics(SchemaBase):
    """操作日志统计"""

    total_count: int = Field(description='总数量')
    success_count: int = Field(description='成功数量')
    error_count: int = Field(description='异常数量')
    avg_cost_time: float = Field(description='平均耗时(ms)')
    max_cost_time: float = Field(description='最大耗时(ms)')
    min_cost_time: float = Field(description='最小耗时(ms)')


class SysOperationLogTrend(SchemaBase):
    """操作日志趋势（按时间维度统计）"""

    date: str = Field(description='日期')
    total_count: int = Field(description='总数量')
    success_count: int = Field(description='成功数量')
    error_count: int = Field(description='异常数量')
    avg_cost_time: float = Field(description='平均耗时(ms)')


class SysOperationLogModuleStats(SchemaBase):
    """操作日志模块统计"""

    moudle: str = Field(description='模块名称')
    total_count: int = Field(description='调用次数')
    success_rate: float = Field(description='成功率(%)')
    avg_cost_time: float = Field(description='平均耗时(ms)')
