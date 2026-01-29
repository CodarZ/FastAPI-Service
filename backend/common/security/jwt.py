import json

from datetime import timedelta
from typing import Any
from uuid import uuid4

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwt

from backend.app.admin.schema.sys_user import SysUserDetail
from backend.common.dataclasses import AccessToken, NewToken, RefreshToken, TokenPayload
from backend.common.exception import errors
from backend.core.config import settings
from backend.database.postgresql import async_session
from backend.database.redis import redis_client
from backend.utils.timezone import timezone

DependsJWTAuth = Depends(HTTPBearer())


def jwt_encode(payload: dict[str, Any]) -> str:
    """JWT 编码"""
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)


def jwt_decode(token: str) -> TokenPayload:
    """JWT 解码"""
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, [settings.TOKEN_ALGORITHM], {'verify_exp': True})
        user_id = payload.get('user_id')
        session_uuid = payload.get('session_uuid')
        expire_time = payload.get('expire_time')

        if not user_id or not session_uuid or not expire_time:
            raise errors.TokenError(msg='Token 缺失必要信息')

        expire_time = timezone.to_timezone(expire_time)
    except ExpiredSignatureError as e:
        raise errors.TokenError(msg='Token 已过期') from e
    except JWTError as e:
        raise errors.TokenError(msg='Token 无效') from e
    except Exception as e:
        raise errors.ServerError(msg='Token 解析异常') from e

    return TokenPayload(user_id=int(user_id), session_uuid=session_uuid, expire_time=expire_time)


async def jwt_authentication(token: str):
    """JWT 认证"""
    payload = jwt_decode(token)
    user_id = payload.user_id
    cache_token = await redis_client.get(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{payload.session_uuid}')

    if not cache_token:
        raise errors.TokenError(msg='Token 已过期')
    if cache_token != token:
        raise errors.TokenError(msg='Token 已失效')

    return await get_jwt_user(user_id)


async def create_access_token(user_id: int, multi_login: bool, **kwargs) -> AccessToken:
    """创建 Access Token"""

    expire_time = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)

    session_uuid = str(uuid4())

    access_token = jwt_encode({
        'user_id': str(user_id),
        'session_uuid': session_uuid,
        'expire_time': expire_time.timestamp(),
    })

    if not multi_login:
        await redis_client.delete_prefix(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}')

    await redis_client.setex(
        f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}',
        settings.TOKEN_EXPIRE_SECONDS,
        access_token,
    )

    # 附带信息
    if kwargs:
        await redis_client.setex(
            f'{settings.TOKEN_EXTRA_INFO_REDIS_PREFIX}:{user_id}:{session_uuid}',
            settings.TOKEN_EXPIRE_SECONDS,
            json.dumps(kwargs, ensure_ascii=False),
        )

    return AccessToken(access_token, expire_time, session_uuid)


async def create_refresh_token(session_uuid: str, user_id: int, *, multi_login: bool) -> RefreshToken:
    """创建 Refresh Token"""

    expire_time = timezone.now() + timedelta(seconds=settings.TOKEN_REFRESH_EXPIRE_SECONDS)

    refresh_token = jwt_encode({
        'user_id': str(user_id),
        'session_uuid': session_uuid,
        'expire_time': expire_time.timestamp(),
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
    refresh_token: str,
    session_uuid: str,
    user_id: int,
    *,
    multi_login: bool,
    **kwargs,
):
    """创建新 Access Token 和 Refresh Token"""

    redis_refresh_token = await redis_client.get(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}:{session_uuid}')

    if not redis_refresh_token or redis_refresh_token != refresh_token:
        raise errors.TokenError(msg='Refresh Token 无效, 请重新登录')

    await redis_client.delete(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user_id}:{session_uuid}')
    await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}')

    new_token = await create_access_token(user_id, multi_login, **kwargs)
    new_refresh_token = await create_refresh_token(new_token.session_uuid, user_id, multi_login=multi_login)

    return NewToken(
        access_token=new_token.access_token,
        access_expire_time=new_token.expire_time,
        refresh_token=new_refresh_token.refresh_token,
        refresh_expire_time=new_refresh_token.expire_time,
        session_uuid=new_token.session_uuid,
    )


async def revoke_token(user_id: int, session_uuid: str) -> None:
    """撤销 token"""
    await redis_client.delete(f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}')
    await redis_client.delete(f'{settings.TOKEN_EXTRA_INFO_REDIS_PREFIX}:{user_id}:{session_uuid}')


def get_token(request: Request) -> str:
    """获取请求头中的 token"""

    authorization = request.headers.get('Authorization')
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != 'bearer':
        raise errors.TokenError(msg='Token 无效')
    return token


async def get_jwt_user(user_id: int) -> SysUserDetail:
    """获取 JWT 用户信息"""

    cache_user = await redis_client.get(f'{settings.JWT_USER_REDIS_PREFIX}:{user_id}')

    if cache_user:
        user = SysUserDetail.model_validate_json(cache_user)

    else:
        from backend.app.admin.service.sys_user import SysUserService

        async with async_session() as db:
            user = await SysUserService.get_current_user(db=db, user_id=user_id)

            await redis_client.setex(
                f'{settings.JWT_USER_REDIS_PREFIX}:{user_id}',
                settings.TOKEN_EXPIRE_SECONDS,
                user.model_dump_json(),
            )
    return user


def verify_superuser(request: Request, _token: str = DependsJWTAuth) -> bool:
    """验证当前用户超级管理员权限"""

    superuser = request.user.is_superuser
    if not superuser or not request.user.is_admin:
        raise errors.AuthorizationError
    return superuser


# 超级管理员鉴权依赖注入
DependsSuperUser = Depends(verify_superuser)
