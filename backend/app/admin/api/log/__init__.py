from fastapi import APIRouter

from backend.app.admin.api.log.sys_operation_log import router as operation_log_router

router = APIRouter(prefix='/log')

router.include_router(operation_log_router, prefix='/operation', tags=['操作日志'])
