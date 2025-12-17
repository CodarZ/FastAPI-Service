import sys

from redis import AuthenticationError
from redis.asyncio import Redis

from backend.common.log import log
from backend.core.config import settings


class RedisClient(Redis):
    def __init__(self) -> None:
        """初始化 Redis 配置"""

        super().__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD.get_secret_value(),
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            socket_connect_timeout=settings.REDIS_TIMEOUT,
            socket_keepalive=True,  # 保持连接
            health_check_interval=30,  # 健康检查间隔
            decode_responses=True,  # 转码 utf-8
        )

    async def open(self) -> None:
        """建立 Redis 连接并验证"""

        try:
            await self.execute_command('PING')
            log.success('✅ Redis 连接成功')
        except TimeoutError:
            log.error('❌ Redis 连接超时')
            sys.exit(1)
        except AuthenticationError:
            log.error('❌ Redis 连接认证失败')
            sys.exit(1)
        except Exception as e:
            log.error('❌ Redis 连接异常 {}', e)
            sys.exit(1)

    async def delete_prefix(self, prefix: str, exclude: str | list[str] | None = None, batch_size: int = 1000) -> int:
        """删除指定前缀的所有 key

        Args:
            prefix: key 前缀（如 'user:*', 'session:*'）
            exclude: 排除的键或键列表，不会被删除
            batch_size: 批量删除的大小，默认 1000

        Returns:
            删除的 key 数量
        """

        exclude_set = set(exclude) if isinstance(exclude, list) else {exclude} if isinstance(exclude, str) else set()
        batch_keys = []
        deleted_count = 0

        pattern = f'{prefix}*' if not prefix.endswith('*') else prefix

        async for key in self.scan_iter(match=pattern):
            if key not in exclude_set:
                batch_keys.append(key)

                if len(batch_keys) >= batch_size:
                    await self.delete(*batch_keys)
                    deleted_count += len(batch_keys)
                    batch_keys.clear()

        # 删除剩余的 key
        if batch_keys:
            await self.delete(*batch_keys)
            deleted_count += len(batch_keys)

        return deleted_count

    async def get_prefix(self, prefix: str, count: int = 1000) -> list[str]:
        """获取指定前缀的所有 key"""

        pattern = f'{prefix}*' if not prefix.endswith('*') else prefix
        return [key async for key in self.scan_iter(match=pattern, count=count)]


redis_client: RedisClient = RedisClient()
