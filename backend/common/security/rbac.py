"""RBAC 权限校验模块

提供基于角色的访问控制（RBAC）权限校验功能。
支持 AND/OR/NOT 逻辑操作符和正则白名单路径匹配。
"""

import re

from typing import Any, Callable

from fastapi import APIRouter, Depends, Request
from fastapi.params import Depends as DependsParams

from backend.common.enum.custom import RBACLogical
from backend.common.exception import errors
from backend.common.request.context import ctx
from backend.common.security.jwt import DependsJWTAuth
from backend.common.security.permission import permission_service
from backend.core.config import settings


class RBACChecker:
    """RBAC 权限检查器"""

    # 编译后的白名单正则缓存
    _white_list_patterns: list[re.Pattern] | None = None

    def __init__(self, *permissions: str, logical: RBACLogical = RBACLogical.AND):
        """初始化 RBAC 权限检查器

        Args:
            permissions: 需要的权限标识，如 'sys:user:add', 'sys:user:delete'
            logical: 逻辑关系, 如： AND/OR/NOT
        """

        self.permissions = permissions
        self.logical = RBACLogical(logical.upper())

    async def __call__(self, request: Request, _token: str = DependsJWTAuth) -> bool:
        """权限检查"""

        # 1. 检查 路径白名单
        if self.is_path_in_white_list(request.url.path):
            return True

        # 2. 检查 指定权限
        if not self.permissions:
            return True

        # 3. 检查 权限标识白名单
        if all(self.is_permission_in_white_list(p) for p in self.permissions):
            return True

        user = request.user

        # 4. 跳过 超级管理员
        if hasattr(user, 'is_superuser') and user.is_superuser:
            return True

        # 5.1 获取 用户所有权限 all_permissions
        all_permissions = await self._get_user_all_permissions(request, user)

        # 5.2 校验权限
        has_permission = self._check_permissions(all_permissions)

        if not has_permission:
            missing = set(self.permissions) - all_permissions
            msg = settings.ENVIRONMENT != 'production' and f'缺少权限: {missing}' or '权限不足'
            raise errors.ForbiddenError(msg=msg)

        return True

    @classmethod
    def is_path_in_white_list(cls, path: str) -> bool:
        """检查 路径白名单"""

        patterns = cls._get_white_list_patterns()
        return any(pattern.search(path) for pattern in patterns)

    @staticmethod
    def is_permission_in_white_list(permission: str) -> bool:
        """检查 权限标识白名单"""

        return permission in settings.RBAC_WHITE_PERMISSION

    @classmethod
    def _get_white_list_patterns(cls) -> list[re.Pattern]:
        """获取编译后的白名单正则表达式"""

        if cls._white_list_patterns is None:
            cls._white_list_patterns = [re.compile(pattern) for pattern in settings.RBAC_WHITE_PATTERNS]
        return cls._white_list_patterns

    async def _get_user_all_permissions(self, request: Request, user) -> set[str]:
        """获取用户权限集合"""

        if ctx.permissions is not None:
            return ctx.permissions

        # 从 Permission Service 获取（会自动使用缓存, 存取数据库）
        user_id = user.id if hasattr(user, 'id') else getattr(user, 'identity', None)
        if user_id is None:
            return set()

        permissions = await permission_service.get_user_permissions(int(user_id))

        # 存储到 ctx 供后续使用
        ctx.permissions = permissions

        return permissions

    def _check_permissions(self, all_permissions: set[str]) -> bool:
        """检查权限 (根据逻辑操作符)"""

        if self.logical == RBACLogical.AND:
            return all(p in all_permissions for p in self.permissions)
        if self.logical == RBACLogical.OR:
            return any(p in all_permissions for p in self.permissions)
        if self.logical == RBACLogical.NOT:
            return all(p not in all_permissions for p in self.permissions)
        return False


def DependsRBAC(*permissions: str, logical: RBACLogical = RBACLogical.AND):
    """创建 RBAC 权限依赖"""

    return Depends(RBACChecker(*permissions, logical=logical))


class RBACRouter(APIRouter):
    """自动添加权限文档的 API 路由"""

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        **kwargs: Any,
    ) -> None:
        """重写添加路由方法，自动处理权限文档"""
        dependencies = kwargs.get('dependencies') or []

        # 提取 RBAC 依赖中的权限信息
        permissions_doc = []
        for dep in dependencies:
            if (
                isinstance(dep, DependsParams)
                and hasattr(dep, 'dependency')
                and isinstance(dep.dependency, RBACChecker)
            ):
                checker: RBACChecker = dep.dependency
                perms = [f'`{p}`' for p in checker.permissions]
                if perms:
                    logic_str = f' ({checker.logical.value})' if len(perms) > 1 else ''
                    permissions_doc.append(f'{", ".join(perms)}{logic_str}')

        # 如果有权限要求，添加到 summary 和 description 中
        if permissions_doc:
            # 添加到 Summary
            summary = kwargs.get('summary') or endpoint.__name__.replace('_', ' ').title()

            # 格式化权限字符串（去掉反引号用于 Summary）
            summary_perms = [p.replace('`', '') for p in permissions_doc]
            perm_str = ', '.join(summary_perms)

            kwargs['summary'] = f'{summary}, {perm_str}'

        super().add_api_route(path, endpoint, **kwargs)
