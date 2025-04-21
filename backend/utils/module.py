#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib

from functools import lru_cache

from backend.common.exception import errors
from backend.common.logger import log


@lru_cache(maxsize=512)
def import_module_cached(module_path: str):
    """缓存导入模块"""
    return importlib.import_module(module_path)


def dynamic_import_data_model(module_path: str) -> object:
    """动态导入数据模型"""
    try:
        module_path, class_name = module_path.rsplit('.', 1)
        module = import_module_cached(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        log.error(f'动态导入数据模型失败: {module_path}, 错误信息: {e}')
        raise errors.ServerError(
            msg='系统异常, 数据模型列动态解析失败！',
            data={
                'module_path': module_path,
            },
        )
