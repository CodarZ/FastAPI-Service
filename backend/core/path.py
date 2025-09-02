#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

# 根目录
ROOT_PATH = Path(__file__).resolve().parent.parent.parent

# 项目根目录
BASE_PATH = ROOT_PATH / 'backend'

# 日志文件路径
LOG_DIR = ROOT_PATH / 'log'

# 静态资源目录
STATIC_DIR = ROOT_PATH / 'static'

# env 环境变量文件
ENV_DIR = ROOT_PATH / 'env'

# 确保目录存在
for directory in [LOG_DIR, STATIC_DIR, ENV_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
