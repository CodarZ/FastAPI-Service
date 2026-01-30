import json

from backend.core.config import settings
from backend.database.redis import redis_client


class PermissionService:
    """用户权限缓存服务"""

    async def get_user_permissions(self, user_id: int) -> set[str]:
        """获取用户权限集合"""

        # 1. Redis 缓存
        cache_key = self._get_cache_key(user_id)
        cached = await redis_client.get(cache_key)

        if cached:
            return set(json.loads(cached))

        # 2. 从数据库加载并写入缓存
        permissions = await self._load_permissions_from_db(user_id)
        if permissions:
            await redis_client.set(cache_key, json.dumps(list(permissions)))
        return permissions

    async def invalidate_user_permissions(self, user_id: int) -> None:
        """失效用户权限缓存"""
        cache_key = self._get_cache_key(user_id)
        await redis_client.delete(cache_key)

    async def invalidate_role_users_permissions(self, role_id: int) -> int:
        """失效角色下所有用户的权限缓存

        当【角色的菜单】权限变更时调用此方法。
        """
        from backend.app.admin.crud import sys_role_crud
        from backend.database.postgresql import async_session

        async with async_session() as db:
            role = await sys_role_crud.get_with_users(db, role_id)
            if not role or not role.users:
                return 0

            count = 0
            for user in role.users:
                await self.invalidate_user_permissions(user.id)
                count += 1

            return count

    async def invalidate_all_permissions(self) -> int:
        """失效所有用户权限缓存

        当【菜单】权限标识变更时调用此方法。
        """
        return await redis_client.delete_prefix(settings.RBAC_PERMISSION_REDIS_PREFIX)

    @staticmethod
    def _get_cache_key(user_id: int) -> str:
        """获取 用户权限缓存 key"""

        return f'{settings.RBAC_PERMISSION_REDIS_PREFIX}:{user_id}'

    async def _load_permissions_from_db(self, user_id: int) -> set[str]:
        """从数据库加载用户权限集合"""

        from backend.app.admin.service import sys_user_service

        return await sys_user_service.get_permissions(user_id=user_id)


permission_service = PermissionService()
