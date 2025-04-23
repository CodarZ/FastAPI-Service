#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from fastapi import Depends, Request

from backend.common.enum.custom import MethodEnum, StatusEnum
from backend.common.exception.errors import PermissionDeniedError, TokenError
from backend.common.logger import log
from backend.common.security.jwt import DependsJWTAuth
from backend.core.config import settings


async def rbac_dependency(request: Request, _token: str = DependsJWTAuth) -> None:
    """RBAC 权限校验"""

    # API 鉴权白名单
    path = request.url.path
    if path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
        return

    # JWT 授权状态
    log.log('JWT 授权状态:', request.auth.scopes)
    if not request.auth.scopes:
        raise TokenError

    # 超级管理员
    if request.user.is_admin:
        return

    # 检测用户角色
    user_roles = request.user.roles
    if not user_roles or all(status == 0 for status in user_roles):
        raise PermissionDeniedError(msg='用户未分配角色，请联系系统管理员')

    # 检测后台管理操作权限
    method = request.method
    if method != MethodEnum.GET or method != MethodEnum.OPTIONS:
        if not request.user.is_staff:
            raise PermissionDeniedError(msg='用户已被禁止后台管理操作，请联系系统管理员')

    # RBAC 鉴权
    if settings.RBAC_ROLE_MENU_MODE:
        path_auth_perm = getattr(request.state, 'permission', None)

        # 没有菜单操作权限标识不校验
        if not path_auth_perm:
            return
        # 菜单鉴权白名单
        if path_auth_perm in settings.RBAC_ROLE_MENU_EXCLUDE:
            return

        # 已分配菜单权限校验
        allow_perms = []
        for role in user_roles:
            for menu in role.menus:
                if menu.perms and menu.status == StatusEnum.YES:
                    allow_perms.extend(menu.perms.split(','))
        if path_auth_perm not in allow_perms:
            raise PermissionDeniedError


# RBAC 授权依赖注入
DependsRBAC = Depends(dependency=rbac_dependency)
