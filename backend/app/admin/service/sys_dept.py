from backend.app.admin.schema import SysDeptBatchDelete
from backend.app.admin.schema import SysDeptBatchPatchStatus
from backend.app.admin.schema import SysDeptPatchStatus
from backend.app.admin.schema import SysDeptUpdate
from backend.app.admin.schema import SysDeptCreate
from typing import TYPE_CHECKING
from backend.app.admin.schema import SysDeptFilter
from backend.app.admin.schema import SysDeptDetail
from backend.app.admin.schema import SysDeptInfo
from backend.app.admin.model import SysDept
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.admin.crud import sys_dept_crud
from backend.common.exception import errors
from backend.app.admin.schema import SysDeptTreeNode
from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SysDeptService:
    """部门服务类"""

    @staticmethod
    async def _get_dept_or_404(db: AsyncSession, pk: int):
        dept = await sys_dept_crud.get(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='部门不存在')
        return dept

    @staticmethod
    async def _get_dept_with_parent_or_404(db: AsyncSession, pk: int):
        """获取部门（包含父部门信息），不存在则抛出 404

        使用此方法当需要访问 dept.parent 时，避免 lazy='noload' 导致的 None
        """
        dept = await sys_dept_crud.get_with_parent(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='部门不存在')
        return dept

    @staticmethod
    async def get_dept_info(*, db: AsyncSession, pk: int) -> SysDeptInfo:
        """获取部门信息"""
        dept = await SysDeptService._get_dept_with_parent_or_404(db, pk)
        return SysDeptInfo.model_validate(dept)

    @staticmethod
    async def get_dept_detail(*, db: AsyncSession, pk: int) -> SysDeptDetail:
        """获取部门详情"""
        dept = await SysDeptService._get_dept_with_parent_or_404(db, pk)
        return SysDeptDetail.model_validate(dept)

    @staticmethod
    async def get_list(*, params: SysDeptFilter):
        """获取部门列表"""
        async with async_session.begin() as db:
            stmt = await sys_dept_crud.get_list_select(params)
            result = await db.scalars(stmt)
            return result.all()

    @staticmethod
    async def get_tree(*, params: SysDeptFilter) -> list[SysDeptTreeNode]:
        """获取部门树形列表"""
        async with async_session.begin() as db:
            stmt = await sys_dept_crud.get_list_select(params)
            result = await db.scalars(stmt)
            dept_list = result.all()

            # 转换为 TreeNode Schema
            nodes = [SysDeptTreeNode.model_validate(dept) for dept in dept_list]

            # TODO 构建树形结构工具函数
            tree_nodes = []
            node_map = {node.id: node for node in nodes}

            for node in nodes:
                if node.parent_id is None or node.parent_id not in node_map:
                    tree_nodes.append(node)
                else:
                    parent = node_map[node.parent_id]
                    parent.children.append(node)

            return tree_nodes

    async def create(self, db: AsyncSession, params: SysDeptCreate) -> SysDept:
        """创建部门"""

        # TODO 校验同一部门下，不应存在相同的子部门 ，而不是全局唯一
        dept = await sys_dept_crud.get_by_column(db, 'title', params.title)
        if dept:
            raise errors.ConflictError(msg='部门名称已存在')
        if params.parent_id is not None:
            parent = await sys_dept_crud.get(db, params.parent_id)
            if not parent:
                raise errors.NotFoundError(msg='上级部门不存在')

        return await sys_dept_crud.create(db, params)

    async def update(self, db: AsyncSession, pk: int, params: SysDeptUpdate) -> int:
        """全量更新部门信息"""
        dept = await sys_dept_crud.get(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='部门不存在')

        # TODO 校验同一部门下，不应存在相同的子部门 ，而不是全局唯一
        if params.title != dept.title:
            dept = await sys_dept_crud.get_by_column(db, 'title', params.title)
            if dept:
                raise errors.ConflictError(msg='部门名称已存在')

        return await sys_dept_crud.update(db, pk, params)

    async def patch_status(self, db: AsyncSession, pk: int, params: SysDeptPatchStatus) -> int:
        """更新部门状态"""
        await SysDeptService._get_dept_or_404(db, pk)
        return await sys_dept_crud.update_by_column(db, pk, 'status', params.status)

    async def batch_patch_status(self, db: AsyncSession, params: SysDeptBatchPatchStatus) -> int:
        """批量更新部门状态

        处理逻辑：
            1. 校验部门是否存在，不存在的自动跳过
            2. 对剩余有效部门执行批量更新

        Returns:
            包含执行结果的字典：
            - updated_count: 实际更新的数量
            - skipped_not_found: 不存在的部门ID列表
        """
        dept_ids = params.dept_ids
        status = params.status

        existing_ids = await sys_dept_crud.get_existing_ids(db, dept_ids)
        not_found_ids = list(set(dept_ids) - set(existing_ids))

        updated_count = await sys_dept_crud.batch_update_status(db, existing_ids, status)

        return {
            'updated_count': updated_count,
            'skipped_not_found': not_found_ids,
        }

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """删除部门"""
        await SysDeptService._get_dept_or_404(db, pk)

        return await sys_dept_crud.delete(db, pk)

    @staticmethod
    async def batch_delete(*, db: AsyncSession, params: SysDeptBatchDelete) -> dict[str, int | list[int]]:
        """批量删除部门

        处理逻辑：
            1. 校验部门是否存在，不存在的自动跳过
            2. 对剩余有效部门执行批量删除

        Returns:
            包含执行结果的字典：
            - deleted_count: 实际删除的数量
            - skipped_not_found: 不存在的部门ID列表
        """
        dept_ids = params.dept_ids

        existing_ids = await sys_dept_crud.get_existing_ids(db, dept_ids)
        not_found_ids = list(set(dept_ids) - set(existing_ids))

        deleted_count = await sys_dept_crud.batch_delete(db, existing_ids)

        return {
            'deleted_count': deleted_count,
            'skipped_not_found': not_found_ids,
        }


sys_dept_service = SysDeptService()
