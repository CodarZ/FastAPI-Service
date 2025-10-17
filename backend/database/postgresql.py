import sys

from typing import Annotated, AsyncGenerator
from uuid import uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.common.log import log
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
        log.info('🔄 PostgreSQL 引擎创建成功')
    except Exception as e:
        log.error('❌ PostgreSQL 引擎创建失败 {}', e)
        sys.exit(1)
    else:
        # 创建异步会话工厂
        db_session = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
        )
        return engine, db_session


# SALA 异步引擎和会话
async_engine, async_db_session = create_async_engine_and_session(settings.PostgreSQL_DATABASE_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """通过依赖注入, 提供异步数据库会话"""
    async with async_db_session() as session:
        yield session


async def create_tables() -> None:
    """创建数据库表"""
    try:
        async with async_engine.begin() as coon:
            await coon.run_sync(MappedBase.metadata.create_all)
        log.success('✅ 数据库表创建成功')
    except Exception as e:
        log.error('❌ 数据库表创建失败，连接数据库失败: {}', e)
        sys.exit(1)


def uuid4_str() -> str:
    """数据库存储 uuid 字符串"""
    return str(uuid4())


# 当前数据库会话 注解
CurrentSession = Annotated[AsyncSession, Depends(get_db)]
