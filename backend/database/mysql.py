#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from typing import Annotated, AsyncGenerator
from uuid import uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.common.logger import log
from backend.common.model import MappedBase
from backend.core.config import settings


def create_async_engine_and_session(url):
    try:
        engine = create_async_engine(
            url=url,
            echo=settings.DB_ECHO,
            future=True,
            # 中等并发
            pool_size=10,  # 低：- 高：+
            max_overflow=20,  # 低：- 高：+
            pool_timeout=30,  # 低：+ 高：-
            pool_recycle=3600,  # 低：+ 高：-
            pool_pre_ping=True,  # 低：False 高：True
            pool_use_lifo=False,  # 低：False 高：True
        )
        log.success('✅ MySQL 连接成功')
    except Exception as e:
        log.error('❌ MySQL 连接失败 {}', e)
        sys.exit()
    else:
        # 创建异步会话工厂
        db_session = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
        )
        return engine, db_session


async_engine, async_db_session = create_async_engine_and_session(settings.MYSQL_DATABASE_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话

    通过依赖注入的方式，在 FastAPI 的请求生命周期内提供异步数据库会话。
    在发生异常时回滚事务，并在会话结束后关闭会话。

    :yield: 异步数据库会话对象
    """
    async with async_db_session() as session:
        yield session


async def create_table() -> None:
    """自动创建数据库表"""

    async with async_engine.begin() as coon:
        await coon.run_sync(MappedBase.metadata.create_all)  # 在事务中运行同步方法以创建表
        log.success('✅ 数据表创建成功！')


def uuid4_str() -> str:
    """数据库引擎对 UUID 类型兼容性的解决方案。

    将 Python 的 UUID4 对象转换为字符串，以便在数据库中以文本格式存储。
    """
    return str(uuid4())


# Session Annotated
CurrentSession = Annotated[AsyncSession, Depends(get_db)]
