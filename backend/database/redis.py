#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from redis import AuthenticationError
from redis.asyncio import Redis

from backend.common.log import log
from backend.core.config import settings


class RedisClient(Redis):
    def __init__(self) -> None:
        super().__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD.get_secret_value(),
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            socket_connect_timeout=settings.REDIS_TIMEOUT,
            socket_keepalive=True,
            health_check_interval=30,
            decode_responses=True,
        )

    async def open(self) -> None:
        """建立 Redis 连接并验证"""
        try:
            await self.ping()
            log.success('✅ Redis 连接成功')
        except TimeoutError:
            log.error('❌ 数据库 redis 连接超时')
            sys.exit(1)
        except AuthenticationError:
            log.error('❌ 数据库 redis 连接认证失败')
            sys.exit(1)
        except Exception as e:
            log.error('❌ 数据库 redis 连接异常 {}', e)
            sys.exit(1)

    async def shut(self) -> None:
        """关闭 Redis 连接"""
        try:
            await self.close()
            log.success('✅ Redis 连接关闭成功')
        except Exception as e:
            log.error('❌ 关闭 Redis 连接时出现异常: {}', e)

    async def delete_prefix(self, prefix: str, exclude: str | list[str] | None = None) -> None:
        """删除指定前缀的所有 Key"""
        exclude_set = set()
        if exclude:
            if isinstance(exclude, str):
                exclude_set.add(exclude)
            else:
                exclude_set.update(exclude)
        try:
            keys = []
            async for key in self.scan_iter(match=f'{prefix}*'):
                if key not in exclude_set:
                    keys.append(key)

            if keys:
                deleted_count = await self.delete(*keys)
                log.info(f"成功删除 {deleted_count} 个前缀为 '{prefix}' 的 key")

        except Exception as e:
            log.error(f"删除前缀为 '{prefix}' 的 key 时出现异常: {e}")
            raise


redis_client: RedisClient = RedisClient()
