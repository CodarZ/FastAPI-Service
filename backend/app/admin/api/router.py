#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from backend.app.admin.api.v1.auth import router as auth_router

admin_router = APIRouter()


admin_router.include_router(auth_router)
