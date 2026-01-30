"""菜单管理 API"""

from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.admin.schema.sys_menu import (
    SysMenuBatchDelete,
    SysMenuBatchPatchStatus,
    SysMenuCreate,
    SysMenuDetail,
    SysMenuFilter,
    SysMenuInfo,
    SysMenuListItem,
    SysMenuOption,
    SysMenuOptionTree,
    SysMenuPatchHidden,
    SysMenuPatchParent,
    SysMenuPatchSort,
    SysMenuPatchStatus,
    SysMenuRoute,
    SysMenuTableTree,
    SysMenuTreeNode,
    SysMenuUpdate,
)
from backend.app.admin.service import sys_menu_service
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.common.response.code import ResponseStatus
from backend.common.security.rbac import DependsRBAC
from backend.database.postgresql import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.post('/create', summary='创建菜单', dependencies=[DependsRBAC('sys:menu:create')])
async def create_menu(db: CurrentSessionTransaction, params: SysMenuCreate):
    """创建新菜单"""
    await sys_menu_service.create(db=db, params=params)
    return response_base.success(res=ResponseStatus(200, '菜单创建成功'))


@router.get(
    '/info',
    summary='获取菜单信息',
    response_model=ResponseSchemaModel[SysMenuInfo],
    dependencies=[DependsRBAC('sys:menu:info')],
)
async def get_menu_info(db: CurrentSession, menu_id: Annotated[int, Query(description='菜单 ID')]):
    """获取菜单基本信息"""
    data = await sys_menu_service.get_menu_info(db=db, pk=menu_id)
    return response_base.success(data=data)


@router.get(
    '/detail',
    summary='获取菜单详情',
    response_model=ResponseSchemaModel[SysMenuDetail],
    dependencies=[DependsRBAC('sys:menu:detail')],
)
async def get_menu_detail(db: CurrentSession, menu_id: Annotated[int, Query(description='菜单 ID')]):
    """获取菜单完整详情"""
    data = await sys_menu_service.get_menu_detail(db=db, pk=menu_id)
    return response_base.success(data=data)


@router.get(
    '/list',
    summary='获取菜单列表',
    response_model=ResponseSchemaModel[list[SysMenuListItem]],
    dependencies=[DependsRBAC('sys:menu:list')],
)
async def get_menu_list(params: Annotated[SysMenuFilter, Query()]):
    """获取菜单列表（扁平表格展示）"""
    data = await sys_menu_service.get_list(params=params)
    return response_base.success(data=data)


@router.get(
    '/list-tree',
    summary='获取菜单树形表格',
    response_model=ResponseSchemaModel[list[SysMenuTableTree]],
    dependencies=[DependsRBAC('sys:menu:list')],
)
async def get_menu_table_tree(params: Annotated[SysMenuFilter, Query()]):
    """获取菜单树形表格（用于前端表格树形展示，支持筛选）"""
    data = await sys_menu_service.get_table_tree(params=params)
    return response_base.success(data=data)


@router.get(
    '/tree',
    summary='获取菜单树',
    response_model=ResponseSchemaModel[list[SysMenuTreeNode]],
    dependencies=[DependsRBAC('sys:menu:list')],
)
async def get_menu_tree():
    """获取菜单树（树形结构展示，用于菜单管理页面）"""
    data = await sys_menu_service.get_tree()
    return response_base.success(data=data)


@router.get(
    '/options',
    summary='获取菜单选项',
    response_model=ResponseSchemaModel[list[SysMenuOption]],
    dependencies=[DependsRBAC('sys:menu:list')],
)
async def get_menu_options():
    """获取菜单选项列表（用于下拉选择器）"""
    data = await sys_menu_service.get_options()
    return response_base.success(data=data)


@router.get(
    '/option-tree',
    summary='获取菜单选项树',
    response_model=ResponseSchemaModel[list[SysMenuOptionTree]],
    dependencies=[DependsRBAC('sys:menu:list')],
)
async def get_menu_option_tree():
    """获取菜单选项树（用于树形选择器，如上级菜单选择）"""
    data = await sys_menu_service.get_option_tree()
    return response_base.success(data=data)


@router.get(
    '/routes',
    summary='获取前端路由配置',
    response_model=ResponseSchemaModel[list[SysMenuRoute]],
    dependencies=[DependsRBAC('sys:menu:list')],
)
async def get_menu_routes():
    """获取前端路由配置（用于动态生成前端路由）"""
    data = await sys_menu_service.get_routes()
    return response_base.success(data=data)


@router.put('/update', summary='更新菜单信息', dependencies=[DependsRBAC('sys:menu:update')])
async def update_menu(db: CurrentSessionTransaction, params: SysMenuUpdate):
    """更新菜单信息（全量更新）"""
    count = await sys_menu_service.update(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '菜单信息更新成功'))


@router.patch('/update/status', summary='更新菜单状态', dependencies=[DependsRBAC('sys:menu:update')])
async def patch_menu_status(db: CurrentSessionTransaction, params: SysMenuPatchStatus):
    """修改菜单状态"""
    count = await sys_menu_service.patch_status(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '菜单状态更新成功'))


@router.patch('/update/hidden', summary='更新菜单隐藏状态', dependencies=[DependsRBAC('sys:menu:update')])
async def patch_menu_hidden(db: CurrentSessionTransaction, params: SysMenuPatchHidden):
    """修改菜单隐藏状态"""
    count = await sys_menu_service.patch_hidden(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '菜单隐藏状态更新成功'))


@router.patch('/update/sort', summary='更新菜单排序', dependencies=[DependsRBAC('sys:menu:update')])
async def patch_menu_sort(db: CurrentSessionTransaction, params: SysMenuPatchSort):
    """修改菜单排序"""
    count = await sys_menu_service.patch_sort(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '菜单排序更新成功'))


@router.patch('/update/parent', summary='更新菜单父级', dependencies=[DependsRBAC('sys:menu:update')])
async def patch_menu_parent(db: CurrentSessionTransaction, params: SysMenuPatchParent):
    """修改菜单父级（移动菜单）"""
    count = await sys_menu_service.patch_parent(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '菜单父级更新成功'))


@router.patch('/batch/update/status', summary='批量更新菜单状态', dependencies=[DependsRBAC('sys:menu:update')])
async def batch_patch_menu_status(db: CurrentSessionTransaction, params: SysMenuBatchPatchStatus):
    """批量修改菜单状态"""
    count = await sys_menu_service.batch_update_status(db=db, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, f'成功更新 {count} 个菜单状态'))


@router.delete('/delete', summary='删除菜单', dependencies=[DependsRBAC('sys:menu:delete')])
async def delete_menu(db: CurrentSessionTransaction, menu_id: Annotated[int, Query(description='菜单 ID')]):
    """删除菜单（必须先删除子菜单）"""
    count = await sys_menu_service.delete(db=db, pk=menu_id)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '菜单删除成功'))


@router.delete('/batch/delete', summary='批量删除菜单', dependencies=[DependsRBAC('sys:menu:delete')])
async def batch_delete_menu(db: CurrentSessionTransaction, params: SysMenuBatchDelete):
    """批量删除菜单（必须先删除子菜单）"""
    count = await sys_menu_service.batch_delete(db=db, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, f'成功删除 {count} 个菜单'))
