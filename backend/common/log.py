import logging
import re
import sys

import loguru

from loguru import logger

from backend.common.request import get_request_trace_id
from backend.core.config import settings
from backend.core.path import LOG_DIR

__all__ = ['register_logger']

#  需要静默/降级的第三方记录器
#  key: 记录器名称, value: 要设置的最低级别 (None 表示完全禁用)
_SILENCED_LOGGERS: dict[str, int | None] = {
    # 文件变更监听 — 开发热重载时会疯狂打印文件扫描信息
    'watchfiles.main': logging.CRITICAL,
    'watchfiles.watcher': logging.CRITICAL,
    # Granian 的 access log 由应用层中间件自行记录，避免重复
    'granian.access': None,
    'granian.server': logging.WARNING,
    # asyncpg 连接池内部诊断日志
    'asyncpg': logging.WARNING,
    # multipart 解析调试信息
    'multipart.multipart': logging.WARNING,
    'multipart': logging.WARNING,
}

#  日志文件格式 — 文件中不含 ANSI 色彩标记，便于后续 ELK / Loki 采集
_FILE_LOG_FORMAT: str = (
    '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[request_id]} | {module}:{function}:{line} | {message}'
)


def _sqla_formatter(record: loguru.Record) -> str:
    """SQLAlchemy echo 输出压缩多余空白.

    当 DB_ECHO=True 时，SQLAlchemy 的 SQL 日志会包含大量换行和缩进，
    此格式化器将其压缩为单行，提升可读性。
    参考: https://github.com/sqlalchemy/sqlalchemy/discussions/12791
    """
    msg = record.get('message', '')
    name = record.get('name', '')

    # 重写 sqlalchemy echo 输出
    # https://github.com/sqlalchemy/sqlalchemy/discussions/12791
    if name and name.startswith('sqlalchemy'):
        record['message'] = re.sub(r'\s+', ' ', msg).strip()

    return f'{_FILE_LOG_FORMAT}\n'


class InterceptHandler(logging.Handler):
    """拦截标准库 logging 消息并转发到 loguru.

    原理：
    1. 根据 LogRecord.levelno 映射到 loguru 的 level name
    2. 沿调用栈回溯找到实际产生日志的帧，确保 loguru 记录正确的源码位置
    3. 通过 logger.opt(depth, exception) 发射日志
    """

    def emit(self, record: logging.LogRecord) -> None:
        # 映射标准 level → loguru level name
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 找到产生日志的真实调用帧
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _request_id_patcher(record: loguru.Record) -> None:
    """自动获取 X-Request-ID, 注入 request_id."""
    record['extra']['request_id'] = get_request_trace_id()


def register_logger() -> None:
    """初始化整个应用的日志系统.

    执行步骤：
    1. 清除 loguru 默认 handler
    2. 注册 request_id patcher
    3. 添加控制台 sink（彩色、带 request_id）
    4. 添加 access 文件 sink（≥ INFO, 每日滚动, 7 天保留）
    5. 添加 error 文件 sink（≥ ERROR, 每日滚动, 30 天保留）
    6. 拦截标准 logging 根记录器
    7. 遍历所有子记录器，移除默认 handler 并设置 propagate
    8. 静默噪音记录器
    """
    is_dev = settings.ENVIRONMENT != 'production'

    # ---- 步骤 1: 移除 loguru 内置的 stderr handler ----
    logger.remove()

    # ---- 步骤 2: 注册 patcher，让每条日志自动携带 request_id ----
    logger.configure(patcher=_request_id_patcher)

    # ---- 步骤 3: 控制台 sink ----
    logger.add(
        sink=sys.stdout,
        level=settings.LOG_CONSOLE_LEVEL,
        format=settings.LOG_STD_FORMAT,
        colorize=True,
        backtrace=True,
        diagnose=is_dev,  # 生产环境关闭变量诊断，防止敏感信息泄露
    )

    # ---- 步骤 4: access 文件 sink (INFO ~ WARNING，不含 ERROR) ----
    logger.add(
        sink=str(LOG_DIR / settings.LOG_ACCESS_FILENAME),
        level=settings.LOG_ACCESS_LEVEL,
        format=_sqla_formatter,
        filter=lambda record: record['level'].no < 40,
        rotation='00:00',  # 每天零点切割，历史文件自动带日期后缀
        retention='7 days',
        compression='gz',
        encoding='utf-8',
        enqueue=True,  # 异步写入，多进程安全
        backtrace=True,
        diagnose=is_dev,
    )

    # ---- 步骤 5: error 文件 sink (≥ ERROR，与 access 严格不重叠) ----
    logger.add(
        sink=str(LOG_DIR / settings.LOG_ERROR_FILENAME),
        level=settings.LOG_ERROR_LEVEL,
        format=_sqla_formatter,
        rotation='00:00',
        retention='30 days',
        compression='gz',
        encoding='utf-8',
        enqueue=True,
        backtrace=True,
        diagnose=is_dev,
    )

    # ---- 步骤 6: 拦截标准 logging 根记录器 ----
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # ---- 步骤 7: 遍历所有已注册的子记录器 ----
    for name in list(logging.root.manager.loggerDict):
        child_logger = logging.getLogger(name)
        child_logger.handlers.clear()
        child_logger.propagate = True

    # ---- 步骤 8: 静默噪音记录器 ----
    for logger_name, level in _SILENCED_LOGGERS.items():
        noisy = logging.getLogger(logger_name)
        if level is None:
            noisy.disabled = True
        else:
            noisy.setLevel(level)
        noisy.propagate = False  # 阻止冒泡，彻底屏蔽

    logger.info(f'📋 日志系统初始化完成 (环境：{settings.ENVIRONMENT})')
