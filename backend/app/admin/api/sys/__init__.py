from fastapi import APIRouter

from backend.app.admin.api.sys.dept import router as dept_router
from backend.app.admin.api.sys.menu import router as menu_router
from backend.app.admin.api.sys.role import router as role_router
from backend.app.admin.api.sys.user import router as user_router

router = APIRouter(prefix='/sys')

router.include_router(user_router, prefix='/user', tags=['系统用户'])
router.include_router(dept_router, prefix='/dept', tags=['系统部门'])
router.include_router(role_router, prefix='/role', tags=['系统角色'])
router.include_router(menu_router, prefix='/menu', tags=['系统菜单'])
