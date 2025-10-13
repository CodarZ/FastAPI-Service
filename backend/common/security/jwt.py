#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pydantic_core import from_json
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.schema.user import UserDetail
from backend.common.dataclasses import AccessToken, NewToken, RefreshToken, TokenPayload
from backend.common.exception import errors
from backend.common.exception.errors import TokenError
from backend.common.response.code import StandardResponseCode
from backend.core.config import settings
from backend.database.postgresql import async_db_session
from backend.database.redis import redis_client
from backend.utils.serializers import select_as_dict
from backend.utils.timezone import timezone

password_hash = PasswordHash((BcryptHasher(),))


class FastAPIHTTPBearer(HTTPBearer):
    """自定义 HTTPBearer 认证"""

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == StandardResponseCode.HTTP_403:
                raise TokenError()
            raise e


# JWT Depends
DependsJWTAuth = Depends(FastAPIHTTPBearer())


def get_hash_password(password: str, salt: bytes | None):
    """获取加密盐 加密后密码"""
    return password_hash.hash(password, salt=salt)


def verify_password(password: str, hash: str) -> bool:
    """密码验证"""
    return password_hash.verify(password, hash)


def jwt_encode(payload: dict[str, Any]):
    """生成 JWT Token"""
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)


def jwt_decode(token: str) -> TokenPayload:
    """解析 Token"""
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM, {'verify_exp': True})

        user_id = payload.get('user_id')
        session_uuid = payload.get('session_uuid')
        expire = payload.get('expire')

        if not session_uuid or not user_id or not expire:
            raise errors.TokenError(msg='Token 无效')

        # 将 ISO 格式字符串转换为 datetime 对象
        expire_datetime = datetime.fromisoformat(expire) if isinstance(expire, str) else expire
        expire_time = timezone.from_datetime(timezone.to_utc(expire_datetime))

    except ExpiredSignatureError:
        raise errors.TokenError(msg='Token 已过期')
    except JWTError:
        raise errors.TokenError(msg='Token 无效')
    except Exception:
        raise errors.ServerError(msg='Token 解析异常')
    return TokenPayload(int(user_id), session_uuid, expire_time)


async def create_access_token(user_id: int, multi_login: bool, **kwargs) -> AccessToken:
    """生成 Access Token"""

    expire_time = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)

    session_uuid = str(uuid4())
    access_token = jwt_encode({
        'user_id': user_id,
        'session_uuid': session_uuid,
        'expire': expire_time.isoformat(),
    })

    if not multi_login:
        await redis_client.delete_prefix(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}')
        await redis_client.delete_prefix(f'{settings.TOKEN_EXTRA_INFO_REDIS_PREFIX}:{user_id}')

    await redis_client.setex(
        f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}',
        settings.TOKEN_EXPIRE_SECONDS,
        access_token,
    )

    # Token 附加信息单独存储
    if kwargs:
        await redis_client.setex(
            f'{settings.TOKEN_EXTRA_INFO_REDIS_PREFIX}:{user_id}:{session_uuid}',
            settings.TOKEN_EXPIRE_SECONDS,
            json.dumps(kwargs, ensure_ascii=False),
        )

    return AccessToken(access_token, expire_time, session_uuid)


async def create_refresh_token(session_uuid: str, user_id: int, multi_login: bool):
    """生成 Refresh Token"""

    expire_time = timezone.now() + timedelta(seconds=settings.TOKEN_REFRESH_EXPIRE_SECONDS)

    refresh_token = jwt_encode({
        'user_id': user_id,
        'session_uuid': session_uuid,
        'expire': expire_time.isoformat(),
    })

    if not multi_login:
        await redis_client.delete_prefix(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}')

    await redis_client.setex(
        f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}:{session_uuid}',
        settings.TOKEN_REFRESH_EXPIRE_SECONDS,
        refresh_token,
    )

    return RefreshToken(refresh_token, expire_time)


async def create_new_token(
    refresh_token: str, session_uuid: str, user_id: int, multi_login: bool, **kwargs
) -> NewToken:
    """生成 New Token 包含 access token 和 refresh token"""
    redis_refresh_token = await redis_client.get(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}:{session_uuid}')
    if not redis_refresh_token or redis_refresh_token != refresh_token:
        raise errors.TokenError(msg='Refresh Token 已过期，请重新登录! ')

    await redis_client.delete(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}:{session_uuid}')
    await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}')

    n_access_token = await create_access_token(user_id, multi_login, **kwargs)
    n_refresh_token = await create_refresh_token(n_access_token.session_uuid, user_id, multi_login)

    return NewToken(
        access_token=n_access_token.access_token,
        access_expire_time=n_access_token.expire_time,
        refresh_token=n_refresh_token.refresh_token,
        refresh_expire_time=n_refresh_token.expire_time,
        session_uuid=n_access_token.session_uuid,
    )


async def revoke_token(user_id: int, session_uuid: str) -> None:
    """撤销 token 授权"""
    await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}')
    await redis_client.delete(f'{settings.TOKEN_EXTRA_INFO_REDIS_PREFIX}:{user_id}:{session_uuid}')


def get_token(request: Request) -> str:
    """获取请求头中的 token"""
    authorization = request.headers.get('Authorization')
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != 'bearer':
        raise errors.TokenError(msg='Token 无效')
    return token


async def get_current_user(db: AsyncSession, pk: int):
    """
    获取当前用户

    :param db: 数据库会话
    :param pk: 用户 ID
    :return:
    """
    from backend.app.admin.crud.user import user_crud

    user = await user_crud.get(db, pk)
    if not user:
        raise errors.TokenError(msg='Token 无效')
    if not user.status:
        raise errors.AuthorizationError(msg='用户已被锁定，请联系系统管理员')
    return user


async def jwt_authentication(token: str) -> UserDetail:
    """JWT 认证"""
    token_payload = jwt_decode(token)
    user_id = token_payload.user_id
    redis_token = await redis_client.get(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{token_payload.session_uuid}')
    if not redis_token:
        raise errors.TokenError(msg='Token 已过期')
    if token != redis_token:
        raise errors.TokenError(msg='Token 无效')

    cache_user = await redis_client.get(f'{settings.JWT_USER_REDIS_PREFIX}:{user_id}')

    if not cache_user:
        async with async_db_session() as db:
            current_user = await get_current_user(db, user_id)
            user = UserDetail(**select_as_dict(current_user))
            await redis_client.setex(
                f'{settings.JWT_USER_REDIS_PREFIX}:{user_id}',
                settings.TOKEN_EXPIRE_SECONDS,
                user.model_dump_json(),
            )
    else:
        user = UserDetail.model_validate(from_json(cache_user, allow_partial=True))

    return user
