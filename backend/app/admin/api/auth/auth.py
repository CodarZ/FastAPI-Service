from fastapi import APIRouter

from backend.app.admin.schema.auth import LoginRequest, LoginResponse
from backend.app.admin.service.auth import auth_service
from backend.common.response.base import ResponseSchemaModel, response_base
from backend.database.postgresql import CurrentSessionTransaction

router = APIRouter()


@router.post('/login', summary='用户登录', response_model=ResponseSchemaModel[LoginResponse])
async def login(db: CurrentSessionTransaction, params: LoginRequest):
    """用户登录"""
    data = await auth_service.login(db=db, params=params)
    return response_base.success(data=data)
