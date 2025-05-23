#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.paths import ENV_DIR
from backend.utils.tools import get_project_version

__all__ = ['settings']


class Settings(BaseSettings):
    ENVIRONMENT: Literal['development', 'test', 'production'] = 'development'

    model_config = SettingsConfigDict(
        env_file=f'{ENV_DIR}/.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )

    # ==============  FastAPI  ==============
    FASTAPI_API_ROUTE_PREFIX: str = '/api'
    FASTAPI_VERSION: str = get_project_version()
    FASTAPI_TITLE: str = 'FastAPI Services'
    FASTAPI_DESCRIPTION: str = '基于 FastAPI 搭建的后端服务'
    FASTAPI_DOCS_URL: str | None = f'{FASTAPI_API_ROUTE_PREFIX}/docs'
    FASTAPI_OPENAPI_URL: str | None = f'{FASTAPI_API_ROUTE_PREFIX}/openapi'
    FASTAPI_STATIC_FILES: bool = True

    @model_validator(mode='before')
    @classmethod
    def validator_api_url(cls, values):
        if values['ENVIRONMENT'] == 'production':
            values['FASTAPI_DOCS_URL'] = None
            values['FASTAPI_OPENAPI_URL'] = None
            values['FASTAPI_STATIC_FILES'] = False
        return values


@lru_cache
def get_settings() -> Settings:
    return Settings()


# 创建全局配置实例
settings = get_settings()
