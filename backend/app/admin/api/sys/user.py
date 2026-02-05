from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.admin.schema.sys_user import (
    SysUserBatchDelete,
    SysUserBatchPatchStatus,
    SysUserCreate,
    SysUserDetail,
    SysUserFilter,
    SysUserInfo,
    SysUserListItem,
    SysUserPatchPassword,
    SysUserPatchProfile,
    SysUserPatchStatus,
    SysUserResetPassword,
    SysUserUpdate,
)
from backend.app.admin.service import sys_user_service
from backend.common.pagination import DependsPagination, PageList
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.common.response.code import ResponseStatus
from backend.common.security.rbac import DependsRBAC
from backend.database.postgresql import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.post('/create', summary='创建用户')
async def create_user(db: CurrentSessionTransaction, params: SysUserCreate):
    """创建新用户"""
    await sys_user_service.create(db=db, params=params)
    return response_base.success(res=ResponseStatus(200, '用户创建成功'))


@router.get(
    '/info',
    summary='获取用户信息',
    response_model=ResponseSchemaModel[SysUserInfo],
    dependencies=[DependsRBAC('sys:user:info')],
)
async def get_user_info(db: CurrentSession, user_id: Annotated[int, Query(description='用户 ID')]):
    data = await sys_user_service.get_user_info(db=db, pk=user_id)
    return response_base.success(data=data)


@router.get(
    '/detail',
    summary='获取用户详情',
    response_model=ResponseSchemaModel[SysUserDetail],
    dependencies=[DependsRBAC('sys:user:detail')],
)
async def get_user_detail(db: CurrentSession, user_id: Annotated[int, Query(description='用户 ID')]):
    data = await sys_user_service.get_user_detail(db=db, pk=user_id)
    return response_base.success(data=data)


@router.get(
    '/permissions',
    summary='获取用户权限列表',
    response_model=ResponseSchemaModel[list[str]],
    dependencies=[DependsRBAC('sys:user:permissions')],
)
async def get_user_permissions(user_id: Annotated[int, Query(description='用户 ID')]):
    """获取指定用户的所有权限标识

    返回用户通过角色关联获得的所有菜单权限标识列表
    """
    permissions = await sys_user_service.get_permissions(user_id=user_id)
    return response_base.success(data=list(permissions))


@router.get(
    '/list',
    summary='获取用户列表',
    response_model=ResponseSchemaModel[PageList[SysUserListItem]],
    dependencies=[DependsRBAC('sys:user:list'), DependsPagination],
)
async def get_user_list(params: Annotated[SysUserFilter, Depends()]):

    data = await sys_user_service.get_list(params=params)
    return response_base.success(data=data)


@router.put('/update', summary='更新用户信息', dependencies=[DependsRBAC('sys:user:update')])
async def update_user(db: CurrentSessionTransaction, params: SysUserUpdate):
    count = await sys_user_service.update(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '用户信息更新成功'))


@router.patch('/update/status', summary='更新用户状态', dependencies=[DependsRBAC('sys:user:update')])
async def patch_user_status(db: CurrentSessionTransaction, params: SysUserPatchStatus):
    count = await sys_user_service.patch_status(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '用户状态更新成功'))


@router.patch('/update/profile', summary='更新用户资料', dependencies=[DependsRBAC('sys:user:update')])
async def patch_user_profile(db: CurrentSessionTransaction, params: SysUserPatchProfile):
    count = await sys_user_service.patch_profile(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '用户资料更新成功'))


@router.patch('/update/password', summary='修改用户密码', dependencies=[DependsRBAC('sys:user:update')])
async def patch_user_password(db: CurrentSessionTransaction, params: SysUserPatchPassword):
    """用户修改自己的密码

    需要验证旧密码是否正确，两次新密码是否一致（Schema 层已校验）
    """
    count = await sys_user_service.patch_password(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '密码修改成功'))


@router.patch('/reset/password', summary='重置用户密码', dependencies=[DependsRBAC('sys:user:reset')])
async def reset_user_password(db: CurrentSessionTransaction, params: SysUserResetPassword):
    """管理员重置用户密码

    无需验证旧密码，直接设置新密码
    """
    count = await sys_user_service.reset_password(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '密码重置成功'))


@router.delete('/delete', summary='删除用户', dependencies=[DependsRBAC('sys:user:delete')])
async def delete_user(db: CurrentSessionTransaction, user_id: Annotated[int, Query(description='用户 ID')]):
    """删除单个用户

    注意：
    - 超级管理员不允许被删除
    """
    count = await sys_user_service.delete(db=db, pk=user_id)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '用户删除成功'))


@router.delete('/batch/delete', summary='批量删除用户', dependencies=[DependsRBAC('sys:user:delete')])
async def batch_delete_user(db: CurrentSessionTransaction, params: SysUserBatchDelete):
    """批量删除用户

    注意：
    - 不存在的用户ID会被自动跳过
    - 超级管理员不会被删除
    """
    result = await sys_user_service.batch_delete(db=db, params=params)
    deleted_count = result['deleted_count']

    return response_base.success(
        res=ResponseStatus(200, f'成功删除 {deleted_count} 个用户'),
        data=result,
    )


@router.patch('/batch/update/status', summary='批量更新用户状态', dependencies=[DependsRBAC('sys:user:update')])
async def batch_patch_user_status(db: CurrentSessionTransaction, params: SysUserBatchPatchStatus):
    """批量更新用户状态

    注意：
    - 不存在的用户ID会被自动跳过
    - 超级管理员不会被修改状态
    """
    result = await sys_user_service.batch_patch_status(db=db, params=params)
    updated_count = result['updated_count']

    return response_base.success(
        res=ResponseStatus(200, f'成功更新 {updated_count} 个用户状态'),
        data=result,
    )
