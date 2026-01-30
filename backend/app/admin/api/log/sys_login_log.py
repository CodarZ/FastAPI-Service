"""登录日志 API

登录日志是由认证中间件/登录接口自动记录的，不提供创建接口
主要提供查询、统计、删除等功能
"""

from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.admin.schema.sys_login_log import (
    SysLoginLogBatchDelete,
    SysLoginLogBatchDeleteResult,
    SysLoginLogClear,
    SysLoginLogClearResult,
    SysLoginLogDetail,
    SysLoginLogFilter,
    SysLoginLogListItem,
    SysLoginLogStatistics,
)
from backend.app.admin.service import sys_login_log_service
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.common.response.code import ResponseStatus
from backend.common.security.rbac import DependsRBAC
from backend.database.postgresql import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '/detail',
    summary='获取登录日志详情',
    response_model=ResponseSchemaModel[SysLoginLogDetail],
    dependencies=[DependsRBAC('log:login:detail')],
)
async def get_login_log_detail(db: CurrentSession, log_id: Annotated[int, Query(description='日志 ID')]):
    """获取登录日志详细信息

    包含完整的登录信息：
    - 用户信息（用户名、用户ID）
    - 登录状态（成功/异常）
    - 设备信息（IP、操作系统、浏览器、设备类型）
    - 地理位置（国家、地区、城市）
    - User-Agent 原始信息
    - 提示消息
    - 登录时间
    """
    data = await sys_login_log_service.get_log_detail(db=db, pk=log_id)
    return response_base.success(data=data)


@router.get(
    '/list',
    summary='获取登录日志列表',
    response_model=ResponseSchemaModel[list[SysLoginLogListItem]],
    dependencies=[DependsRBAC('log:login:list')],
)
async def get_login_log_list(params: Annotated[SysLoginLogFilter, Query()]):
    """获取登录日志列表

    支持多条件过滤：
    - 用户名（模糊匹配）
    - 用户ID
    - 登录状态（0异常 1正常）
    - IP 地址
    - 城市（模糊匹配）
    - 操作系统（模糊匹配）
    - 浏览器（模糊匹配）
    - 登录时间范围

    用于：
    - 查看用户登录历史
    - 监控异常登录
    - 安全审计
    """
    data = await sys_login_log_service.get_list(params=params)
    return response_base.success(data=data)


@router.delete('/delete', summary='删除登录日志', dependencies=[DependsRBAC('log:login:delete')])
async def delete_login_log(db: CurrentSessionTransaction, log_id: Annotated[int, Query(description='日志 ID')]):
    """删除单条登录日志"""
    count = await sys_login_log_service.delete(db=db, pk=log_id)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '日志删除成功'))


@router.delete(
    '/batch/delete',
    summary='批量删除登录日志',
    response_model=ResponseSchemaModel[SysLoginLogBatchDeleteResult],
    dependencies=[DependsRBAC('log:login:delete')],
)
async def batch_delete_login_log(db: CurrentSessionTransaction, params: SysLoginLogBatchDelete):
    """批量删除登录日志

    根据日志ID列表批量删除

    使用场景：
    - 清理测试数据
    - 删除选中的历史记录
    """
    result = await sys_login_log_service.batch_delete(db=db, params=params)

    return response_base.success(
        res=ResponseStatus(200, f'成功删除 {result.deleted_count} 条日志'),
        data=result,
    )


@router.delete(
    '/clear',
    summary='清理登录日志',
    response_model=ResponseSchemaModel[SysLoginLogClearResult],
    dependencies=[DependsRBAC('log:login:clear')],
)
async def clear_login_log(db: CurrentSessionTransaction, params: SysLoginLogClear):
    """批量清理登录日志

    支持按条件清理：
    - 清理指定时间之前的日志（before_time）
    - 清理指定状态的日志（status: 0异常/1正常）

    使用场景：
    - 定期清理历史日志（如保留最近3个月的记录）
    - 清理异常登录日志
    - 清理测试环境日志
    - 数据归档前的清理

    注意：
    - 至少需要提供一个清理条件
    - 建议定期清理以控制数据量
    """
    result = await sys_login_log_service.clear(db=db, params=params)

    return response_base.success(
        res=ResponseStatus(200, f'成功清理 {result.cleared_count} 条日志'),
        data=result,
    )


@router.get(
    '/statistics',
    summary='获取登录日志统计',
    response_model=ResponseSchemaModel[SysLoginLogStatistics],
    dependencies=[DependsRBAC('log:login:statistics')],
)
async def get_login_log_statistics(params: Annotated[SysLoginLogFilter, Query()]):
    """获取登录日志统计信息

    统计内容：
    - 总登录次数（total_count）
    - 成功登录次数（success_count）
    - 异常登录次数（error_count）

    支持按条件过滤统计：
    - 按用户统计
    - 按时间范围统计
    - 按状态统计
    - 按地理位置统计

    用于：
    - 安全分析
    - 用户行为分析
    - 登录成功率监控
    """
    data = await sys_login_log_service.get_statistics(params=params)
    return response_base.success(data=data)
