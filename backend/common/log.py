import inspect
import logging
import re
import sys

from os import path

from asgi_correlation_id import correlation_id
from loguru import logger

from backend.core.config import settings
from backend.core.path import LOG_DIR


class InterceptHandler(logging.Handler):
    """
    日志拦截处理器，用于将标准库的日志重定向到 loguru
    """

    def emit(self, record: logging.LogRecord):
        # 获取对应的 Loguru 级别（如果存在）
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找记录日志消息的调用者
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def default_formatter(record):
    """默认日志格式化程序"""

    # 重写 sqlalchemy echo 输出
    # https://github.com/sqlalchemy/sqlalchemy/discussions/12791
    record_name = record['name'] or ''
    if record_name.startswith('sqlalchemy'):
        record['message'] = re.sub(r'\s+', ' ', record['message']).strip()

    return settings.LOG_STD_FORMAT if settings.LOG_STD_FORMAT.endswith('\n') else f'{settings.LOG_STD_FORMAT}\n'


def setup_logging() -> None:
    # 设置根日志处理器和级别
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_ROOT_LEVEL)

    # 遍历所有子日志记录器，移除默认处理器，设置传播选项
    for name in logging.root.manager.loggerDict.keys():
        # 移除子日志器的所有处理器
        logging.getLogger(name).handlers = []

        if 'uvicorn.access' in name or 'watchfiles.main' in name:
            logging.getLogger(name).propagate = False
        else:
            logging.getLogger(name).propagate = True

    logger.remove()

    def correlation_id_filter(record):
        cid = correlation_id.get(settings.LOG_CID_DEFAULT_VALUE)
        record['correlation_id'] = (cid or '-')[: settings.LOG_CID_UUID_LENGTH]
        return True

    # 配置 loguru 处理器
    logger.configure(
        handlers=[
            {  # 处理器: 控制台输出
                'sink': sys.stdout,
                'level': settings.LOG_STDOUT_LEVEL,
                'format': default_formatter,
                'filter': lambda record: correlation_id_filter(record),
            }
        ]
    )


def set_custom_logfile() -> None:
    """设置自定义日志文件"""
    log_path = LOG_DIR

    # 日志文件
    log_stdout_file = path.join(log_path, settings.LOG_STDOUT_FILENAME)
    log_stderr_file = path.join(log_path, settings.LOG_STDERR_FILENAME)

    # 配置 Loguru 日志文件处理器
    # https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    log_config = {
        'rotation': '10 MB',  # 单个日志文件大小超过 10MB 时轮转
        'retention': '15 days',  # 保留最近 15 天的日志
        'compression': 'tar.gz',  # 旧日志压缩为 .tar.gz 格式
        'enqueue': True,  # 启用多线程安全
        'format': settings.LOG_FILE_FORMAT,  # 日志格式化样式
    }

    # 标准输出文件
    logger.add(
        str(log_stdout_file),
        level=settings.LOG_STDOUT_LEVEL,
        filter=lambda record: record['level'].no <= 30,
        backtrace=False,
        diagnose=False,
        **log_config,
    )

    # 标准错误文件
    logger.add(
        str(log_stderr_file),
        level=settings.LOG_STDERR_LEVEL,
        filter=lambda record: record['level'].no > 30,
        backtrace=True,
        diagnose=True,
        **log_config,
    )


log = logger
