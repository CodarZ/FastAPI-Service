from fastapi import APIRouter

from backend.app.admin.api.auth import router as auth_router
from backend.app.admin.api.sys import router as sys_router
from backend.app.admin.api.log import router as log_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(sys_router)
router.include_router(log_router)
