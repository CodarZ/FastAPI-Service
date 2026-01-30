from fastapi import APIRouter

from backend.app.admin.api.monitor.health import router as health_router

router = APIRouter(prefix='/monitor')

router.include_router(health_router, tags=['监控'])
