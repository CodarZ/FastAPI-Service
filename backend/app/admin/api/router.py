from fastapi import APIRouter
from backend.app.admin.api.sys import router as sys_router

router = APIRouter()

router.include_router(sys_router)
