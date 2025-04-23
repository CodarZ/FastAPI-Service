#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from datetime import timedelta
from typing import Any
from uuid import uuid4

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.schema.user import UserInfoWithRelations
from backend.common.dataclasses import AccessToken, NewToken, RefreshToken, TokenPayload
from backend.common.exception.errors import PermissionDeniedError, TokenError
from backend.core.config import settings
from backend.database.mysql import async_db_session
from backend.database.redis import redis_client
from backend.utils.serializers import select_as_dict
from backend.utils.timezone import timezone

# JWT authorizes dependency injection
DependsJWTAuth = Depends(HTTPBearer())

password_hash = PasswordHash((BcryptHasher(),))


def get_hash_password(password: str, salt: bytes | None):
    """加密 密码（支持 salt 加密盐）"""
    return password_hash.hash(password, salt=salt)


def verify_password(plain: str, hashed: str):
    """校验明文密码与哈希密码是否匹配"""
    return password_hash.verify(plain, hashed)


def jwt_encode(payload: dict[str, Any]) -> str:
    """生成 JWT token

    可附带载荷信息, 服务端可以通过解析获取这些数据, 无需查数据库, 如: user_id 等。
    """
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)


def jwt_decode(token: str):
    """解析 JWT token

    解析 JWT token, 获取载荷信息, 并验证 token 的有效性。
    """

    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)
        print('JWT token decode payload:', payload)

        # session_uuid = payload.get('session_uuid') or 'debug'
        # expire_time = payload.get('expire_time')

        user_id = payload.get('user_id')
        if not user_id:
            raise TokenError(msg='Token 无效')
    except ExpiredSignatureError:
        raise TokenError(msg='Token 已经过期')
    except (JWTError, Exception):
        raise TokenError(msg='Token 解析失败')
    # return TokenPayload(user_id=user_id, session_uuid=session_uuid, expire_time=expire_time)
    return TokenPayload(**payload)


async def create_access_token(user_id: int, multi_login: bool, **kwargs):
    """生成 Access Token"""

    expire_time = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
    session_uuid = str(uuid4())

    access_token = jwt_encode({
        'session_uuid': session_uuid,
        'expire_time': expire_time.isoformat(),
        'user_id': user_id,
    })

    if not multi_login:
        await redis_client.delete_prefix(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}')
        await redis_client.delete_prefix(f'{settings.TOKEN_EXTRA_INFO_REDIS_PREFIX}:{user_id}')

    await redis_client.setex(
        f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}',
        settings.TOKEN_EXPIRE_SECONDS,
        access_token,
    )

    if kwargs:
        # Token 附加的其他信息 单独存储
        await redis_client.setex(
            f'{settings.TOKEN_EXTRA_INFO_REDIS_PREFIX}:{user_id}:{session_uuid}',
            settings.TOKEN_EXPIRE_SECONDS,
            json.dumps(kwargs, ensure_ascii=False),
        )

    return AccessToken(access_token, expire_time, session_uuid)


async def create_refresh_token(user_id: int, multi_login: bool):
    """生成 Refresh Token"""

    expire_time = timezone.now() + timedelta(seconds=settings.TOKEN_REFRESH_EXPIRE_SECONDS)

    refresh_token = jwt_encode({
        'expire_time': expire_time.isoformat(),
        'user_id': user_id,
    })

    if not multi_login:
        await redis_client.delete_prefix(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}')

    await redis_client.setex(
        f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}:{refresh_token}',
        settings.TOKEN_REFRESH_EXPIRE_SECONDS,
        refresh_token,
    )

    return RefreshToken(refresh_token, expire_time)


async def create_new_token(user_id: int, refresh_token: str, multi_login: bool, **kwargs):
    """根据 refresh token 生成新的 access token"""

    redis_refresh_token = await redis_client.get(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}:{refresh_token}')

    if not redis_refresh_token:
        raise TokenError(msg='Refresh Token 已过期, 请重新登录')

    n_token = await create_access_token(user_id, multi_login, **kwargs)

    return NewToken(n_token.access_token, n_token.expire_time, n_token.session_uuid)


async def revoke_token(user_id: str, session_uuid: str):
    """撤销 token"""
    await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}')


def get_token(request: Request) -> str:
    """获取请求头中的 token"""
    authorization = request.headers.get('Authorization')
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != 'bearer':
        raise TokenError(msg='Token 无效')
    return token


async def get_current_user(db: AsyncSession, pk: int):
    """获取当前用户

    需要结合业务逻辑来实现
    """


def is_admin_user(request: Request) -> bool:
    """验证当前用户是否为管理员"""
    superuser = request.user.is_admin
    if not superuser or not request.user.is_staff:
        raise PermissionDeniedError
    return superuser


async def jwt_authentication(token: str):
    """JWT Token 认证

    1. 获取并解析 token
    2. 验证 token 是否过期
    3. 获取用户信息
    """
    token_payload = jwt_decode(token)
    user_id = token_payload.user_id
    session_uuid = token_payload.session_uuid

    redis_token = await redis_client.get(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}')
    if not redis_token:
        raise TokenError(msg='Token 已过期, 请重新登录')

    if token != redis_token:
        raise TokenError(msg='Token 无效, 请重新登录')

    cache_user = await redis_client.get(f'{settings.JWT_USER_REDIS_PREFIX}:{user_id}')

    if not cache_user:
        #  如果没有缓存用户信息, 则从数据库中获取
        async with async_db_session() as db:
            current_user = await get_current_user(db, user_id)
            user = UserInfoWithRelations(**select_as_dict(current_user))

            await redis_client.setex(
                f'{settings.JWT_USER_REDIS_PREFIX}:{user_id}',
                settings.JWT_USER_REDIS_EXPIRE_SECONDS,
                user.model_dump_json(),
            )
    else:
        user = UserInfoWithRelations.model_validate_json(cache_user)
        # https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
        # user = UserInfoWithRelations.model_validate(from_json(cache_user, allow_partial=True))

    return user
