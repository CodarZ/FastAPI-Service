"""菜单服务类"""

from typing import TYPE_CHECKING

from backend.app.admin.crud import sys_menu_crud
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
    SysMenuTableTree,
    SysMenuRoute,
    SysMenuTreeNode,
    SysMenuUpdate,
)
from backend.common.exception import errors
from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.admin.model import SysMenu


class SysMenuService:
    """菜单服务类"""

    @staticmethod
    async def _get_menu_or_404(db: 'AsyncSession', pk: int) -> 'SysMenu':
        """获取菜单, 不存在则抛出 NotFoundError"""
        menu = await sys_menu_crud.get(db, pk)
        if not menu:
            raise errors.NotFoundError(msg='菜单不存在')
        return menu

    @staticmethod
    def _build_tree(menus: list['SysMenu'], parent_id: int | None = None) -> list[dict]:
        """递归构建菜单树"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = SysMenuService._build_tree(menus, menu.id)
                node = {
                    'id': menu.id,
                    'title': menu.title,
                    'type': menu.type,
                    'path': menu.path,
                    'component': menu.component,
                    'permission': menu.permission,
                    'icon': menu.icon,
                    'redirect': menu.redirect,
                    'status': menu.status,
                    'hidden': menu.hidden,
                    'keep_alive': menu.keep_alive,
                    'tab': menu.tab,
                    'breadcrumb': menu.breadcrumb,
                    'sort': menu.sort,
                    'parent_id': menu.parent_id,
                    'children': children or None,
                }
                tree.append(node)
        return tree

    @staticmethod
    def _build_option_tree(menus: list['SysMenu'], parent_id: int | None = None) -> list[dict]:
        """递归构建菜单选项树（简化版）"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = SysMenuService._build_option_tree(menus, menu.id)
                node = {
                    'id': menu.id,
                    'title': menu.title,
                    'type': menu.type,
                    'parent_id': menu.parent_id,
                    'children': children or None,
                }
                tree.append(node)
        return tree

    @staticmethod
    def _build_route_tree(menus: list['SysMenu'], parent_id: int | None = None) -> list[dict]:
        """递归构建前端路由树（只包含目录、菜单、外链、嵌入式组件，排除按钮）"""
        tree = []
        for menu in menus:
            # 只处理启用状态的菜单，排除按钮类型（type=2）
            if menu.parent_id == parent_id and menu.status == 1 and menu.type != 2:
                children = SysMenuService._build_route_tree(menus, menu.id)
                node = {
                    'id': menu.id,
                    'title': menu.title,
                    'type': menu.type,
                    'path': menu.path,
                    'component': menu.component,
                    'icon': menu.icon,
                    'redirect': menu.redirect,
                    'hidden': menu.hidden,
                    'keep_alive': menu.keep_alive,
                    'tab': menu.tab,
                    'breadcrumb': menu.breadcrumb,
                    'active_menu': menu.active_menu,
                    'children': children or None,
                }
                tree.append(node)
        return tree

    @staticmethod
    def _build_table_tree(menus: list['SysMenu'], parent_id: int | None = None) -> list[dict]:
        """递归构建菜单树形表格（用于前端表格树形展示）"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = SysMenuService._build_table_tree(menus, menu.id)
                node = {
                    'id': menu.id,
                    'title': menu.title,
                    'type': menu.type,
                    'path': menu.path,
                    'component': menu.component,
                    'permission': menu.permission,
                    'icon': menu.icon,
                    'status': menu.status,
                    'hidden': menu.hidden,
                    'sort': menu.sort,
                    'parent_id': menu.parent_id,
                    'created_time': menu.created_time,
                    'children': children or None,
                }
                tree.append(node)
        return tree

    @staticmethod
    async def get_menu_info(*, db: 'AsyncSession', pk: int) -> SysMenuInfo:
        """获取菜单信息"""
        menu = await SysMenuService._get_menu_or_404(db, pk)
        return SysMenuInfo.model_validate(menu)

    @staticmethod
    async def get_menu_detail(*, db: 'AsyncSession', pk: int) -> SysMenuDetail:
        """获取菜单详情"""
        menu = await SysMenuService._get_menu_or_404(db, pk)
        return SysMenuDetail.model_validate(menu)

    @staticmethod
    async def get_list(*, params: SysMenuFilter) -> list[SysMenuListItem]:
        """获取菜单列表（扁平表格展示）"""
        async with async_session.begin() as db:
            stmt = await sys_menu_crud.get_list_select(params)
            result = await db.scalars(stmt)
            menus = result.all()
            # 在 session 内完成序列化, 避免 DetachedInstanceError
            return [SysMenuListItem.model_validate(menu) for menu in menus]

    @staticmethod
    async def get_tree() -> list[SysMenuTreeNode]:
        """获取菜单树（树形结构展示）"""
        async with async_session.begin() as db:
            menus = await sys_menu_crud.get_all(db)
            tree_data = SysMenuService._build_tree(menus)
            return [SysMenuTreeNode.model_validate(node) for node in tree_data]

    @staticmethod
    async def get_options() -> list[SysMenuOption]:
        """获取菜单选项列表（用于下拉选择器）"""
        async with async_session.begin() as db:
            menus = await sys_menu_crud.get_all(db)
            return [SysMenuOption.model_validate(menu) for menu in menus]

    @staticmethod
    async def get_option_tree() -> list[SysMenuOptionTree]:
        """获取菜单选项树（用于树形选择器）"""
        async with async_session.begin() as db:
            menus = await sys_menu_crud.get_all(db)
            tree_data = SysMenuService._build_option_tree(menus)
            return [SysMenuOptionTree.model_validate(node) for node in tree_data]

    @staticmethod
    async def get_routes() -> list[SysMenuRoute]:
        """获取前端路由配置"""
        async with async_session.begin() as db:
            menus = await sys_menu_crud.get_by_status(db, status=1)
            route_data = SysMenuService._build_route_tree(menus)
            return [SysMenuRoute.model_validate(node) for node in route_data]

    @staticmethod
    async def get_table_tree(*, params: SysMenuFilter) -> list[SysMenuTableTree]:
        """获取菜单树形表格（树形表格展示）"""
        async with async_session.begin() as db:
            stmt = await sys_menu_crud.get_list_select(params)
            result = await db.scalars(stmt)
            menus = list(result.all())
            tree_data = SysMenuService._build_table_tree(menus)
            return [SysMenuTableTree.model_validate(node) for node in tree_data]

    @staticmethod
    async def create(*, db: 'AsyncSession', params: SysMenuCreate) -> None:
        """创建新菜单"""
        # 校验上级菜单是否存在
        if params.parent_id and not await sys_menu_crud.check_parent_exists(db, params.parent_id):
            raise errors.NotFoundError(msg='上级菜单不存在')

        # 校验同级菜单标题是否重复
        if not await sys_menu_crud.check_title_unique(db, params.title, params.parent_id):
            raise errors.ConflictError(msg='同级菜单标题已存在')

        # 校验权限标识是否重复（如果提供了权限标识）
        if params.permission and not await sys_menu_crud.check_permission_unique(db, params.permission):
            raise errors.ConflictError(msg='权限标识已存在')

        await sys_menu_crud.create(db, params)

    @staticmethod
    async def update(*, db: 'AsyncSession', pk: int, params: SysMenuUpdate) -> int:
        """更新菜单信息"""
        # 检查菜单是否存在
        await SysMenuService._get_menu_or_404(db, pk)

        # 校验上级菜单是否存在
        if params.parent_id:
            if not await sys_menu_crud.check_parent_exists(db, params.parent_id):
                raise errors.NotFoundError(msg='上级菜单不存在')

            # 不允许将菜单移动到自己或自己的子孙菜单下
            if params.parent_id == pk:
                raise errors.ForbiddenError(msg='不能将菜单移动到自己下面')

            # 检查是否移动到自己的子孙菜单下
            children_ids = await sys_menu_crud.get_all_children_ids(db, pk)
            if params.parent_id in children_ids:
                raise errors.ForbiddenError(msg='不能将菜单移动到自己的子菜单下')

        # 校验同级菜单标题是否重复
        if not await sys_menu_crud.check_title_unique(db, params.title, params.parent_id, exclude_id=pk):
            raise errors.ConflictError(msg='同级菜单标题已存在')

        # 校验权限标识是否重复（如果提供了权限标识）
        if params.permission and not await sys_menu_crud.check_permission_unique(db, params.permission, exclude_id=pk):
            raise errors.ConflictError(msg='权限标识已存在')

        return await sys_menu_crud.update(db, pk, params)

    @staticmethod
    async def patch_status(*, db: 'AsyncSession', pk: int, params: SysMenuPatchStatus) -> int:
        """修改菜单状态"""
        await SysMenuService._get_menu_or_404(db, pk)
        return await sys_menu_crud.update_by_column(db, pk, 'status', params.status)

    @staticmethod
    async def patch_hidden(*, db: 'AsyncSession', pk: int, params: SysMenuPatchHidden) -> int:
        """修改菜单隐藏状态"""
        await SysMenuService._get_menu_or_404(db, pk)
        return await sys_menu_crud.update_by_column(db, pk, 'hidden', params.hidden)

    @staticmethod
    async def patch_sort(*, db: 'AsyncSession', pk: int, params: SysMenuPatchSort) -> int:
        """修改菜单排序"""
        await SysMenuService._get_menu_or_404(db, pk)
        return await sys_menu_crud.update_by_column(db, pk, 'sort', params.sort)

    @staticmethod
    async def patch_parent(*, db: 'AsyncSession', pk: int, params: SysMenuPatchParent) -> int:
        """修改菜单父级"""
        await SysMenuService._get_menu_or_404(db, pk)

        # 校验上级菜单是否存在
        if params.parent_id:
            if not await sys_menu_crud.check_parent_exists(db, params.parent_id):
                raise errors.NotFoundError(msg='上级菜单不存在')

            # 不允许将菜单移动到自己或自己的子孙菜单下
            if params.parent_id == pk:
                raise errors.ForbiddenError(msg='不能将菜单移动到自己下面')

            # 检查是否移动到自己的子孙菜单下
            children_ids = await sys_menu_crud.get_all_children_ids(db, pk)
            if params.parent_id in children_ids:
                raise errors.ForbiddenError(msg='不能将菜单移动到自己的子菜单下')

        return await sys_menu_crud.update_by_column(db, pk, 'parent_id', params.parent_id)

    @staticmethod
    async def batch_update_status(*, db: 'AsyncSession', params: SysMenuBatchPatchStatus) -> int:
        """批量修改菜单状态"""
        # 验证菜单是否存在
        existing_ids = await sys_menu_crud.get_existing_ids(db, params.menu_ids)
        if len(existing_ids) != len(params.menu_ids):
            raise errors.NotFoundError(msg='部分菜单不存在')

        return await sys_menu_crud.batch_update_status(db, params.menu_ids, params.status)

    @staticmethod
    async def delete(*, db: 'AsyncSession', pk: int) -> int:
        """删除菜单"""
        await SysMenuService._get_menu_or_404(db, pk)

        # 检查是否有子菜单
        if await sys_menu_crud.check_has_children(db, pk):
            raise errors.ForbiddenError(msg='该菜单存在子菜单，无法删除')

        return await sys_menu_crud.delete(db, pk)

    @staticmethod
    async def batch_delete(*, db: 'AsyncSession', params: SysMenuBatchDelete) -> int:
        """批量删除菜单"""
        # 验证菜单是否存在
        existing_ids = await sys_menu_crud.get_existing_ids(db, params.menu_ids)
        if len(existing_ids) != len(params.menu_ids):
            raise errors.NotFoundError(msg='部分菜单不存在')

        # 检查每个菜单是否有子菜单
        for menu_id in params.menu_ids:
            if await sys_menu_crud.check_has_children(db, menu_id):
                raise errors.ForbiddenError(msg=f'菜单 {menu_id} 存在子菜单，无法删除')

        return await sys_menu_crud.batch_delete(db, params.menu_ids)


sys_menu_service = SysMenuService()
