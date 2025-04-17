#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError

from backend.common.logger import log
from backend.core.config import settings


class RedisClient(Redis):
    def __init__(self):
        super(RedisClient, self).__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD.get_secret_value(),
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT,
            socket_connect_timeout=5,  # 连接超时
            socket_keepalive=True,  # 保持连接
            health_check_interval=30,  # 健康检查间隔
            decode_responses=True,  # 转码 utf-8
            retry_on_timeout=True,  # 超时重试
            max_connections=20,  # 最大连接数
        )

    async def open(self) -> None:
        """触发初始化连接"""
        try:
            await self.ping()
        except TimeoutError:
            log.error('❌ 数据库 redis 连接超时')
            sys.exit()
        except AuthenticationError:
            log.error('❌ 数据库 redis 连接认证失败')
            sys.exit()
        except Exception as e:
            log.error('❌ 数据库 redis 连接异常 {}', e)
            sys.exit()

    async def delete_prefix(self, prefix: str, exclude: str | list[str] | None = None):
        """删除指定前缀的所有 key

        :param prefix: 前缀
        :param exclude: 排除的 key
        """
        if isinstance(exclude, str):
            exclude = [exclude]
        elif exclude is None:
            exclude = []

        deleted_keys = []
        async for key in self.scan_iter(match=f'{prefix}*'):
            if key not in exclude:
                deleted_keys.append(key)

        if deleted_keys:
            await self.delete(*deleted_keys)
            log.info(f"🧹 已删除 Redis 前缀 '{prefix}' 下 {len(deleted_keys)} 个 key")


redis_client = RedisClient()
