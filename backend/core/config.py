#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import lru_cache
from os import urandom
from secrets import token_urlsafe
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

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

    # ============== Middleware ==============
    MIDDLEWARE_ACCESS: bool = True  # 是否启用 请求日志中间件
    MIDDLEWARE_CORS: bool = True  # 是否启用 跨域中间件

    # ============== Trace ID ==============
    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'  # 请求头中 Trace ID 的 Key

    # ============== CORS ==============
    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://127.0.0.1:8000',
    ]  # 允许跨域的源，末尾不带 '/'
    CORS_EXPOSE_HEADERS: list[str] = [
        TRACE_ID_REQUEST_HEADER_KEY,
    ]  # 允许跨域的响应头

    # ============== DateTime ==============
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # ============== 数据库 MySQL ==============
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 3306
    DB_USER: str = 'root'
    DB_PASSWORD: SecretStr = SecretStr('123456')
    DB_DATABASE: str = 'fastapi-services'

    DB_ECHO: bool = False  # 连接到数据库时是否打印SQL语句
    DB_CHARSET: str = 'utf8mb4'

    # @computed_field
    @property
    def MYSQL_DATABASE_URL(self):
        return URL.create(
            drivername='mysql+asyncmy',
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_DATABASE if self.ENVIRONMENT == 'production' else f'{self.DB_DATABASE}_test',
            query={'charset': self.DB_CHARSET},
        )

    # ============== Redis ==============
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: SecretStr = SecretStr('')
    REDIS_DATABASE: int = 0
    REDIS_TIMEOUT: int = 10
    REQUEST_LIMITER_REDIS_PREFIX: str = 'fs:limiter'  # Redis 限流器前缀

    # ============== JWT ================
    JWT_USER_REDIS_PREFIX: str = 'fs:user'
    JWT_USER_REDIS_EXPIRE_SECONDS: int = 604800  # 过期时间 7 天，单位：秒

    # ============== Token ==============
    TOKEN_SECRET_KEY: str = token_urlsafe(32)
    TOKEN_ALGORITHM: str = 'HS256'
    TOKEN_EXPIRE_SECONDS: int = 604800
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 691200  # refresh token 过期时间 8 天，单位：秒
    TOKEN_REDIS_PREFIX: str = 'fs:token'  # token 存储在 Redis 的前缀
    TOKEN_REFRESH_REDIS_PREFIX: str = 'fs:refresh_token'  # refresh_token 存储在 Redis 的前缀
    TOKEN_EXTRA_INFO_REDIS_PREFIX: str = 'fs:token_extra_info'  # token 存储在 Redis 附带的额外信息
    TOKEN_ONLINE_REDIS_PREFIX: str = 'fs:token_online'  # 在线用户存储在 Redis 的前缀
    TOKEN_REQUEST_PATH_EXCLUDE: list[str] = [
        f'{FASTAPI_API_ROUTE_PREFIX}/auth/login',
    ]  # JWT 白名单

    # ============== Cookies ==============
    COOKIE_REFRESH_TOKEN_KEY: str = 'fs_refresh_token'  # cookie 中存放 refresh_token 的名字
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    # ============== IP Location ==============
    IP_LOCATION_PARSE: Literal['online', 'offline', 'false'] = 'offline'
    IP_LOCATION_REDIS_PREFIX: str = 'fs:ip:location'
    IP_LOCATION_EXPIRE_SECONDS: int = 86400

    # ============== 日志 Log ==============
    LOG_ROOT_LEVEL: str = 'NOTSET'
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_FILE_FORMAT: str = LOG_STD_FORMAT
    LOG_CID_DEFAULT_VALUE: str = '-'  # 默认的 CID 值
    LOG_CID_UUID_LENGTH: int = 32
    LOG_STDOUT_LEVEL: str = 'INFO'
    LOG_STDERR_LEVEL: str = 'ERROR'
    LOG_STDOUT_FILENAME: str = f'fs_access_{ENVIRONMENT}.log'
    LOG_STDERR_FILENAME: str = f'fs_error_{ENVIRONMENT}.log'

    # ============== 操作日志 ==============
    OPERATION_LOG_ENCRYPT_TYPE: int = 1  # 0: AES (性能损耗); 1: md5; 2: ItsDangerous; 3: 不加密, others: 替换为 ******
    OPERATION_LOG_ENCRYPT_SECRET_KEY: SecretStr = SecretStr(
        urandom(32).hex()
    )  # 密钥 urandom(32), 需使用 bytes.hex() 方法转换为 str
    OPERATION_LOG_PATH_EXCLUDE: list[str] = [
        '/favicon.ico',
        FASTAPI_API_ROUTE_PREFIX,
        FASTAPI_DOCS_URL,
        FASTAPI_OPENAPI_URL,
    ]
    OPERATION_LOG_ENCRYPT_KEY_INCLUDE: list[str] = [
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]  # 需要脱敏处理的字段


@lru_cache
def get_settings() -> Settings:
    return Settings()


# 创建全局配置实例
settings = get_settings()
