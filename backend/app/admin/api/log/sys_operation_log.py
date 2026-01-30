"""操作日志 API

操作日志是由中间件自动记录的，不提供创建接口
主要提供查询、统计、删除等功能
"""

from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.admin.schema.sys_operation_log import (
    SysOperationLogBatchDelete,
    SysOperationLogClear,
    SysOperationLogDetail,
    SysOperationLogFilter,
    SysOperationLogListItem,
    SysOperationLogModuleStats,
    SysOperationLogModuleStatsQuery,
    SysOperationLogStatistics,
    SysOperationLogTrend,
    SysOperationLogTrendQuery,
)
from backend.app.admin.service import sys_operation_log_service
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.common.response.code import ResponseStatus
from backend.common.security.rbac import DependsRBAC
from backend.database.postgresql import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '/detail',
    summary='获取操作日志详情',
    response_model=ResponseSchemaModel[SysOperationLogDetail],
    dependencies=[DependsRBAC('log:operation:detail')],
)
async def get_operation_log_detail(db: CurrentSession, log_id: Annotated[int, Query(description='日志 ID')]):
    """获取操作日志详细信息"""
    data = await sys_operation_log_service.get_log_detail(db=db, pk=log_id)
    return response_base.success(data=data)


@router.get(
    '/detail/trace',
    summary='根据跟踪ID获取日志',
    response_model=ResponseSchemaModel[SysOperationLogDetail],
    dependencies=[DependsRBAC('log:operation:detail')],
)
async def get_operation_log_by_trace_id(db: CurrentSession, trace_id: Annotated[str, Query(description='跟踪 ID')]):
    """根据跟踪ID获取操作日志详情

    用于日志追踪和问题排查
    """
    data = await sys_operation_log_service.get_log_by_trace_id(db=db, trace_id=trace_id)
    return response_base.success(data=data)


@router.get(
    '/list',
    summary='获取操作日志列表',
    response_model=ResponseSchemaModel[list[SysOperationLogListItem]],
    dependencies=[DependsRBAC('log:operation:list')],
)
async def get_operation_log_list(params: Annotated[SysOperationLogFilter, Query()]):
    """获取操作日志列表

    支持多条件过滤：
    - 用户名、模块、路径、跟踪ID
    - 请求方式、状态码、状态
    - IP、操作系统、浏览器、设备
    - 地理位置（国家、地区、城市）
    - 耗时范围、操作时间范围
    """
    data = await sys_operation_log_service.get_list(params=params)
    return response_base.success(data=data)


@router.delete('/delete', summary='删除操作日志', dependencies=[DependsRBAC('log:operation:delete')])
async def delete_operation_log(db: CurrentSessionTransaction, log_id: Annotated[int, Query(description='日志 ID')]):
    """删除单条操作日志"""
    count = await sys_operation_log_service.delete(db=db, pk=log_id)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '日志删除成功'))


@router.delete('/batch/delete', summary='批量删除操作日志', dependencies=[DependsRBAC('log:operation:delete')])
async def batch_delete_operation_log(db: CurrentSessionTransaction, params: SysOperationLogBatchDelete):
    """批量删除操作日志

    根据日志ID列表批量删除
    """
    result = await sys_operation_log_service.batch_delete(db=db, params=params)
    deleted_count = result['deleted_count']

    return response_base.success(
        res=ResponseStatus(200, f'成功删除 {deleted_count} 条日志'),
        data=result,
    )


@router.delete('/clear', summary='清理操作日志', dependencies=[DependsRBAC('log:operation:clear')])
async def clear_operation_log(db: CurrentSessionTransaction, params: SysOperationLogClear):
    """批量清理操作日志

    支持按条件清理：
    - 清理指定时间之前的日志
    - 清理指定状态的日志（成功/异常）
    - 清理指定模块的日志

    使用场景：
    - 定期清理历史日志
    - 清理异常日志
    - 清理测试环境日志
    """
    result = await sys_operation_log_service.clear(db=db, params=params)
    cleared_count = result['cleared_count']

    return response_base.success(
        res=ResponseStatus(200, f'成功清理 {cleared_count} 条日志'),
        data=result,
    )


@router.get(
    '/statistics',
    summary='获取操作日志统计',
    response_model=ResponseSchemaModel[SysOperationLogStatistics],
    dependencies=[DependsRBAC('log:operation:statistics')],
)
async def get_operation_log_statistics(params: Annotated[SysOperationLogFilter, Query()]):
    """获取操作日志统计信息

    统计内容：
    - 总数量
    - 成功/异常数量
    - 平均耗时、最大耗时、最小耗时

    支持按条件过滤统计
    """
    data = await sys_operation_log_service.get_statistics(params=params)
    return response_base.success(data=data)


@router.get(
    '/trend',
    summary='获取操作日志趋势',
    response_model=ResponseSchemaModel[list[SysOperationLogTrend]],
    dependencies=[DependsRBAC('log:operation:trend')],
)
async def get_operation_log_trend(params: Annotated[SysOperationLogTrendQuery, Query()]):
    """获取操作日志趋势（按 `operated_time` 日期统计）

    按日期分组统计：
    - 每日总数量
    - 每日成功/异常数量
    - 每日平均耗时

    默认统计最近7天
    """
    data = await sys_operation_log_service.get_trend(params=params, days=params.days)
    return response_base.success(data=data)


@router.get(
    '/module/statistics',
    summary='获取模块调用统计',
    response_model=ResponseSchemaModel[list[SysOperationLogModuleStats]],
    dependencies=[DependsRBAC('log:operation:module')],
)
async def get_operation_log_module_stats(params: Annotated[SysOperationLogModuleStatsQuery, Query()]):
    """获取操作日志模块统计

    按模块分组统计：
    - 调用次数
    - 成功率
    - 平均耗时

    按调用次数降序排列，默认返回前10个
    """
    data = await sys_operation_log_service.get_module_statistics(params=params, limit=params.limit)
    return response_base.success(data=data)
