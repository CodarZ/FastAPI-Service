#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import inspect
import logging

from os import path
from sys import stdout

from asgi_correlation_id import correlation_id
from loguru import logger

from backend.core import paths
from backend.core.config import settings


class InterceptHandler(logging.Handler):
    """
    日志拦截处理器，用于将标准库的日志重定向到 loguru
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        参考：https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
        """
        # 获取对应的 Loguru 级别（如果存在）
        level: str | int
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


def setup_logging() -> None:
    """
    设置日志处理器
    """
    # 设置根日志处理器为 InterceptHandler
    logging.root.handlers = [InterceptHandler()]
    # 设置根日志级别
    logging.root.setLevel(settings.LOG_ROOT_LEVEL)

    # 遍历所有子日志记录器，移除默认处理器，设置传播选项
    for name in logging.root.manager.loggerDict.keys():
        # 移除子日志器的所有处理器
        logging.getLogger(name).handlers = []
        if 'uvicorn.access' in name or 'watchfiles.main' in name:
            logging.getLogger(name).propagate = False  # 不传播日志
        else:
            logging.getLogger(name).propagate = True  # 传播日志到根记录器

        # 调试日志处理
        # logging.debug(f'{logging.getLogger(name)}, {logging.getLogger(name).propagate}')

    def correlation_id_filter(record):
        """
        定义相关联 correlation_id 过滤函数

        https://github.com/snok/asgi-correlation-id?tab=readme-ov-file#configure-logging

        https://github.com/snok/asgi-correlation-id/issues/7
        """
        cid = correlation_id.get(settings.LOG_CID_DEFAULT_VALUE)
        if not cid:
            # 生成新的关联 ID
            import uuid

            cid = str(uuid.uuid4())
            correlation_id.set(cid)

        record['correlation_id'] = cid[: settings.LOG_CID_UUID_LENGTH]
        record['extra']['correlation_id'] = cid[: settings.LOG_CID_UUID_LENGTH]  # 官方建议
        return True

    logger.remove()
    logger.configure(
        handlers=[
            {
                'sink': stdout,
                'level': settings.LOG_STDOUT_LEVEL,
                'filter': lambda record: correlation_id_filter(record),
                'format': settings.LOG_STD_FORMAT,
            },
        ]
    )


def set_custom_logfile() -> None:
    """设置自定义日志文件"""
    log_path = paths.LOG_DIR
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
