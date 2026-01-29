from typing import TYPE_CHECKING, Any

from backend.app.admin.crud import sys_dept_crud, sys_user_crud
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
from backend.common.exception import errors
from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SysDeptService:
    """部门服务类"""

    @staticmethod
    async def _get_dept_or_404(db: AsyncSession, pk: int):
        """获取部门, 不存在则抛出 NotFoundError"""
        dept = await sys_dept_crud.get(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='部门不存在')
        return dept

    @staticmethod
    async def _validate_parent(db: AsyncSession, parent_id: int | None, current_id: int | None = None):
        """验证父级部门有效性

        Args:
            db: 数据库会话
            parent_id: 父级部门 ID
            current_id: 当前部门 ID（更新时使用, 用于防止循环引用）
        """
        if parent_id is None:
            return

        # 验证父级部门存在
        parent = await sys_dept_crud.get(db, parent_id)
        if not parent:
            raise errors.NotFoundError(msg='上级部门不存在')

        # 更新时检查循环引用：不能将自己或子部门设为父级
        if current_id is not None:
            if parent_id == current_id:
                raise errors.RequestError(msg='上级部门不能是自己')

            # 检查 parent_id 是否是 current_id 的子孙节点
            if await SysDeptService._is_descendant(db, parent_id, current_id):
                raise errors.RequestError(msg='上级部门不能是自己的子部门')

    @staticmethod
    async def _is_descendant(db: AsyncSession, check_id: int, ancestor_id: int) -> bool:
        """检查是否是子孙节点"""
        dept = await sys_dept_crud.get(db, check_id)
        while dept and dept.parent_id is not None:
            if dept.parent_id == ancestor_id:
                return True
            dept = await sys_dept_crud.get(db, dept.parent_id)
        return False

    @staticmethod
    async def get_dept_info(*, db: AsyncSession, pk: int) -> SysDeptInfo:
        """获取部门信息"""
        dept = await SysDeptService._get_dept_or_404(db, pk)
        return SysDeptInfo.model_validate(dept)

    @staticmethod
    async def get_dept_detail(*, db: AsyncSession, pk: int) -> SysDeptDetail:
        """获取部门详情"""
        dept = await SysDeptService._get_dept_or_404(db, pk)
        return SysDeptDetail.model_validate(dept)

    @staticmethod
    async def get_list(*, params: SysDeptFilter) -> list[SysDeptListItem]:
        """获取部门列表（扁平结构）"""
        async with async_session.begin() as db:
            stmt = await sys_dept_crud.get_list_select(params)
            result = await db.scalars(stmt)
            depts = result.all()
            # 在 session 内完成序列化，避免 DetachedInstanceError
            return [SysDeptListItem.model_validate(dept) for dept in depts]

    @staticmethod
    async def get_tree(*, params: SysDeptFilter) -> list[SysDeptTreeNode]:
        """获取部门树形结构

        策略：全量查询节点并在内存中组装 children, 避免 relationship 递归加载
        """
        async with async_session.begin() as db:
            stmt = await sys_dept_crud.get_list_select(params)
            result = await db.scalars(stmt)
            depts = result.all()

            # 转换为 Schema 并构建树（确保 children 初始化为空列表，便于 append）
            nodes = []
            for dept in depts:
                node = SysDeptTreeNode.model_validate(dept)
                if node.children is None:
                    node.children = []
                nodes.append(node)
            return SysDeptService._build_tree(nodes)

    @staticmethod
    async def get_option_tree() -> list[SysDeptOptionTree]:
        """获取部门选项树（用于下拉选择器）

        只返回启用状态的部门, 仅包含 id、title、parent_id
        """
        async with async_session.begin() as db:
            from backend.app.admin.model import SysDept
            from sqlalchemy import select

            stmt = (
                select(SysDept.id, SysDept.title, SysDept.parent_id)
                .where(SysDept.status == 1)
                .order_by(SysDept.sort, SysDept.id)
            )
            result = await db.execute(stmt)
            rows = result.all()

            # 转换为 Schema 并构建树（初始化 children 为空列表，便于 append）
            nodes = [SysDeptOptionTree(id=r.id, title=r.title, parent_id=r.parent_id, children=[]) for r in rows]
            return SysDeptService._build_tree(nodes)

    @staticmethod
    def _build_tree(nodes: list) -> list:
        """构建树形结构

        Args:
            nodes: 扁平节点列表（必须有 id、parent_id、children 属性）

        Returns:
            根节点列表（parent_id 为 None 的节点）
        """
        if not nodes:
            return []

        # 构建 id -> node 映射
        node_map: dict[int, Any] = {node.id: node for node in nodes}

        # 构建树
        roots = []
        for node in nodes:
            if node.parent_id is None or node.parent_id not in node_map:
                roots.append(node)
            else:
                parent = node_map.get(node.parent_id)
                if parent:
                    parent.children.append(node)

        # 将空的 children 列表替换为 None
        def set_empty_children_to_none(node):
            if not node.children:
                node.children = None
            else:
                for child in node.children:
                    set_empty_children_to_none(child)

        for root in roots:
            set_empty_children_to_none(root)

        return roots

    @staticmethod
    async def create(*, db: AsyncSession, params: SysDeptCreate):
        """创建部门"""
        # 校验部门名称是否重复
        existing = await sys_dept_crud.get_by_column(db, 'title', params.title)
        if existing:
            raise errors.ConflictError(msg='部门名称已存在')

        # 校验上级部门
        await SysDeptService._validate_parent(db, params.parent_id)

        await sys_dept_crud.create(db, params)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, params: SysDeptUpdate) -> int:
        """全量更新部门信息"""
        dept = await SysDeptService._get_dept_or_404(db, pk)

        # 校验部门名称是否重复（排除当前部门）
        if params.title != dept.title:
            existing = await sys_dept_crud.get_by_column(db, 'title', params.title)
            if existing:
                raise errors.ConflictError(msg='部门名称已存在')

        # 校验上级部门（防止循环引用）
        await SysDeptService._validate_parent(db, params.parent_id, current_id=pk)

        return await sys_dept_crud.update(db, pk, params)

    @staticmethod
    async def patch_status(*, db: AsyncSession, pk: int, params: SysDeptPatchStatus) -> int:
        """更新部门状态"""
        await SysDeptService._get_dept_or_404(db, pk)
        return await sys_dept_crud.update_by_column(db, pk, 'status', params.status)

    @staticmethod
    async def patch_parent(*, db: AsyncSession, pk: int, params: SysDeptPatchParent) -> int:
        """更新部门父级"""
        await SysDeptService._get_dept_or_404(db, pk)

        # 校验上级部门（防止循环引用）
        await SysDeptService._validate_parent(db, params.parent_id, current_id=pk)

        return await sys_dept_crud.update_by_column(db, pk, 'parent_id', params.parent_id)

    @staticmethod
    async def patch_sort(*, db: AsyncSession, pk: int, params: SysDeptPatchSort) -> int:
        """更新部门排序"""
        await SysDeptService._get_dept_or_404(db, pk)
        return await sys_dept_crud.update_by_column(db, pk, 'sort', params.sort)

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """删除部门

        注意：由于外键配置了 ondelete='CASCADE', 删除部门会级联删除所有子部门
        """
        dept = await sys_dept_crud.get_with_children(db, pk)
        if not dept:
            raise errors.NotFoundError(msg='部门不存在')

        # 如果有子部门, 提示用户
        if dept.children:
            raise errors.RequestError(msg='该部门下存在子部门, 请先删除子部门')

        # 检查该部门下是否有用户
        if await sys_user_crud.has_users_in_dept(db, pk):
            raise errors.RequestError(msg='该部门下存在用户, 请先移除用户')

        return await sys_dept_crud.delete(db, pk=pk)

    @staticmethod
    async def batch_delete(*, db: AsyncSession, params: SysDeptBatchDelete) -> dict[str, int | list[int]]:
        """批量删除部门

        处理逻辑：
            1. 校验部门是否存在, 不存在的自动跳过
            2. 过滤掉有子部门的部门（不允许批量删除有子部门的）
            3. 对剩余有效部门执行批量删除

        Returns:
            包含执行结果的字典：
            - deleted_count: 实际删除的数量
            - skipped_not_found: 不存在的部门ID列表
            - skipped_has_children: 有子部门的部门ID列表
        """
        dept_ids = params.dept_ids

        # 1. 获取实际存在的部门ID
        existing_ids = await sys_dept_crud.get_existing_ids(db, dept_ids)
        not_found_ids = list(set(dept_ids) - set(existing_ids))

        # 2. 筛选出有子部门的部门ID
        has_children_ids = []
        deletable_ids = []

        for dept_id in existing_ids:
            dept = await sys_dept_crud.get_with_children(db, dept_id)
            if dept and dept.children:
                has_children_ids.append(dept_id)
            else:
                deletable_ids.append(dept_id)

        # 3. 执行批量删除
        deleted_count = await sys_dept_crud.batch_delete(db, deletable_ids)

        return {
            'deleted_count': deleted_count,
            'skipped_not_found': not_found_ids,
            'skipped_has_children': has_children_ids,
        }

    @staticmethod
    async def batch_patch_status(*, db: AsyncSession, params: SysDeptBatchPatchStatus) -> dict[str, int | list[int]]:
        """批量更新部门状态

        处理逻辑：
            1. 校验部门是否存在, 不存在的自动跳过
            2. 对存在的部门执行批量更新

        Returns:
            包含执行结果的字典：
            - updated_count: 实际更新的数量
            - skipped_not_found: 不存在的部门ID列表
        """
        dept_ids = params.dept_ids
        status = params.status

        # 1. 获取实际存在的部门ID
        existing_ids = await sys_dept_crud.get_existing_ids(db, dept_ids)
        not_found_ids = list(set(dept_ids) - set(existing_ids))

        # 2. 执行批量更新
        updated_count = await sys_dept_crud.batch_update_status(db, existing_ids, status)

        return {
            'updated_count': updated_count,
            'skipped_not_found': not_found_ids,
        }


sys_dept_service = SysDeptService()
