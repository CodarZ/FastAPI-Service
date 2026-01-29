from typing import TYPE_CHECKING

from backend.app.admin.crud import sys_user_crud
from backend.app.admin.schema.auth import LoginRequest, LoginResponse, SwaggerLoginRequest
from backend.common.exception import errors
from backend.common.security.jwt import create_access_token
from backend.common.security.password import verify_password
from backend.app.admin.schema.sys_user import SysUserDetail

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    """授权服务类"""

    @staticmethod
    async def login(
        *,
        db: 'AsyncSession',
        params: LoginRequest | SwaggerLoginRequest,
        multi_login: bool = True,
    ) -> LoginResponse:
        """用户登录"""

        # 根据用户名查询用户
        user = await sys_user_crud.get_by_column(db, 'username', params.username)
        if not user:
            raise errors.AuthorizationError(msg='用户名或密码错误')

        # 检查用户是否设置了密码
        if not user.password:
            raise errors.AuthorizationError(msg='用户未设置密码')

        # 验证密码
        if not verify_password(params.password, user.password):
            raise errors.AuthorizationError(msg='用户名或密码错误')

        # 检查用户状态
        if not user.status:
            raise errors.AuthorizationError(msg='用户已被禁用，请联系系统管理员')

        # 检查用户部门状态
        if user.dept_id and user.dept and not user.dept.status:
            raise errors.AuthorizationError(msg='用户所属部门已被禁用，请联系系统管理员')

        # 检查用户角色状态（如果用户有角色，至少要有一个启用的角色）
        if user.roles:
            active_roles = [role for role in user.roles if role.status]
            if not active_roles:
                raise errors.AuthorizationError(msg='用户未分配有效角色，请联系系统管理员')

        # 创建 access token
        access_token_obj = await create_access_token(user.id, multi_login)

        # 构建用户信息
        user_detail = SysUserDetail.model_validate(user)

        # 构建登录响应
        return LoginResponse(
            access_token=access_token_obj.access_token,
            expire_time=access_token_obj.expire_time,
            session_uuid=access_token_obj.session_uuid,
            user=user_detail,
        )


auth_service = AuthService()
