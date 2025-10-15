#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from backend.app.admin.api.v1.log.login import router as login_router
from backend.app.admin.api.v1.log.operation import router as operation_router

router = APIRouter(prefix='/log')

router.include_router(operation_router, prefix='/operation', tags=['请求操作日志'])
router.include_router(login_router, prefix='/login', tags=['登录日志'])
