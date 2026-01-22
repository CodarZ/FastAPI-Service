from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.admin.schema.sys_dept import (
    SysDeptBatchDelete,
    SysDeptBatchPatchStatus,
    SysDeptCreate,
    SysDeptDetail,
    SysDeptFilter,
    SysDeptInfo,
    SysDeptListItem,
    SysDeptOptionTree,
    SysDeptPatchParent,
    SysDeptPatchSort,
    SysDeptPatchStatus,
    SysDeptTreeNode,
    SysDeptUpdate,
)
from backend.app.admin.service import sys_dept_service
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.common.response.code import ResponseStatus
from backend.database.postgresql import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.post('/create', summary='创建部门')
async def create_dept(db: CurrentSessionTransaction, params: SysDeptCreate):
    """创建新部门"""
    await sys_dept_service.create(db=db, params=params)
    return response_base.success(res=ResponseStatus(200, '部门创建成功'))


@router.get('/info', summary='获取部门信息', response_model=ResponseSchemaModel[SysDeptInfo])
async def get_dept_info(db: CurrentSession, dept_id: Annotated[int, Query(description='部门 ID')]):
    """获取部门基本信息"""
    data = await sys_dept_service.get_dept_info(db=db, pk=dept_id)
    return response_base.success(data=data)


@router.get('/detail', summary='获取部门详情', response_model=ResponseSchemaModel[SysDeptDetail])
async def get_dept_detail(db: CurrentSession, dept_id: Annotated[int, Query(description='部门 ID')]):
    """获取部门完整详情"""
    data = await sys_dept_service.get_dept_detail(db=db, pk=dept_id)
    return response_base.success(data=data)


@router.get('/list', summary='获取部门列表', response_model=ResponseSchemaModel[list[SysDeptListItem]])
async def get_dept_list(params: Annotated[SysDeptFilter, Query()]):
    """获取部门扁平列表（用于表格展示）"""
    data = await sys_dept_service.get_list(params=params)
    return response_base.success(data=data)


@router.get('/tree', summary='获取部门树', response_model=ResponseSchemaModel[list[SysDeptTreeNode]])
async def get_dept_tree(params: Annotated[SysDeptFilter, Query()]):
    """获取部门树形结构（用于树形表格展示）"""
    data = await sys_dept_service.get_tree(params=params)
    return response_base.success(data=data)


@router.get('/option-tree', summary='获取部门选项树', response_model=ResponseSchemaModel[list[SysDeptOptionTree]])
async def get_dept_option_tree():
    """获取部门选项树（用于下拉选择器，仅返回启用状态的部门）"""
    data = await sys_dept_service.get_option_tree()
    return response_base.success(data=data)


@router.put('/update', summary='更新部门信息')
async def update_dept(db: CurrentSessionTransaction, params: SysDeptUpdate):
    """全量更新部门信息"""
    count = await sys_dept_service.update(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门信息更新成功'))


@router.patch('/update/status', summary='更新部门状态')
async def patch_dept_status(db: CurrentSessionTransaction, params: SysDeptPatchStatus):
    """更新部门状态"""
    count = await sys_dept_service.patch_status(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门状态更新成功'))


@router.patch('/update/parent', summary='更新部门父级')
async def patch_dept_parent(db: CurrentSessionTransaction, params: SysDeptPatchParent):
    """更新部门父级（调整部门层级）"""
    count = await sys_dept_service.patch_parent(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门父级更新成功'))


@router.patch('/update/sort', summary='更新部门排序')
async def patch_dept_sort(db: CurrentSessionTransaction, params: SysDeptPatchSort):
    """更新部门排序"""
    count = await sys_dept_service.patch_sort(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门排序更新成功'))


@router.delete('/delete', summary='删除部门')
async def delete_dept(db: CurrentSessionTransaction, dept_id: Annotated[int, Query(description='部门 ID')]):
    """删除单个部门

    注意：
    - 有子部门的部门不允许删除，请先删除子部门
    - 部门下有用户时不允许删除（待实现）
    """
    count = await sys_dept_service.delete(db=db, pk=dept_id)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门删除成功'))


@router.delete('/batch/delete', summary='批量删除部门')
async def batch_delete_dept(db: CurrentSessionTransaction, params: SysDeptBatchDelete):
    """批量删除部门

    注意：
    - 不存在的部门ID会被自动跳过
    - 有子部门的部门不会被删除
    """
    result = await sys_dept_service.batch_delete(db=db, params=params)
    deleted_count = result['deleted_count']

    return response_base.success(
        res=ResponseStatus(200, f'成功删除 {deleted_count} 个部门'),
        data=result,
    )


@router.patch('/batch/update/status', summary='批量更新部门状态')
async def batch_patch_dept_status(db: CurrentSessionTransaction, params: SysDeptBatchPatchStatus):
    """批量更新部门状态

    注意：
    - 不存在的部门ID会被自动跳过
    """
    result = await sys_dept_service.batch_patch_status(db=db, params=params)
    updated_count = result['updated_count']

    return response_base.success(
        res=ResponseStatus(200, f'成功更新 {updated_count} 个部门状态'),
        data=result,
    )
