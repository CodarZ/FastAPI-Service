from fastapi import APIRouter

from backend.app.admin.api.sys.user import router as user_router

router = APIRouter(prefix='/sys')

router.include_router(user_router, prefix='/user', tags=['系统用户'])
