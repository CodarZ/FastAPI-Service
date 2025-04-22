#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.paths import ENV_DIR


class AdminSettings(BaseSettings):
    """Admin 配置"""

    ENVIRONMENT: Literal['development', 'test', 'production'] = 'development'
    model_config = SettingsConfigDict(
        env_file=Path(ENV_DIR) / f'.env.{os.getenv("ENVIRONMENT", "development")}',
        env_file_encoding='utf-8',
    )

    # Auth2

    # Captcha
    CAPTCHA_LOGIN_REDIS_PREFIX: str = 'fs:login:captcha'  # 登录验证码存储在 Redis 的前缀
    CAPTCHA_LOGIN_EXPIRE_SECONDS: int = 300


@lru_cache
def get_admin_settings() -> AdminSettings:
    """获取 admin 配置"""
    return AdminSettings()


admin_settings = get_admin_settings()
