import os

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from backend import __version__
from backend.core.path import ENV_DIR

__all__ = ['settings']


def _get_env_file():
    """获取 env 环境变量文件"""

    env_dir = Path(ENV_DIR)
    env = os.getenv('ENVIRONMENT', 'development')

    return [
        env_dir / '.env',
        env_dir / '.env.local',
        env_dir / f'.env.{env}',
        env_dir / f'.env.{env}.local',
    ]


class Settings(BaseSettings):
    """系统变量配置"""

    ENVIRONMENT: Literal['development', 'test', 'production'] = 'development'

    model_config = SettingsConfigDict(case_sensitive=True, env_file_encoding='utf-8', env_file=_get_env_file())

    # ============================  FastAPI 配置  ============================
    FASTAPI_ROUTE_PREFIX: str = ''  # 必须以 '/' 开头，末尾不要带 '/'
    FASTAPI_VERSION: str = __version__
    FASTAPI_TITLE: str = 'FastAPI Services'
    FASTAPI_DESCRIPTION: str = '基于 FastAPI 搭建的后端服务'
    FASTAPI_DOCS_URL: str | None = f'{FASTAPI_ROUTE_PREFIX}/docs'
    FASTAPI_OPENAPI_URL: str | None = f'{FASTAPI_ROUTE_PREFIX}/openapi'

    # ============================ DateTime ============================
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # ============================ 数据库 PostgreSQL ============================
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_DATABASE: str

    DB_ECHO: bool = False  # 是否在日志中输出执行的 SQL 语句
    DB_ECHO_POOL: bool | Literal['debug'] = False  # 是否在日志中输出数据库连接池的调试信息
    DB_CHARSET: str = 'utf8mb4'

    @property
    def PostgreSQL_URL(self):
        """PostgreSQL 数据库连接URL"""

        database = self.DB_DATABASE if self.ENVIRONMENT == 'production' else f'{self.DB_DATABASE}_test'

        return URL.create(
            drivername='postgresql+asyncpg',
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=database,
        )

    # ============================ Redis ============================
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: SecretStr
    REDIS_DATABASE: int = 0
    REDIS_TIMEOUT: int = 5
    REDIS_REQUEST_LIMITER_PREFIX: str = 'fs:limiter'  # Redis 限流器前缀

    # ============================ Middleware ============================
    MIDDLEWARE_CORS: bool = True  # 是否启用 跨域中间件

    # ============================ CORS ============================
    CORS_ALLOWED_ORIGINS: list[str] = []  # 允许跨域的源, 末尾不要带 '/'
    CORS_EXPOSE_HEADERS: list[str] = []  # 允许跨域的响应头

    # ============================ Trace ID ============================
    TRACE_ID_LOG_DEFAULT: str = '-'

    # ============================ 验证码 ============================
    CAPTCHA_REDIS_PREFIX: str = 'fs:captcha'
    CAPTCHA_EXPIRE_SECONDS: int = 300  # 5 分钟

    # ============================ Token ============================
    TOKEN_SECRET_KEY: str  # 密钥, 可使用 os.urandom(32).hex() 生成一个随机的密钥

    TOKEN_ALGORITHM: str = 'HS256'
    TOKEN_EXPIRE_SECONDS: int = 259200  # token 过期时间 3 天，单位：秒
    TOKEN_REDIS_PREFIX: str = 'fs:token'  # token 存储在 Redis 的前缀
    TOKEN_ONLINE_REDIS_PREFIX: str = 'fs:token_online'  # 在线用户存储在 Redis 的前缀
    TOKEN_EXTRA_INFO_REDIS_PREFIX: str = 'fs:token_extra_info'  # token 存储在 Redis 附带的额外信息
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 691200  # refresh_token 过期时间 8 天，单位：秒
    TOKEN_REFRESH_REDIS_PREFIX: str = 'fs:refresh_token'  # refresh_token 存储在 Redis 的前缀

    TOKEN_WHITE_PATH: list[str] = [
        f'{FASTAPI_ROUTE_PREFIX}/auth/login',
    ]  # JWT 白名单
    # TOKEN_WHITE_PATH_PATTERNS: list[str] = []  # JWT 白名单 - 正则表达式匹配

    # ============== JWT ================
    JWT_USER_REDIS_PREFIX: str = 'fs:user'
    JWT_USER_EXPIRE_SECONDS: int = 604800  # 过期时间 7 天，单位：秒

    # ============================ Cookie ============================
    COOKIE_REFRESH_TOKEN_KEY: str = 'fs_refresh_token'  # cookie 中存放 refresh_token 的名字
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    # ============================ RBAC 权限校验 ============================
    RBAC_PERMISSION_REDIS_PREFIX: str = 'fs:rbac:permission'
    RBAC_PERMISSION_EXPIRE_SECONDS: int = 36000  # 权限缓存过期时间 10 小时
    RBAC_WHITE_PATH_PATTERNS: list[str] = [
        r'^/auth/logout$',
        r'^/auth/refresh$',
    ]  # RBAC 鉴权白名单 - 支持正则表达式匹配，这些路径跳过权限校验（仍需 JWT 认证）
    RBAC_WHITE_PERMISSION: list[str] = []  # 权限标识白名单 - 特定权限标识跳过校验（菜单/按钮权限）

    # ============================ 用户账户 ============================
    USER_LOCK_REDIS_PREFIX: str = 'fs:user:lock'
    USER_LOCK_THRESHOLD: int = 5  # 用户密码错误锁定阈值，0 表示禁用锁定
    USER_LOCK_SECONDS: int = 60 * 5  # 5 分钟

    # ============================ 初始超级管理员 ============================
    INIT_SUPERUSER_USERNAME: str = 'superadmin'
    INIT_SUPERUSER_PASSWORD: str = '123456'
    INIT_SUPERUSER_NICKNAME: str = '超级管理员'
    INIT_SUPERUSER_EMAIL: str | None = None
    INIT_SUPERUSER_PHONE: str | None = None

    # ============================ IP 信息 ============================
    IP_REDIS_PREFIX: str = 'fs:ip'  # 存储在 Redis 的前缀
    IP_EXPIRE_SECONDS: int = 86400

    # ============================ 日志 LOG ============================
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | <cyan> {request_id} </> | <lvl>{message}</>'
    )

    LOG_CONSOLE_LEVEL: str = 'INFO'
    LOG_ACCESS_LEVEL: str = 'INFO'
    LOG_ERROR_LEVEL: str = 'ERROR'

    LOG_ACCESS_FILENAME: str = 'fs_access.log'
    LOG_ERROR_FILENAME: str = 'fs_error.log'

    # ============================ 操作日志 ============================
    OPERATION_LOG_SECRET_KEY: str  # 密钥, 可使用 os.urandom(32).hex() 生成一个随机的密钥

    # OPERATION_LOG_WHITE_PATH_PATTERNS: list[str] = []  # 请求路径 - 正则表达式匹配
    OPERATION_LOG_WHITE_PATH: list[str] = [
        '/favicon.ico',
        FASTAPI_DOCS_URL,
        FASTAPI_OPENAPI_URL,
        '/monitor/health',
    ]  # 请求路径不记录日志

    OPERATION_LOG_ENCRYPT_KEY: list[str] = [
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]  # 默认需要脱敏处理的字段

    OPERATION_LOG_QUEUE_MAXSIZE: int = 100000  # 队列的最大长度
    OPERATION_LOG_QUEUE_BATCH_SIZE: int = 100  # 每次批量写入数据库的日志数量
    OPERATION_LOG_QUEUE_TIMEOUT: int = 60  # 队列等待操作的时间，单位：秒

    @model_validator(mode='before')
    @classmethod
    def validator_api_url(cls, values):
        """生产环境禁止访问 API 文档和 OpenAPI JSON"""

        if values.get('ENVIRONMENT') == 'production':
            values['FASTAPI_DOCS_URL'] = None
            values['FASTAPI_OPENAPI_URL'] = None
        return values


@lru_cache
def get_settings():
    return Settings()  # type: ignore


settings = get_settings()
