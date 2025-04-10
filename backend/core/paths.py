#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

# 获取项目根目录 绝对路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# env 环境变量文件
ENV_DIR = BASE_DIR / 'env'

# log 日志文件路径
LOG_DIR = BASE_DIR / 'log'

# static 挂载静态目录
STATIC_DIR = BASE_DIR / 'static'

# 确保目录存在
for directory in [ENV_DIR, LOG_DIR, STATIC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
