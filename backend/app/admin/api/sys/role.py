from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.admin.schema import SysRoleDetail, SysRoleFilter, SysRoleInfo, SysRoleListItem
from backend.app.admin.schema.sys_role import (
    SysRoleBatchDelete,
    SysRoleBatchPatchStatus,
    SysRoleBatchUserAuth,
    SysRoleCreate,
    SysRoleOption,
    SysRolePatchDataScope,
    SysRolePatchStatus,
    SysRoleUpdate,
)
from backend.app.admin.service import sys_role_service
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.common.response.code import ResponseStatus
from backend.common.security.rbac import DependsRBAC
from backend.database.postgresql import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.post('/create', summary='创建角色', dependencies=[DependsRBAC('sys:role:create')])
async def create_role(db: CurrentSessionTransaction, params: SysRoleCreate):
    """创建新角色"""
    await sys_role_service.create(db=db, params=params)
    return response_base.success(res=ResponseStatus(200, '角色创建成功'))


@router.get(
    '/info',
    summary='获取角色信息',
    response_model=ResponseSchemaModel[SysRoleInfo],
    dependencies=[DependsRBAC('sys:role:info')],
)
async def get_role_info(db: CurrentSession, role_id: Annotated[int, Query(description='角色 ID')]):
    """获取角色基本信息"""
    data = await sys_role_service.get_role_info(db=db, pk=role_id)
    return response_base.success(data=data)


@router.get(
    '/detail',
    summary='获取角色详情',
    response_model=ResponseSchemaModel[SysRoleDetail],
    dependencies=[DependsRBAC('sys:role:detail')],
)
async def get_role_detail(db: CurrentSession, role_id: Annotated[int, Query(description='角色 ID')]):
    """获取角色详细信息"""
    data = await sys_role_service.get_role_detail(db=db, pk=role_id)
    return response_base.success(data=data)


@router.get(
    '/list',
    summary='获取角色列表',
    response_model=ResponseSchemaModel[list[SysRoleListItem]],
    dependencies=[DependsRBAC('sys:role:list')],
)
async def get_role_list(params: Annotated[SysRoleFilter, Query()]):
    """获取角色扁平列表（用于表格展示）"""
    data = await sys_role_service.get_list(params=params)
    return response_base.success(data=data)


@router.get(
    '/option',
    summary='获取角色选项',
    response_model=ResponseSchemaModel[list[SysRoleOption]],
    dependencies=[DependsRBAC('sys:role:list')],
)
async def get_role_option():
    """获取角色选项

    - 用于下拉选择器
    - 仅返回启用状态的角色
    """
    data = await sys_role_service.get_options()
    return response_base.success(data=data)


@router.put('/update', summary='更新角色信息（包括关联菜单权限）', dependencies=[DependsRBAC('sys:role:update')])
async def update_role(db: CurrentSessionTransaction, params: SysRoleUpdate):
    """更新角色信息（包括关联菜单权限）"""
    count = await sys_role_service.update(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '角色信息更新成功'))


@router.put('/update/data-scope', summary='更新角色数据范围权限', dependencies=[DependsRBAC('sys:role:update')])
async def update_role_data_scope(db: CurrentSessionTransaction, params: SysRolePatchDataScope):
    """更新角色数据范围权限"""
    count = await sys_role_service.patch_data_scope(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '角色数据范围权限更新成功'))


@router.patch('/update/status', summary='更新角色状态', dependencies=[DependsRBAC('sys:role:update')])
async def patch_role_status(db: CurrentSessionTransaction, params: SysRolePatchStatus):
    """更新角色状态"""
    count = await sys_role_service.patch_status(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '角色状态更新成功'))


@router.delete('/delete', summary='删除角色', dependencies=[DependsRBAC('sys:role:delete')])
async def delete_role(db: CurrentSessionTransaction, role_id: Annotated[int, Query(description='角色 ID')]):
    """删除单个角色

    注意：
    - 角色下有用户时不允许删除（待实现）
    """
    count = await sys_role_service.delete(db=db, pk=role_id)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '角色删除成功'))


@router.post('/batch/user/auth', summary='批量分配用户', dependencies=[DependsRBAC('sys:role:auth')])
async def post_role_user_auth(db: CurrentSessionTransaction, params: SysRoleBatchUserAuth):
    """批量分配用户"""
    result = await sys_role_service.batch_assign_users(db=db, params=params)
    assigned_count = result['assigned_count']
    return response_base.success(
        res=ResponseStatus(200, f'成功分配 {assigned_count} 个用户'),
        data=result,
    )


@router.post('/batch/user/cancel', summary='批量取消授权用户', dependencies=[DependsRBAC('sys:role:auth')])
async def post_role_user_cancel(db: CurrentSessionTransaction, params: SysRoleBatchUserAuth):
    """批量取消授权用户"""
    result = await sys_role_service.batch_revoke_users(db=db, params=params)
    revoked_count = result['revoked_count']
    return response_base.success(
        res=ResponseStatus(200, f'成功取消授权 {revoked_count} 个用户'),
        data=result,
    )


@router.delete('/batch/delete', summary='批量删除角色', dependencies=[DependsRBAC('sys:role:delete')])
async def batch_delete_role(db: CurrentSessionTransaction, params: SysRoleBatchDelete):
    """批量删除角色

    注意：
    - 不存在的角色ID会被自动跳过
    - 角色下有用户时不允许删除（待实现）
    """
    result = await sys_role_service.batch_delete(db=db, params=params)
    deleted_count = result['deleted_count']
    return response_base.success(
        res=ResponseStatus(200, f'成功删除 {deleted_count} 个角色'),
        data=result,
    )


@router.patch('/batch/update/status', summary='批量更新角色状态', dependencies=[DependsRBAC('sys:role:update')])
async def batch_patch_role_status(db: CurrentSessionTransaction, params: SysRoleBatchPatchStatus):
    """批量更新角色状态

    注意：
    - 不存在的角色ID会被自动跳过
    """
    result = await sys_role_service.batch_patch_status(db=db, params=params)
    updated_count = result['updated_count']
    return response_base.success(
        res=ResponseStatus(200, f'成功更新 {updated_count} 个角色状态'),
        data=result,
    )
