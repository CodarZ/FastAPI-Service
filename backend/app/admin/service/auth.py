from typing import TYPE_CHECKING

from fastapi.security import HTTPBasicCredentials

from backend.app.admin.crud import sys_user_crud
from backend.app.admin.model.sys_user import SysUser
from backend.app.admin.schema.auth import LoginRequest, LoginResponse
from backend.common.exception import errors
from backend.common.security.jwt import create_access_token
from backend.common.security.password import verify_password
from backend.app.admin.schema.sys_user import SysUserDetail

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    """授权服务类"""

    @staticmethod
    async def verify_user(db: AsyncSession, username: str, password: str) -> SysUser:
        """验证用户名和密码"""

        # 根据用户名查询用户
        user = await sys_user_crud.get_by_column(db, 'username', username)
        if not user:
            raise errors.AuthorizationError(msg='用户名或密码错误')

        # 检查用户是否设置了密码
        if not user.password:
            raise errors.AuthorizationError(msg='用户未设置密码')

        # 验证密码
        if not verify_password(password, user.password):
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

        return user

    async def login(
        self,
        *,
        db: 'AsyncSession',
        params: LoginRequest,
        multi_login: bool = True,
    ) -> LoginResponse:
        """用户登录"""

        user = await self.verify_user(db, params.username, params.password)

        # 创建 access token
        access_token_obj = await create_access_token(user.id, multi_login)

        # 构建登录响应
        return LoginResponse(
            access_token=access_token_obj.access_token,
            expire_time=access_token_obj.expire_time,
            session_uuid=access_token_obj.session_uuid,
            user=SysUserDetail.model_validate(user),
        )

    async def login_swagger(self, *, db: AsyncSession, params: HTTPBasicCredentials) -> tuple[str, SysUserDetail]:
        """Swagger 文档登录"""
        user = await self.verify_user(db, params.username, params.password)
        access_token_obj = await create_access_token(user.id, multi_login=user.is_multi_login, swagger=True)
        return (access_token_obj.access_token, SysUserDetail.model_validate(user))


auth_service = AuthService()
