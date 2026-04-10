from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase
from backend.common.schema.type import IdsListInt


# ==================== 输入 Schema ====================
class SysRequestLogBatchDelete(SchemaBase):
    """请求日志批量删除请求."""

    ids: IdsListInt = Field(..., min_length=1, description='日志 ID 列表')


# ==================== 输出 Schema ====================
class SysRequestLogInfoBase(SchemaBase):
    """请求日志核心输出基类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='日志 ID')
    admin_id: int | None = Field(default=None, description='请求用户 ID')
    username: str | None = Field(default=None, description='请求用户名')
    path: str = Field(..., description='请求地址')
    method: str = Field(..., description='请求方法')
    module: str | None = Field(default=None, description='业务模块')
    trace_id: str | None = Field(default=None, description='链路追踪 ID')
    ip: str | None = Field(default=None, description='客户端 IP')
    description: str | None = Field(default=None, description='描述')
    status_code: int | None = Field(default=None, description='HTTP 响应状态码')
    cost_time: int | None = Field(default=None, description='请求耗时（毫秒）')
    level: int = Field(default=0, description='日志级别：0=普通 1=重要 2=敏感')
    result_status: int = Field(default=1, description='最终状态：0=失败 1=成功')
    created_time: datetime | None = Field(default=None, description='创建时间')


class SysRequestLogInfo(SysRequestLogInfoBase):
    """请求日志通用预览信息."""

    pass


class SysRequestLogDetail(SysRequestLogInfoBase):
    """请求日志详情（包含请求体和响应体）."""

    user_agent: str | None = Field(default=None, description='浏览器 User-Agent')
    request_params: str | None = Field(default=None, description='请求参数')
    request_body: str | None = Field(default=None, description='请求体')
    response_body: str | None = Field(default=None, description='响应内容')
    error_msg: str | None = Field(default=None, description='错误信息')
    remark: str | None = Field(default=None, description='备注')


class SysRequestLogListItem(SysRequestLogInfoBase):
    """请求日志分页列表结构."""

    pass


# ==================== 查询 Schema ====================
class SysRequestLogFilter(SchemaBase):
    """请求日志查询过滤条件."""

    admin_id: int | None = Field(default=None, description='按用户 ID 过滤')
    username: str | None = Field(default=None, max_length=64, description='按用户名过滤')
    path: str | None = Field(default=None, max_length=512, description='按请求路径过滤')
    method: str | None = Field(default=None, max_length=10, description='按请求方法过滤')
    module: str | None = Field(default=None, max_length=64, description='按业务模块过滤')
    ip: str | None = Field(default=None, max_length=128, description='按 IP 地址过滤')
    status_code: int | None = Field(default=None, description='按 HTTP 状态码过滤')
    level: int | None = Field(default=None, ge=0, le=2, description='按日志级别过滤')
    result_status: int | None = Field(default=None, ge=0, le=1, description='按最终状态过滤')
    begin_time: datetime | None = Field(default=None, description='开始时间范围')
    end_time: datetime | None = Field(default=None, description='结束时间范围')
