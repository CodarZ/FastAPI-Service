import inspect
import logging
import re
import sys

from loguru import logger as _logger

from backend.common.request.trace_id import get_request_trace_id
from backend.core.config import settings
from backend.core.path import LOG_DIR


class InterceptHandler(logging.Handler):
    """日志拦截处理器

    将标准库的日志重定向到 loguru
    """

    def emit(self, record: logging.LogRecord):
        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找记录的调用者
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        _logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def default_formatter(record) -> str:
    """默认日志格式化程序"""
    record_name = record.get('name') or ''

    # 重写 sqlalchemy echo 输出
    # https://github.com/sqlalchemy/sqlalchemy/discussions/12791
    if record_name.startswith('sqlalchemy'):
        record['message'] = re.sub(r'\s+', ' ', record['message']).strip()

    return settings.LOG_STD_FORMAT if settings.LOG_STD_FORMAT.endswith('\n') else f'{settings.LOG_STD_FORMAT}\n'


def setup_logging():
    """配置日志处理器"""

    # 设置根日志处理器和级别
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_CONSOLE_LEVEL)

    # 遍历所有子日志记录器, 移除默认处理器, 设置传播选项
    for name in logging.root.manager.loggerDict:
        # 移除子日志记录器的所有处理器
        logging.getLogger(name).handlers = []

        # 日志处理规则
        # 1.关闭
        #   + granian.access：HTTP 访问日志，关闭
        #   + 其他三方日志，如 watchfiles.main：关闭
        # 2.保留
        #   + _granian / granian：框架核心日志，保留
        if 'granian.access' in name or 'watchfiles.main' in name:
            logging.getLogger(name).propagate = False
        else:
            logging.getLogger(name).propagate = True

    # 移除 loguru 默认 handler
    _logger.remove()

    # request_id 过滤器（供 loguru 使用）
    def request_id_filter(record):
        """为日志记录添加 request_id 字段"""
        rid = get_request_trace_id()
        record['request_id'] = rid[:32]
        return True

    # 配置 loguru 处理器
    _logger.configure(
        handlers=[
            {
                # 控制台输出
                'sink': sys.stdout,
                'level': settings.LOG_CONSOLE_LEVEL,
                'format': default_formatter,
                'filter': request_id_filter,
            }
        ]
    )


def set_custom_logfile():
    """设置自定义日志文件"""

    # 日志文件
    log_access_file = LOG_DIR / settings.LOG_ACCESS_FILENAME
    log_error_file = LOG_DIR / settings.LOG_ERROR_FILENAME

    # 日志压缩回调
    # 配置 Loguru 日志文件处理器
    # https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    log_config = {
        'rotation': '10 MB',
        'retention': '15 days',
        'compression': 'tar.gz',
        'enqueue': True,
        'format': settings.LOG_STD_FORMAT,
    }

    # 标准输出文件
    _logger.add(
        str(log_access_file),
        level=settings.LOG_ACCESS_LEVEL,
        filter=lambda record: record['level'].no <= 30,
        backtrace=False,
        diagnose=False,
        **log_config,
    )

    # 标准错误文件
    _logger.add(
        str(log_error_file),
        level=settings.LOG_ERROR_LEVEL,
        filter=lambda record: record['level'].no > 30,
        backtrace=True,
        diagnose=True,
        **log_config,
    )


log = _logger
