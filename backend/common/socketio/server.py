#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socketio

from backend.common.logger import log
from backend.common.security.jwt import jwt_authentication
from backend.core.config import settings
from backend.database.redis import redis_client

# 创建 Socket.IO 服务器实例
sio = socketio.AsyncServer(
    client_manager=socketio.AsyncRedisManager(
        f'redis://:{settings.REDIS_PASSWORD.get_secret_value()}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/3'
    ),
    async_mode='asgi',
    cors_allowed_origins=settings.CORS_ALLOWED_ORIGINS,
    cors_credentials=True,
    namespaces=['/ws'],
)


@sio.event
async def connect(sid, environ, auth):
    """处理 WebSocket 连接事件"""
    log.info(f'WebSocket 连接, session_uuid: {auth.get("session_uuid")}, token: {auth.get("token")}')

    if not auth:
        log.error('WebSocket 连接失败，缺少身份验证信息')
        return False

    session_uuid = auth.get('session_uuid')
    token = auth.get('token')

    if not token and not session_uuid:
        log.error('WebSocket 连接失败，缺少 token 和 session_uuid')
        return False

    # 免证连接
    if token == 'internal':
        redis_client.sadd(settings.TOKEN_ONLINE_REDIS_PREFIX, session_uuid)
        return True

    try:
        await jwt_authentication(token)
    except Exception as e:
        log.info(f'WebSocket 连接失败，身份验证失败: {str(e)}')

    redis_client.sadd(settings.TOKEN_ONLINE_REDIS_PREFIX, session_uuid)
    return True


@sio.event
async def disconnect(sid: str):
    """处理 WebSocket 断开连接事件"""
    redis_client.spop(settings.TOKEN_ONLINE_REDIS_PREFIX)
