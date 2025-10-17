from fastapi import APIRouter

from backend.app.admin.api.router import admin_router

router = APIRouter()

router.include_router(admin_router)
