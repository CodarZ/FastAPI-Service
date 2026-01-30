from backend.common.security.rbac import RBACRouter

from backend.app.admin.api.auth import router as auth_router
from backend.app.admin.api.sys import router as sys_router
from backend.app.admin.api.log import router as log_router
from backend.common.security.jwt import DependsJWTAuth


router = RBACRouter()

router.include_router(auth_router)
router.include_router(sys_router, dependencies=[DependsJWTAuth])
router.include_router(log_router, dependencies=[DependsJWTAuth])
