import os

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from backend.core.path import ENV_DIR
from backend.utils.project import get_project_version

__all__ = ['settings']


class Settings(BaseSettings):
    ENVIRONMENT: Literal['development', 'test', 'production'] = 'development'

    # 动态加载 ENV_DIR 的 `.env` 文件，支持 .local 文件覆盖
    model_config = SettingsConfigDict(
        env_file=[
            Path(ENV_DIR) / '.env',
            Path(ENV_DIR) / f'.env.{os.getenv("ENVIRONMENT", "development")}',
            Path(ENV_DIR) / f'.env.{os.getenv("ENVIRONMENT", "development")}.local',
        ],
        env_file_encoding='utf-8',
    )

    # ==============  FastAPI 配置  ==============
    FASTAPI_API_ROUTE_PREFIX: str = ''
    FASTAPI_VERSION: str = get_project_version()
    FASTAPI_TITLE: str = 'FastAPI Services'
    FASTAPI_DESCRIPTION: str = '基于 FastAPI 搭建的后端服务'
    FASTAPI_DOCS_URL: str | None = f'{FASTAPI_API_ROUTE_PREFIX}/docs'
    FASTAPI_OPENAPI_URL: str | None = f'{FASTAPI_API_ROUTE_PREFIX}/openapi'
    FASTAPI_STATIC_FILES: bool = False  # 是否启动静态文件

    # ============== 文件上传 ==============
    UPLOAD_READ_SIZE: int = 1024
    UPLOAD_IMAGE_EXT_INCLUDE: list[str] = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    UPLOAD_IMAGE_SIZE_MAX: int = 10 * 1024 * 1024  # 10 MB
    UPLOAD_VIDEO_EXT_INCLUDE: list[str] = ['mp4', 'mov', 'avi', 'flv']
    UPLOAD_VIDEO_SIZE_MAX: int = 100 * 1024 * 1024  # 100 MB

    # ============== DateTime ==============
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # ============== 数据库 PostgreSQL ==============
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_DATABASE: str

    DB_ECHO: bool = False  # 连接到数据库时是否打印SQL语句
    DB_CHARSET: str = 'utf8mb4'

    @property
    def PostgreSQL_DATABASE_URL(self):
        """构建 PostgreSQL 数据库连接 URL"""
        return URL.create(
            drivername='postgresql+asyncpg',
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=self.DB_DATABASE if self.ENVIRONMENT == 'production' else f'{self.DB_DATABASE}_test',
        )

    # ============== Redis ==============
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: SecretStr
    REDIS_DATABASE: int
    REDIS_TIMEOUT: int = 5
    REDIS_REQUEST_LIMITER_PREFIX: str = 'fs:limiter'  # Redis 限流器前缀

    # ============== Trace ID ==============
    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'  # 请求头中 Trace ID 的 Key
    TRACE_ID_LOG_DEFAULT_VALUE: str = '-'

    # ============== Middleware ==============
    MIDDLEWARE_CORS: bool = True  # 是否启用 跨域中间件

    # ============== CORS ==============
    CORS_ALLOWED_ORIGINS: list[str] = []  # 允许跨域的源, 末尾不要带 '/'
    CORS_EXPOSE_HEADERS: list[str] = [
        TRACE_ID_REQUEST_HEADER_KEY,
    ]  # 允许跨域的响应头

    # ============== JWT ================
    JWT_USER_REDIS_PREFIX: str = 'fs:user'
    JWT_USER_EXPIRE_SECONDS: int = 604800  # 过期时间 7 天，单位：秒

    # ============== Token ==============
    TOKEN_SECRET_KEY: str  # 密钥 os.urandom(32), 需使用 bytes.hex() 方法转换为 str

    TOKEN_ALGORITHM: str = 'HS256'
    TOKEN_EXPIRE_SECONDS: int = 604800
    TOKEN_REDIS_PREFIX: str = 'fs:token'  # token 存储在 Redis 的前缀
    TOKEN_ONLINE_REDIS_PREFIX: str = 'fs:token_online'  # 在线用户存储在 Redis 的前缀
    TOKEN_EXTRA_INFO_REDIS_PREFIX: str = 'fs:token_extra_info'  # token 存储在 Redis 附带的额外信息
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 691200  # refresh_token 过期时间 8 天，单位：秒
    TOKEN_REFRESH_REDIS_PREFIX: str = 'fs:refresh_token'  # refresh_token 存储在 Redis 的前缀
    TOKEN_REQUEST_PATH_EXCLUDE: list[str] = [
        f'{FASTAPI_API_ROUTE_PREFIX}/auth/login',
    ]  # JWT / RBAC 路由白名单

    # ============== Cookies ==============
    COOKIE_REFRESH_TOKEN_KEY: str = 'fs_refresh_token'  # cookie 中存放 refresh_token 的名字
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    # ============== 用户账户 ==============
    USER_LOCK_REDIS_PREFIX: str = 'fs:user:lock'
    USER_LOCK_THRESHOLD: int = 5  # 用户密码错误锁定阈值，0 表示禁用锁定
    USER_LOCK_SECONDS: int = 60 * 5  # 5 分钟

    # ============== 登录 ==============
    LOGIN_CAPTCHA_REDIS_PREFIX: str = 'fs:login:captcha'
    LOGIN_CAPTCHA_EXPIRE_SECONDS: int = 300  # 5 分钟

    # ============== IP Location ==============
    IP_LOCATION_REDIS_PREFIX: str = 'fs:ip:location'  # 存储在 Redis 的前缀
    IP_LOCATION_EXPIRE_SECONDS: int = 86400

    # ============== 日志 Log ==============
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )

    LOG_CONSOLE_LEVEL: str = 'INFO'  # 控制台输出

    LOG_ACCESS_LEVEL: str = 'INFO'
    LOG_ERROR_LEVEL: str = 'ERROR'
    LOG_ACCESS_FILENAME: str = 'fs_access.log' if ENVIRONMENT == 'production' else f'fs_access_{ENVIRONMENT}.log'
    LOG_ERROR_FILENAME: str = 'fs_error.log' if ENVIRONMENT == 'production' else f'fs_error_{ENVIRONMENT}.log'

    # ============== 操作日志 ==============
    OPERATION_LOG_ENCRYPT_SECRET_KEY: str  # 密钥 os.urandom(32), 需使用 bytes.hex() 方法转换为 str

    OPERATION_LOG_PATH_EXCLUDE: list[str] = [
        '/favicon.ico',
        FASTAPI_DOCS_URL,
        FASTAPI_OPENAPI_URL,
        FASTAPI_API_ROUTE_PREFIX,
    ]  # 请求路径不记录日志
    OPERATION_LOG_ENCRYPT_KEY_INCLUDE: list[str] = [
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]  # 默认需要脱敏处理的字段

    OPERATION_LOG_QUEUE_BATCH_CONSUME_SIZE: int = 100
    OPERATION_LOG_QUEUE_TIMEOUT: int = 60

    @model_validator(mode='before')
    @classmethod
    def validator_api_url(cls, values):
        """生产环境
        1. 不启动 api 文档
        2. 不开启静态文件服务
        """
        if values.get('ENVIRONMENT') == 'production':
            values['FASTAPI_OPENAPI_URL'] = None
            values['FASTAPI_STATIC_FILES'] = False
        return values


@lru_cache
def get_settings():
    return Settings()  # type: ignore


settings = get_settings()
