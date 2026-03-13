from __future__ import annotations

from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING, Any

from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from backend.core.config import settings

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


__all__ = ['redis_client']

# SCAN 每批建议返回的数量，实测在百万级 key 场景下最优
_SCAN_COUNT = 200


class RedisClient(Redis):
    """异步 Redis 客户端."""

    def __init__(self) -> None:
        """初始化 Redis 连接参数."""
        super().__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD.get_secret_value(),
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            socket_connect_timeout=settings.REDIS_TIMEOUT,
            socket_keepalive=True,  # TCP keepalive，防止长连接被防火墙断开
            health_check_interval=30,  # 后台健康检查周期（秒）
            decode_responses=True,  # 响应自动解码为 str（UTF-8）
            retry_on_timeout=True,  # 超时后自动重试一次
            retry_on_error=[ConnectionError, TimeoutError],  # 触发重试的异常类型
        )

    async def open(self) -> None:
        """建立 Redis 连接，并验证连通性."""
        try:
            self.ping()
            logger.info('✅ Redis 连接成功 [{}:{}]', settings.REDIS_HOST, settings.REDIS_PORT)
        except RedisError as e:
            logger.error('❌ Redis 连接失败: {}', e)
            raise

    async def get_keys(self, prefix: str, *, count: int = _SCAN_COUNT) -> list[str]:
        """获取匹配指定前缀的所有 Key."""
        pattern = f'{prefix}:*' if not prefix.endswith(':') else f'{prefix}*'
        return [key async for key in self.scan_iter(pattern, count=count)]

    async def delete_keys(self, prefix: str, *, count: int = _SCAN_COUNT) -> int:
        """删除匹配指定前缀的所有 Key."""
        keys = await self.get_keys(prefix, count=count)
        if not keys:
            return 0

        # 使用 pipeline 批量删除，一次网络往返搞定
        async with self.pipeline(transaction=False) as pipe:
            for key in keys:
                pipe.delete(key)
            results: list[int] = await pipe.execute()

        deleted = sum(results)
        logger.debug('删除前缀 [{}] 下共 {} 个 Key', prefix, deleted)
        return deleted

    async def get_or_init(self, key: str, default: Any, *, ex: int | None = None) -> str:
        """读取 Key, 若不存在则写入默认值并返回."""
        value = await self.get(key)
        if value is None:
            value = str(default)
            await self.set(key, value, ex=ex)
        return value

    async def set_with_ttl(self, key: str, value: Any, *, ex: int) -> bool:
        """写入键值对并设置过期时间（秒）."""
        return bool(await self.set(key, str(value), ex=ex))

    async def exists_key(self, *keys: str) -> bool:
        """检测一个或多个 Key 是否存在."""
        count = await self.exists(*keys)
        return count == len(keys)

    async def get_ttl(self, key: str) -> int:
        """获取 Key 的剩余生存时间（秒）."""
        return await self.ttl(key)

    async def refresh_ttl(self, key: str, ex: int) -> bool:
        """刷新 Key 的过期时间（秒）."""
        return bool(await self.expire(key, ex))

    @asynccontextmanager
    async def lock_context(
        self,
        name: str,
        *,
        lock_timeout: float = 10.0,
        blocking_timeout: float | None = None,
    ) -> AsyncIterator[None]:
        """获取分布式锁的上下文管理器.

        基于 redis-py 内置的 `Lock`，使用 SET NX + Lua 脚本保证原子性，
        支持自动续期（看门狗机制由上层业务决定是否开启）。

        Args:
            name:             锁名称，建议携带业务前缀，如 `'fs:lock:order:123'`。
            lock_timeout:     锁的最大持有时间（秒），超时后自动释放，防止死锁。
            blocking_timeout: 等待锁的最大时间（秒），`None` 表示不等待直接失败。

        Raises:
            redis.exceptions.LockNotOwnedError: 锁已被其他持有者占用且 blocking_timeout 超时。

        Examples::

            async with redis_client.lock_context('fs:lock:pay:42', timeout=5):
                # 临界区业务逻辑
                ...
        """
        lock = self.lock(name, timeout=lock_timeout, blocking_timeout=blocking_timeout)
        acquired = await lock.acquire()
        if not acquired:
            # blocking_timeout=None 时到达此处意味着立即获锁失败
            raise RedisError(f'获取分布式锁失败: {name}')
        try:
            yield
        finally:
            # 锁 TTL 已过期被服务端自动释放时，release 会抛 LockNotOwnedError，静默处理即可
            with suppress(RedisError):
                await lock.release()

    async def incr_with_expire(self, key: str, *, ex: int) -> int:
        """原子自增，并在首次创建时设置过期时间.

        典型应用：请求限流计数、登录失败次数统计。

        使用 pipeline 将 `INCR` + `EXPIRE` 合并为一次网络调用；
        `INCR` 的原子性由 Redis 服务端保证，`EXPIRE` 仅在首次（值为 1）时需要，
        但为简化代码，每次均发送 `EXPIRE`（成本极低）。

        Args:
            key: Redis Key（计数器键名）。
            ex:  过期窗口大小（秒），如限流窗口 60 秒。

        Returns:
            自增后的计数值。

        Examples::

            # 场景 A：API 限流，每个 IP 每分钟最多 100 次请求
            async def check_rate_limit(ip: str) -> bool:
                key = f'ratelimit:{ip}'
                count = await redis_client.incr_with_expire(key, ex=60)
                return count <= 100  # False 时应返回 429


            # 场景 B：登录失败保护，连续失败 5 次后锁定账号 10 分钟
            async def on_login_fail(username: str) -> None:
                key = f'loginfail:{username}'
                fails = await redis_client.incr_with_expire(key, ex=600)
                if fails >= 5:
                    raise TooManyRequestsError('账号已临时锁定，请 10 分钟后重试')
        """
        async with self.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, ex)
            result: list[Any] = await pipe.execute()
        return int(result[0])

    async def hset_with_expire(self, name: str, mapping: dict[str, Any], *, ex: int) -> None:
        """批量写入 Hash 字段并设置过期时间（原子操作）.

        Note:
            若权限系统只有「有/没有」两种状态，推荐用 Redis Set（``sadd`` / ``sismember``）
            代替 Hash，语义更清晰且无需约定 ``'1'`` / ``'0'``。
            本方法适用于字段值本身有意义的 Hash 结构（如 Session 附加信息）。

        Args:
            name: Hash Key 名称。
            mapping: 字段-值字典，值会被转换为 str。
            ex: 过期时间（秒）。

        Examples::

            # 场景 A：RBAC 权限缓存（推荐 Set 方案）
            # 写入：只存拥有的权限 code，15 分钟过期
            perm_key = f'perm:{user_id}'
            await redis_client.sadd(perm_key, 'user:read', 'post:write')
            await redis_client.expire(perm_key, 900)
            # 鉴权：O(1) 判断是否拥有某权限
            has_perm = await redis_client.sismember(perm_key, 'post:write')  # True / False
            # 读出全部已授权权限（展示用）
            all_perms = await redis_client.smembers(perm_key)  # {'user:read', 'post:write'}

            # 场景 B：Session 元数据缓存，Hash 存储多字段附加信息，24 小时过期
            await redis_client.hset_with_expire(
                name=f'session:{token}',
                mapping={'user_id': str(user.id), 'role': user.role, 'device': 'iPhone'},
                ex=86400,
            )
            # 读取单个字段
            uid = await redis_client.hget(f'session:{token}', 'user_id')
        """
        str_mapping = {k: str(v) for k, v in mapping.items()}
        async with self.pipeline(transaction=True) as pipe:
            pipe.hset(name, mapping=str_mapping)
            pipe.expire(name, ex)
            await pipe.execute()


redis_client: RedisClient = RedisClient()
