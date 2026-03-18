import sys

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.common.model import MappedBase
from backend.core.config import settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def _create_async_db_engine() -> AsyncEngine:
    """创建 PostgreSQL 异步引擎."""
    try:
        engine = create_async_engine(
            url=settings.PostgreSQL_URL,
            echo=settings.DB_ECHO,
            echo_pool=settings.DB_ECHO_POOL,
            # 连接池策略
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
            pool_use_lifo=settings.DB_POOL_USE_LIFO,
            # asyncpg 驱动参数
            connect_args={
                'command_timeout': 60,  # 查询超时时间（秒），防止慢查询阻塞连接
                'server_settings': {
                    'jit': 'off',  # 关闭 JIT 编译，避免短查询的编译开销
                    'timezone': settings.DATETIME_TIMEZONE,  # 统一会话时区，TIMESTAMPTZ 读出即为目标时区
                    'application_name': settings.FASTAPI_TITLE,
                },
            },
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f'❌ PostgreSQL 引擎创建失败: {e}')
        sys.exit(1)
    else:
        logger.info('✅ PostgreSQL 引擎创建成功')
        return engine


def _create_async_db_session(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """创建异步会话工厂."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession]:
    """获取数据库会话（无自动事务）.

    适用场景：
    - 只读查询
    - 手动控制事务
    """
    async with async_db_session() as session:
        yield session


async def get_db_transaction() -> AsyncGenerator[AsyncSession]:
    """获取带自动事务的数据库会话.

    - 正常 yield 结束：自动调用 session.commit()
    - 发生未捕获异常：自动调用 session.rollback()
    """
    async with async_db_session.begin() as session:
        yield session


async def create_tables() -> None:
    """创建数据库表.

    - 仅用于开发/测试, 生产环境应使用 `Alembic` 迁移管理表结构。
    - 根据 `MappedBase` 子类的元数据创建所有表结构, 会跳过已存在的表, 并且不会更新表结构。
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.create_all)
        logger.success('✅ 数据库表创建成功')


async def drop_tables() -> None:
    """删除所有数据库表.

    危险操作, 仅用于开发测试环境
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.drop_all)


# ==================== 异步引擎, 会话 ====================
async_engine: AsyncEngine = _create_async_db_engine()
async_db_session: async_sessionmaker[AsyncSession] = _create_async_db_session(async_engine)

# ==================== 类型注解 ====================
CurrentSession = Annotated[AsyncSession, Depends(get_db)]
CurrentSessionTransaction = Annotated[AsyncSession, Depends(get_db_transaction)]
