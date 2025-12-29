import sys

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.common.log import log
from backend.common.model import MappedBase
from backend.core.config import settings

if TYPE_CHECKING:
    from sqlalchemy import URL


def create_async_engine_and_session(url: str | URL) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """创建异步数据库引擎和会话工厂。

    根据应用环境配置连接池参数, 平衡并发性能与资源占用：
        - 开发/测试环境：较小的连接池, 快速回收
        - 生产环境：更大的连接池和溢出空间, 支持高并发
    """
    try:
        engine = create_async_engine(
            url=url,
            echo=settings.DB_ECHO,
            # === 连接池配置（针对中等并发场景优化） ===
            pool_size=10,  # 连接池大小：保持 10 个常驻连接
            max_overflow=20,  # 溢出连接数：繁忙时最多额外创建 20 个（总计 30 个）
            pool_timeout=30,  # 获取连接超时：30 秒
            pool_recycle=3600,  # 连接回收时间：1 小时, 防止 DB 端超时关闭
            pool_pre_ping=True,  # 连接预检：使用前验证连接有效性（适合跨网络/不稳定连接）
            pool_use_lifo=False,  # FIFO 模式：优先使用旧连接, 避免所有连接同时过期
            # 可选：连接参数
            # connect_args={
            #     'server_settings': {'application_name': 'fastapi-service'},
            #     'command_timeout': 60,
            # },
        )
        log.info('✅ PostgreSQL Engine 配置完成')
    except Exception:
        log.exception('❌ PostgreSQL Engine 配置失败, 应用无法启动')
        sys.exit(1)
    else:
        # 创建会话工厂
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,  # 禁用自动 flush, 手动控制写入时机
            expire_on_commit=False,  # commit 后保持对象属性可访问, 避免额外查询
        )
        log.info('✅ PostgreSQL Session 工厂配置完成')

    return engine, session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """数据库会话"""
    async with async_session() as session:
        yield session


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """带有事务的数据库会话"""
    async with async_session.begin() as session:
        yield session


async def create_tables() -> None:
    """创建数据库表（仅用于开发/测试）。

    - 根据 MappedBase 子类的元数据创建所有表结构, 会跳过已存在的表, 并且不会更新表结构。
    - 生产环境应使用 Alembic 迁移管理表结构
    """

    if not MappedBase.metadata.tables:
        log.warning('⚠️  未检测到任何数据库模型, 跳过表创建')
        return

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(MappedBase.metadata.create_all)
        log.success('✅ 数据库表创建成功')
    except Exception as e:
        log.warning('⚠️  数据库表创建失败: {}, 可能是连接问题, 应用将继续运行', e)
        # 不再退出应用, 允许在没有数据库的情况下启动（用于某些开发场景）


async def drop_tables() -> None:
    """删除所有数据库表（危险操作, 仅用于开发测试环境）。

    示例:
    ```python
    # 测试环境使用示例
    if settings.ENVIRONMENT == 'test':
        await drop_tables()  # 清理测试数据
        await create_tables()  # 重建表结构


    # pytest fixture 示例
    @pytest.fixture(scope='session')
    async def setup_test_db():
        await create_tables()
        yield
        await drop_tables()  # 测试完成后清理
    ```
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.drop_all)


# 创建全局引擎和会话工厂
async_engine, async_session = create_async_engine_and_session(settings.PostgreSQL_DATABASE_URL)

CurrentSession = Annotated[AsyncSession, Depends(get_db)]
"""FastAPI 依赖注入: 数据库会话类型别名。"""

CurrentSessionTransaction = Annotated[AsyncSession, Depends(get_db_transaction)]
"""FastAPI 依赖注入: 自动管理事务的数据库会话类型别名。

与 CurrentSession 的区别：
    - CurrentSession: 需要手动调用 commit/rollback
    - CurrentSessionTransaction: 自动管理事务, 函数结束时自动提交或回滚

事务管理行为:
    - 正常完成：自动 commit
    - 抛出异常：自动 rollback
    - 无需手动调用 commit()

使用场景:
    - 需要原子性保证的多表操作
    - 复杂业务逻辑的事务一致性
    - 简化事务管理代码
"""
