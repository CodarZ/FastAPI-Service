from typing import TYPE_CHECKING

from fastapi import Response
from fastapi.security import HTTPBasicCredentials
from starlette.background import BackgroundTask, BackgroundTasks

from backend.app.admin.crud import sys_user_crud
from backend.app.admin.model.sys_user import SysUser
from backend.app.admin.schema.auth import LoginRequest, LoginResponse
from backend.app.admin.schema.sys_login_log import SysLoginLogCreate
from backend.app.admin.schema.sys_user import SysUserDetail
from backend.app.admin.service.sys_login_log import sys_login_log_service
from backend.common.exception import errors
from backend.common.security.jwt import create_access_token, create_refresh_token
from backend.common.security.password import verify_password
from backend.core.config import settings
from backend.utils.timezone import timezone
from backend.common.request.context import ctx

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
            raise errors.NotFoundError(msg='用户不存在')

        # 检查用户是否设置了密码
        if not user.password:
            raise errors.AuthorizationError(msg='用户未设置密码')

        # 验证密码
        if not verify_password(password, user.password):
            raise errors.AuthorizationError(msg='密码错误')

        # 检查用户状态
        if not user.status:
            raise errors.ForbiddenError(msg='用户已被禁用，请联系系统管理员')

        # 检查用户部门状态
        if user.dept_id and user.dept and not user.dept.status:
            raise errors.ForbiddenError(msg='用户所属部门已被禁用，请联系系统管理员')
        # 检查用户角色状态（如果用户有角色，至少要有一个启用的角色）
        if user.roles:
            active_roles = [role for role in user.roles if role.status]
            if not active_roles:
                raise errors.ForbiddenError(msg='用户未分配有效角色，请联系系统管理员')

        return user

    async def login(
        self,
        *,
        db: 'AsyncSession',
        params: LoginRequest,
        response: Response,
        background_tasks: BackgroundTasks,
    ) -> LoginResponse:
        """用户登录"""

        sys_user = None
        try:
            sys_user = await self.verify_user(db, params.username, params.password)

            await sys_user_crud.update_login_time(db, sys_user.id)
            await db.refresh(sys_user)

            access_token_obj = await create_access_token(
                sys_user.id,
                multi_login=sys_user.is_multi_login,
                # extra info
                username=sys_user.username,
                nickname=sys_user.nickname,
                last_login_time=timezone.to_str(sys_user.last_login_time or timezone.now()),
                ip=ctx.ip,
                user_agent=ctx.user_agent,
                os=ctx.os,
                browser=ctx.browser,
                device=ctx.device,
            )
            refresh_token_obj = await create_refresh_token(
                access_token_obj.session_uuid,
                sys_user.id,
                multi_login=sys_user.is_multi_login,
            )

            response.set_cookie(
                key=settings.COOKIE_REFRESH_TOKEN_KEY,
                value=refresh_token_obj.refresh_token,
                max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                expires=timezone.to_utc(refresh_token_obj.expire_time),
                httponly=True,
            )

        except (errors.AuthorizationError, errors.ForbiddenError, errors.CustomError) as e:
            task = BackgroundTask(
                sys_login_log_service.create,
                params=SysLoginLogCreate(
                    username=params.username,
                    user_id=None,
                    status=0,
                    login_time=timezone.now(),
                    msg=e.msg,
                    country=ctx.country,
                    region=ctx.region,
                    city=ctx.city,
                    ip=ctx.ip,
                    user_agent=ctx.user_agent,
                    os=ctx.os,
                    browser=ctx.browser,
                    device=ctx.device,
                ),
            )
            if isinstance(e, errors.ForbiddenError):
                raise errors.ForbiddenError(msg=e.msg, background=task) from e
            raise errors.AuthorizationError(msg=e.msg, background=task) from e
        except Exception as e:
            raise e
        else:
            background_tasks.add_task(
                sys_login_log_service.create,
                params=SysLoginLogCreate(
                    username=params.username,
                    user_id=sys_user.id,
                    status=1,
                    login_time=timezone.now(),
                    msg='登录成功',
                    country=ctx.country,
                    region=ctx.region,
                    city=ctx.city,
                    ip=ctx.ip,
                    os=ctx.os,
                    browser=ctx.browser,
                    device=ctx.device,
                ),
            )

            return LoginResponse(
                access_token=access_token_obj.access_token,
                expire_time=access_token_obj.expire_time,
                session_uuid=access_token_obj.session_uuid,
                user=SysUserDetail.model_validate(sys_user),
            )

    async def login_swagger(
        self,
        *,
        db: 'AsyncSession',
        params: HTTPBasicCredentials,
    ) -> tuple[str, SysUserDetail]:
        """Swagger 文档登录"""

        sys_user = await self.verify_user(db, params.username, params.password)
        await sys_user_crud.update_login_time(db, sys_user.id)
        access_token_data = await create_access_token(sys_user.id, multi_login=sys_user.is_multi_login, swagger=True)
        return access_token_data.access_token, SysUserDetail.model_validate(sys_user)


auth_service = AuthService()
