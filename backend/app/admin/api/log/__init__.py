from fastapi import APIRouter

from backend.app.admin.api.log.sys_login_log import router as login_log_router
from backend.app.admin.api.log.sys_operation_log import router as operation_log_router

router = APIRouter(prefix='/log')

router.include_router(login_log_router, prefix='/login', tags=['登录日志'])
router.include_router(operation_log_router, prefix='/operation', tags=['操作日志'])
