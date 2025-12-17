"""Alembic 迁移环境配置"""

import asyncio

from logging.config import fileConfig
from typing import TYPE_CHECKING

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from backend.common.model import MappedBase
from backend.core.config import settings
from backend.core.path import ALEMBIC_VERSION_DIR

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


# TODO 在这里导入所有需要迁移的模型, 以确保 Alembic 能够检测到它们

# Alembic Config 对象，提供对 .ini 文件中值的访问
alembic_config = context.config

# 配置 Python 日志
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# 设置 MetaData 对象以支持 'autogenerate'
target_metadata = MappedBase.metadata

# 其他从 env.py 可访问的值
# my_important_option = alembic_config.get_main_option("my_important_option")
alembic_config.set_main_option(
    'sqlalchemy.url', settings.PostgreSQL_DATABASE_URL.render_as_string(hide_password=False).replace('%', '%%')
)

if not ALEMBIC_VERSION_DIR.exists():
    ALEMBIC_VERSION_DIR.mkdir(parents=True, exist_ok=True)


def run_migrations_offline() -> None:
    """在 'offline' 模式下运行迁移。

    在这种模式下，不需要实际的数据库连接。
    只需要配置 URL 即可生成 SQL 脚本。

    使用场景：
        - 生成 SQL 文件而不执行
        - 在无法连接数据库的环境中生成迁移脚本
    """
    url = alembic_config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        compare_type=True,  # 比较列类型变化
        compare_server_default=True,  # 比较默认值变化
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """在提供的连接上执行迁移。"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # 检测列类型变化
        compare_server_default=True,  # 检测默认值变化
        # 可选：自定义迁移选项
        # render_as_batch=True,  # SQLite 需要
        # transaction_per_migration=True,
        # process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """使用异步引擎运行迁移。"""
    # 从配置构建异步引擎

    connectable = async_engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,  # 迁移时不使用连接池
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在 'online' 模式下运行迁移。

    在这种模式下，需要创建一个引擎并关联一个连接。
    适用于实际的数据库迁移操作。
    """
    asyncio.run(run_async_migrations())


# 根据上下文选择运行模式
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
