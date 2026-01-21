from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.admin.schema import (
    SysDeptBatchDelete,
    SysDeptBatchPatchStatus,
    SysDeptCreate,
    SysDeptDetail,
    SysDeptFilter,
    SysDeptInfo,
    SysDeptListItem,
    SysDeptOption,
    SysDeptOptionTree,
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
    data = await sys_dept_service.get_dept_info(db=db, pk=dept_id)
    return response_base.success(data=data)


@router.get('/detail', summary='获取部门详情', response_model=ResponseSchemaModel[SysDeptDetail])
async def get_dept_detail(db: CurrentSession, dept_id: Annotated[int, Query(description='部门 ID')]):
    data = await sys_dept_service.get_dept_detail(db=db, pk=dept_id)
    return response_base.success(data=data)


@router.get('/option', summary='获取部门下拉列表', response_model=ResponseSchemaModel[list[SysDeptOption]])
async def get_dept_option(title: str = Query(None, description='部门名称')):
    data = await sys_dept_service.get_list(params=SysDeptFilter(status=1, title=title))
    return response_base.success(data=data)


@router.get('/option/tree', summary='获取部门树形选项', response_model=ResponseSchemaModel[list[SysDeptOptionTree]])
async def get_dept_option_tree(
    title: str = Query(None, description='部门名称'), status: int = Query(1, description='状态')
):
    params = SysDeptFilter(title=title, status=status)
    data = await sys_dept_service.get_tree(params=params)
    return response_base.success(data=data)


@router.get('/tree', summary='获取部门树形列表', response_model=ResponseSchemaModel[list[SysDeptTreeNode]])
async def get_dept_tree(title: str = Query(None, description='部门名称'), status: int = Query(1, description='状态')):
    # 默认只查询启用状态的部门，用于下拉树
    params = SysDeptFilter(title=title, status=status)
    data = await sys_dept_service.get_tree(params=params)
    return response_base.success(data=data)


@router.get('/list', summary='获取部门列表', response_model=ResponseSchemaModel[list[SysDeptListItem]])
async def get_dept_list(params: Annotated[SysDeptFilter, Query()]):
    data = await sys_dept_service.get_list(params=params)
    return response_base.success(data=data)


@router.put('/update', summary='更新部门信息')
async def update_dept(db: CurrentSessionTransaction, params: SysDeptUpdate):
    count = await sys_dept_service.update(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门信息更新成功'))


@router.patch('/update/status', summary='更新部门状态')
async def patch_dept_status(db: CurrentSessionTransaction, params: SysDeptPatchStatus):
    count = await sys_dept_service.patch_status(db=db, pk=params.id, params=params)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门状态更新成功'))


@router.delete('/delete', summary='删除部门')
async def delete_dept(db: CurrentSessionTransaction, dept_id: Annotated[int, Query(description='部门 ID')]):
    count = await sys_dept_service.delete(db=db, pk=dept_id)
    if count == 0:
        return response_base.fail()
    return response_base.success(res=ResponseStatus(200, '部门删除成功'))


@router.delete('/batch/delete', summary='批量删除部门')
async def batch_delete_dept(db: CurrentSessionTransaction, params: SysDeptBatchDelete):
    """批量删除部门

    注意：
    - 不存在的部门ID会被自动跳过
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

    return response_base.success(res=ResponseStatus(200, f'成功更新 {updated_count} 个部门状态'), data=result)
