#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.paths import ENV_DIR

print(f'ENV_DIR: {ENV_DIR}')


class Settings(BaseSettings):
    ENVIRONMENT: Literal['development', 'test', 'production'] = 'development'

    # 动态加载 ENV_DIR 中的 `.env` 文件

    # 动态加载 ENV_DIR 中的 `.env` 文件
    model_config = SettingsConfigDict(
        env_file=Path(ENV_DIR) / f'.env.{os.getenv("ENVIRONMENT", "development")}',
        env_file_encoding='utf-8',
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
